# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

TobaBuzzPR は、京都府立鳥羽高等学校の広報刷新プロジェクト。ソフトウェア開発ではなく**学校広報の仕組み作り**が主目的。主な成果物はドキュメントとWebプレゼン資料。

- **ターゲット**: 中学生へのリーチ強化
- **施策**: Instagram広報の導入 + ホームページの刷新

## コンテキスト読み込み（セッション開始時）

セッション開始時は以下の順で読むこと：

1. `.agent/workflows/development-rules.md` — プロジェクト固有ルール
2. `.agent/workflows/context.md` — 現在のステータスと前回の作業文脈
3. 必要に応じて `.agent/SPEC.md`、`.agent/PLAN.md`、`.agent/KNOWLEDGE.md` を参照

## セッション終了時

`.agent/workflows/close.md` の手順に従い、context.md / KNOWLEDGE.md / SPEC.md / PLAN.md を更新して報告する。

## 成果物

| ファイル | 内容 |
|---|---|
| `presentation/index.html` | 管理職・職員会議向けWebプレゼン資料（全4章）。GitHub Pages で公開中。 |
| `kyoto_highschool_admission_ratios.md` | 京都府公立高校の前期・中期選抜の100%全数調査データ |
| `kyoto_highschool_data.md` | 全97校のInstagram運用状況調査データ |

`presentation/index.html` は単一の自己完結型HTMLファイル（Tailwind CSS CDN + Leaflet.js による地図機能）。ビルドステップは不要で、ブラウザで直接開いて確認できる。

## 編集ルール

### 個人情報・肖像権
- 生徒の実名・顔写真はドキュメント内に記載しない
- 管理職・教員の実名も避け、役職で表記（「校長」「広報担当」等）
- 他校のSNS調査は公開情報のみを対象とする

### データの取り扱い
- 調査・リサーチの結果は `.agent/KNOWLEDGE.md` に記録して再利用可能にする
- 入試データは「100%網羅ポリシー」を維持する（部分的な更新をしない）

## Python環境（research_tools/）

`research_tools/` 配下に PDF解析・データ整形スクリプト群がある（`.venv` で管理）。

```bash
source .venv/bin/activate
python research_tools/<script>.py
```

生データPDFは `docs/raw_data/` に格納されている。
