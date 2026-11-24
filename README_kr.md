# Concordia

[English](README.md) · [日本語](README_jp.md)

제 저장소들이 같은 방식으로 CI를 돌리도록 모아 둔 GitHub Actions 공용 워크플로입니다.
*Concordia*는 라틴어로 「한마음」입니다. 저장소는 여럿이어도 박자는 하나라는 뜻으로 붙였습니다.

## 워크플로

| 워크플로 | 하는 일 |
|---|---|
| [`python-tests.yml`](.github/workflows/python-tests.yml) | 저장소를 받고, 파이썬을 판마다 따로 준비해 설치 명령과 테스트 명령을 돌립니다 |
| [`hygiene.yml`](.github/workflows/hygiene.yml) | 공개 저장소용 형식 검사: 로컬 에이전트·상태 파일이 추적되지 않는지, 홈 디렉터리 절대 경로가 없는지 봅니다. 내부 프로젝트 번호 꼴은 경고로만 냅니다 |

## 쓰는 법

부르는 저장소의 `.github/workflows/tests.yml`에 이렇게 씁니다.

```yaml
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

`python-tests.yml` 입력:

| 입력 | 기본값 | 비고 |
|---|---|---|
| `python-versions` | `'["3.12"]'` | JSON 배열, 판마다 작업 하나 |
| `install` | `python -m pip install -r requirements.txt` | 아무 셸 명령, 여러 줄 가능 |
| `test` | `python -m pytest -q` | 아무 셸 명령 |
| `cache` | `pip` | requirements·pyproject 파일이 없으면 `''`로 끕니다 |
| `working-directory` | `.` | |

`hygiene.yml` 입력은 `strict`(경고도 실패로, 기본 `false`)와 `concordia-ref`(검사 스크립트를 가져올 판, `uses:`의 태그와 같게)입니다.
일부러 빼야 할 파일(테스트 데이터 등)은 저장소 루트의 `.concordia-allow`에 glob으로 한 줄씩 적습니다.

검사는 정해진 형식만 봅니다. 파일 내용이 무엇에 관한 것인지는 판단하지 않습니다.

## 판

부르는 쪽은 큰 판 태그(`@v1`)에 고정합니다. 호환되는 변경은 태그를 옮기고, 호환되지 않는 변경은 새 큰 판을 냅니다. 결정 기록은 [docs/adr](docs/adr/README.md)에 있습니다.

## 라이선스

[MIT](LICENSE)
