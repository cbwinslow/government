"""Deterministic fixture adapter used to validate the ingestion contracts."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import PurePosixPath

from opendiscourse.domain.models import (
    DiscoveryRequest,
    RawRecord,
    RemoteAsset,
    StoredArtifact,
    VerificationReport,
)
from opendiscourse.ingestion.protocols import ArtifactStore


class FixtureSourceAdapter:
    source_id = "fixture"

    def __init__(self) -> None:
        self._payloads = {
            "fixture://people/ada": {"id": "ada", "name": "Ada Lovelace", "kind": "person"},
            "fixture://bills/hr-1": {"id": "hr-1", "title": "Fixture Bill", "kind": "bill"},
        }
        self._discovered = 0
        self._stored = 0
        self._extracted = 0
        self._failed = 0

    async def discover(self, request: DiscoveryRequest) -> AsyncIterator[RemoteAsset]:
        del request
        for uri in sorted(self._payloads):
            self._discovered += 1
            identifier = uri.rsplit("/", maxsplit=1)[-1]
            yield RemoteAsset(
                source_id=self.source_id,
                dataset_id="bootstrap",
                source_uri=uri,
                logical_path=PurePosixPath("fixture") / f"{identifier}.json",
                media_type="application/json",
            )

    async def download(self, asset: RemoteAsset, store: ArtifactStore) -> StoredArtifact:
        try:
            payload = self._payloads[asset.source_uri]

            async def chunks() -> AsyncIterator[bytes]:
                yield json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

            artifact = await store.put_stream(
                chunks(), media_type=asset.media_type, source_uri=asset.source_uri
            )
            self._stored += 1
            return artifact
        except BaseException:
            self._failed += 1
            raise

    async def extract(
        self,
        asset: RemoteAsset,
        artifact: StoredArtifact,
    ) -> AsyncIterator[RawRecord]:
        payload = self._payloads[asset.source_uri]
        self._extracted += 1
        yield RawRecord(
            source_id=self.source_id,
            dataset_id=asset.dataset_id,
            natural_key=str(payload["id"]),
            payload=payload,
            artifact_checksum=artifact.checksum,
        )

    async def verify(self) -> VerificationReport:
        return VerificationReport(
            discovered=self._discovered,
            stored=self._stored,
            extracted=self._extracted,
            failed=self._failed,
        )
