# Legacy and Upstream Migration

## Policy

The original repository contains cloned upstream projects, datasets, experiments, and acquisition scripts. They are retained as references until each item is inventoried. They are not part of the new `opendiscourse` package architecture.

## Inventory fields

Each legacy or upstream item should record:

- local path;
- upstream repository or download URL;
- exact revision or dataset date;
- license and redistribution terms;
- purpose and useful components;
- whether it should be referenced, wrapped, rewritten, archived, or removed;
- any data already downloaded and where it is stored;
- risks such as embedded repositories, generated files, secrets, or large Git objects.

## Migration process

1. Freeze and tag the pre-rebuild state.
2. Inventory every cloned repository and dataset.
3. Preserve useful source research and test fixtures.
4. Reimplement or wrap only the required behavior behind OpenDiscourse contracts.
5. Add attribution, fixtures, and tests.
6. Move large data to the configured data lake.
7. Remove obsolete copies only after the inventory and replacement are reviewed.

## Rule

Do not import a legacy repository's internal modules directly from `src/opendiscourse`. Integration must occur through stable adapters or explicit external tooling.
