import errno
import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest

import opendiscourse.storage.content_addressed as storage_module
from opendiscourse.storage.content_addressed import ContentAddressedStorage


async def byte_stream(value: bytes) -> AsyncIterator[bytes]:
    yield value[:3]
    yield value[3:]


@pytest.mark.asyncio
async def test_content_addressed_storage_is_deterministic_and_deduplicates(tmp_path: Path) -> None:
    store = ContentAddressedStorage(tmp_path / "lake")

    first = await store.put_stream(
        byte_stream(b"government-data"),
        media_type="text/plain",
        source_uri="fixture://one",
    )
    second = await store.put_stream(
        byte_stream(b"government-data"),
        media_type="text/plain",
        source_uri="fixture://two",
    )

    assert first.checksum == second.checksum
    assert first.storage_uri == second.storage_uri
    assert first.size_bytes == len(b"government-data")
    assert store.object_path(first.checksum).read_bytes() == b"government-data"


def test_object_path_rejects_untrusted_values(tmp_path: Path) -> None:
    store = ContentAddressedStorage(tmp_path)

    with pytest.raises(ValueError):
        store.object_path("../../etc/passwd")


@pytest.mark.asyncio
async def test_cross_filesystem_finalize_uses_atomic_destination_copy(
    tmp_path: Path, monkeypatch
) -> None:
    store = ContentAddressedStorage(tmp_path / "lake", tmp_path / "temporary")
    real_replace = os.replace
    calls = 0

    def replace_with_cross_device_failure(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError(errno.EXDEV, "cross-device link")
        real_replace(source, destination)

    monkeypatch.setattr(storage_module.os, "replace", replace_with_cross_device_failure)

    artifact = await store.put_stream(
        byte_stream(b"cross-filesystem-data"),
        media_type="application/octet-stream",
        source_uri="fixture://cross-filesystem",
    )

    assert calls == 2
    assert store.object_path(artifact.checksum).read_bytes() == b"cross-filesystem-data"
    assert list(store.temp_root.glob("*.partial")) == []
    assert list(store.object_path(artifact.checksum).parent.glob("*.partial")) == []
