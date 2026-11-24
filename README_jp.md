# Concordia

[English](README.md) · [한국어](README_kr.md)

自分のリポジトリで CI を同じやり方で回すための、GitHub Actions の共用ワークフローです。
*Concordia* はラテン語で「心を一つに」。リポジトリは多くても拍子は一つ、という意味で名付けました。

## ワークフロー

| ワークフロー | すること |
|---|---|
| [`python-tests.yml`](.github/workflows/python-tests.yml) | リポジトリを取得し、Python をバージョンごとに用意して、インストールとテストのコマンドを実行します |
| [`hygiene.yml`](.github/workflows/hygiene.yml) | 公開リポジトリ向けの形式チェック：ローカルのエージェント・状態ファイルが追跡されていないか、ホームディレクトリの絶対パスがないかを見ます。内部のプロジェクト番号の形は警告だけ出します |

## 使い方

呼び出す側の `.github/workflows/tests.yml` に次のように書きます。

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

`python-tests.yml` の入力：

| 入力 | 既定値 | 備考 |
|---|---|---|
| `python-versions` | `'["3.12"]'` | JSON 配列、バージョンごとにジョブ一つ |
| `install` | `python -m pip install -r requirements.txt` | 任意のシェルコマンド、複数行可 |
| `test` | `python -m pytest -q` | 任意のシェルコマンド |
| `cache` | `pip` | requirements・pyproject ファイルがなければ `''` で無効に |
| `working-directory` | `.` | |

`hygiene.yml` の入力は `strict`（警告も失敗にする、既定 `false`）と `concordia-ref`（チェック用スクリプトを取る版、`uses:` のタグと同じに）です。
意図して除外するファイル（テストデータなど）は、リポジトリ直下の `.concordia-allow` に glob で一行ずつ書きます。

チェックは決まった形式だけを見ます。ファイルの中身が何についてのものかは判断しません。

## 版

呼び出す側はメジャータグ（`@v1`）に固定します。互換のある変更はタグを動かし、互換のない変更は新しいメジャー版にします。決定記録は [docs/adr](docs/adr/README.md) にあります。

## ライセンス

[MIT](LICENSE)
