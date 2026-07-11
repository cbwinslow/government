"""Source-neutral data contracts used by ingestion adapters."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Any


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class DiscoveryRequest:
    dataset_id: str | None = None
    all_data: bool = False
    cursor: str | None = None
    since: datetime | None = None
    until: datetime | None = None


@dataclass(frozen=True, slots=True)
class RemoteAsset:
    source_id: str
    dataset_id: str
    source_uri: str
    logical_path: PurePosixPath
    media_type: str
    modified_at: datetime | None = None
    etag: str | None = None
    expected_size: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class StoredArtifact:
    checksum: str
    storage_uri: str
    size_bytes: int
    media_type: str
    source_uri: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class RawRecord:
    source_id: str
    dataset_id: str
    natural_key: str
    payload: Mapping[str, Any]
    artifact_checksum: str


@dataclass(frozen=True, slots=True)
class VerificationReport:
    discovered: int
    stored: int
    extracted: int
    failed: int
    messages: tuple[str, ...] = ()

    @property
    def is_complete(self) -> bool:
        return self.failed == 0 and self.discovered == self.stored
