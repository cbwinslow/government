from pathlib import Path

import pytest

from opendiscourse.domain.models import DiscoveryRequest
from opendiscourse.sources.fixture import FixtureSourceAdapter
from opendiscourse.storage.content_addressed import ContentAddressedStorage


@pytest.mark.asyncio
async def test_fixture_source_runs_end_to_end(tmp_path: Path) -> None:
    adapter = FixtureSourceAdapter()
    store = ContentAddressedStorage(tmp_path / "lake")
    natural_keys: list[str] = []

    async for asset in adapter.discover(DiscoveryRequest(all_data=True)):
        artifact = await adapter.download(asset, store)
        async for record in adapter.extract(asset, artifact):
            natural_keys.append(record.natural_key)

    report = await adapter.verify()

    assert natural_keys == ["hr-1", "ada"]
    assert report.is_complete
    assert report.extracted == 2
