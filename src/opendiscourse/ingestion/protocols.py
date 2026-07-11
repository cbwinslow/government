"""Stable extension contracts for source adapters and artifact stores."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from opendiscourse.domain.models import (
    DiscoveryRequest,
    RawRecord,
    RemoteAsset,
    StoredArtifact,
    VerificationReport,
)


@runtime_checkable
class ArtifactStore(Protocol):
    async def put_stream(
        self,
        chunks: AsyncIterator[bytes],
        *,
        media_type: str,
        source_uri: str,
    ) -> StoredArtifact: ...


@runtime_checkable
class SourceAdapter(Protocol):
    source_id: str

    async def discover(self, request: DiscoveryRequest) -> AsyncIterator[RemoteAsset]: ...

    async def download(self, asset: RemoteAsset, store: ArtifactStore) -> StoredArtifact: ...

    async def extract(
        self,
        asset: RemoteAsset,
        artifact: StoredArtifact,
    ) -> AsyncIterator[RawRecord]: ...

    async def verify(self) -> VerificationReport: ...
