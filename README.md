# Concordia

[한국어](README_kr.md) · [日本語](README_jp.md)

Shared GitHub Actions workflows for my repositories, so that every project runs CI the same way.
*Concordia* is Latin for "being of one heart": many repositories, one beat.

## Workflows

| Workflow | What it does |
|---|---|
| [`python-tests.yml`](.github/workflows/python-tests.yml) | Checks out the repo, sets up Python (one job per version), runs an install command and a test command |
| [`hygiene.yml`](.github/workflows/hygiene.yml) | Format-only check for public repositories: no local agent/state files tracked, no absolute home-directory paths, internal project-number tokens reported as warnings |

## Use

```yaml
# .github/workflows/tests.yml in the calling repository
name: tests
on:
  push:
    branches: [main]
  pull_request:

jobs:
  tests:
    uses: fairyofdata/Concordia/.github/workflows/python-tests.yml@v1
    with:
      python-versions: '["3.12"]'
      install: python -m pip install -r requirements.txt
      test: python -m pytest -q

  hygiene:
    uses: fairyofdata/Concordia/.github/workflows/hygiene.yml@v1
```

`python-tests.yml` inputs:

| Input | Default | Notes |
|---|---|---|
| `python-versions` | `'["3.12"]'` | JSON array; one job per version |
| `install` | `python -m pip install -r requirements.txt` | any shell command, multi-line allowed |
| `test` | `python -m pytest -q` | any shell command |
| `cache` | `pip` | `''` to turn caching off (needed when there is no requirements or pyproject file) |
| `working-directory` | `.` | |

`hygiene.yml` inputs: `strict` (warnings fail too, default `false`) and `concordia-ref` (where the checker script comes from; keep it equal to the tag in `uses:`).
To skip files on purpose (test fixtures, for example), list globs in `.concordia-allow` at the repository root.

The checker matches fixed formats only. It does not judge what a file is about.

## Versions

Callers pin a major tag (`@v1`). Compatible changes move the tag; breaking changes get a new major tag. Decisions are in [docs/adr](docs/adr/README.md).

## License

[MIT](LICENSE)
