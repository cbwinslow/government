"""Local content-addressed artifact storage."""

from __future__ import annotations

import asyncio
import errno
import hashlib
import os
import shutil
import uuid
from collections.abc import AsyncIterator
from pathlib import Path

import aiofiles

from opendiscourse.domain.models import StoredArtifact


class ContentAddressedStorage:
    """Store immutable objects by SHA-256 with atomic finalization."""

    def __init__(self, root: Path, temp_root: Path | None = None) -> None:
        self.root = root.expanduser().resolve()
        self.temp_root = (temp_root or self.root / ".tmp").expanduser().resolve()
        self.objects_root = self.root / "objects" / "sha256"

    async def initialize(self) -> None:
        self.objects_root.mkdir(parents=True, exist_ok=True)
        self.temp_root.mkdir(parents=True, exist_ok=True)

    def object_path(self, checksum: str) -> Path:
        invalid_character = any(character not in "0123456789abcdef" for character in checksum)
        if len(checksum) != 64 or invalid_character:
            raise ValueError("checksum must be a lowercase SHA-256 hexadecimal digest")
        return self.objects_root / checksum[:2] / checksum[2:4] / checksum

    async def _finalize(self, temporary_path: Path, destination: Path) -> None:
        """Finalize an object atomically, including across filesystem boundaries."""

        try:
            os.replace(temporary_path, destination)
            return
        except OSError as error:
            if error.errno != errno.EXDEV:
                raise

        destination_temporary = destination.with_name(
            f".{destination.name}.{uuid.uuid4().hex}.partial"
        )
        try:
            await asyncio.to_thread(shutil.copyfile, temporary_path, destination_temporary)
            os.replace(destination_temporary, destination)
            await asyncio.to_thread(temporary_path.unlink, missing_ok=True)
        finally:
            await asyncio.to_thread(destination_temporary.unlink, missing_ok=True)

    async def put_stream(
        self,
        chunks: AsyncIterator[bytes],
        *,
        media_type: str,
        source_uri: str,
    ) -> StoredArtifact:
        await self.initialize()
        temporary_path = self.temp_root / f"artifact-{uuid.uuid4().hex}.partial"
        digest = hashlib.sha256()
        size_bytes = 0

        try:
            async with aiofiles.open(temporary_path, "xb") as handle:
                async for chunk in chunks:
                    if not isinstance(chunk, bytes):
                        raise TypeError("artifact stream chunks must be bytes")
                    if not chunk:
                        continue
                    digest.update(chunk)
                    size_bytes += len(chunk)
                    await handle.write(chunk)

            checksum = digest.hexdigest()
            destination = self.object_path(checksum)
            destination.parent.mkdir(parents=True, exist_ok=True)

            if destination.exists():
                temporary_path.unlink(missing_ok=True)
            else:
                await self._finalize(temporary_path, destination)

            return StoredArtifact(
                checksum=checksum,
                storage_uri=destination.as_uri(),
                size_bytes=size_bytes,
                media_type=media_type,
                source_uri=source_uri,
            )
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            raise
