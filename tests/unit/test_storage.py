from collections.abc import AsyncIterator
from pathlib import Path

import pytest

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
