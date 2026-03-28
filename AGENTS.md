# AGENTS.md - AI Agent Guidelines

このファイルは、コーディング AI エージェントがこのリポジトリで作業する際のガイドラインです。

## プロジェクト概要

VOICEVOX OpenAI TTS API は、VOICEVOX/AivisSpeech エンジンを OpenAI 互換の音声合成 API として提供する FastAPI サーバーです。

## 開発ワークフロー

### ブランチ戦略

- **main**: 本番ブランチ
- **<agent-prefix>/**: AIエージェント作業用ブランチ（例: `codex/service-layer`, `gemini/service-layer`, `claude/service-layer`, `opencode/service-layer`）
- **feature/**: 機能開発ブランチ

### 作業フロー

1. main から作業ブランチを作成: `git checkout -b <agent-prefix>/<task-name>`
2. 変更を実装
3. **pre-commit hook での自動修正:**
   - pre-commit hook によるコード修正が発生した場合、AIエージェントは**自動的に修正をコミットせず**、ユーザーに確認を取る
   - ユーザーが「修正内容を確認してコミットを続行」と指示した場合のみ、`git add` して再度コミット
4. コミット（Conventional Commits 形式）
5. PR を作成
6. レビュー後マージ

## コミット規約

### Conventional Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: 新機能
- `fix`: バグ修正
- `refactor`: リファクタリング（機能変更なし）
- `docs`: ドキュメントのみの変更
- `test`: テスト追加・修正
- `chore`: ビルド・ツール・依存関係の更新

**Scopes:**
- `router`: API ルーター関連
- `service`: Service 層関連
- `schema`: Pydantic スキーマ関連
- `docker`: Docker 設定関連
- `api`: 全体の API 関連

### コミットメッセージ例

```
refactor(router): extract business logic to service layer

- Move TTS logic from speech router to SpeechService
- Add custom exception classes for error handling
- Improve testability by separating HTTP and business layers

Co-authored-by: CODING_AGENT_NAME (MODEL_NAME) <agent@example.com>
```

### Co-authored-by 規約

AI エージェントが関与したコミットでは、コミットメッセージのフッターに必ず含める:

```
Co-authored-by: CODING_AGENT_NAME (MODEL_NAME) <agent@example.com>
```

- `CODING_AGENT_NAME`: エージェント名またはツール名（例: `OpenCode Agent`, `Claude Code`, `Gemini CLI`）
- `MODEL_NAME`: 使用した AI モデルの識別子（例: `openai/gpt-5.4`, `ollama/kimi-k2.5:cloud`）
- `agent@example.com`: エージェント用の連絡先表記。運用で固定値がある場合はそれを使う。

## 品質チェック

### 実行コマンド

```bash
# 自動整形・チェック（pre-commit hook）
git commit

# 手動実行
pre-commit run --all-files

# Python インポートチェック
uv run python -c "from voicevox_openai_tts.api.create_app import create_app"
```

### チェック項目

- ruff format: Python コード整形
- ruff check: リンチェック
- pylint: 静的解析
- pre-commit hooks: 全般チェック

## プロジェクト構成

```
src/voicevox_openai_tts/
├── api/
│   ├── routers/       # FastAPI ルーター（HTTP層）
│   ├── schemas/        # Pydantic スキーマ
│   └── voice_mappings/ # 音声マッピング設定
├── services/          # ビジネスロジック層
│   ├── speech.py     # 音声合成サービス
│   └── voice.py      # 音声情報サービス
└── main.py           # アプリケーションエントリーポイント
```

## 依存関係

- **FastAPI**: Web フレームワーク
- **httpx**: HTTP クライアント（VOICEVOX エンジン通信）
- **Pydantic**: データバリデーション
- **uv**: パッケージ管理・実行

## 重要な制約

### 絶対に避けるべきこと

- **機密情報のコミット**: APIキー、認証情報、`.env` ファイル
- **破壊的変更の force push**: main ブランチへの force push は禁止
- **テストなしの大規模リファクタリング**: 少なくとも手動で動作確認を行う
- **AIエージェントが触っていないファイルをコミット**: TASKS.md, IDEAS.md, .env.docker など、セッション中に編集していないファイルはコミット対象から除外する

### 注意事項

- VOICEVOX エンジンとの通信は非同期（httpx.AsyncClient）
- 環境変数 `VOICEVOX_ENGINE_URL` でエンジンURLを設定
- voice_mappings/ の JSON ファイルは読み取り専用
- **`__init__.py` の記述**: docstring などのコード記述は、ベストプラクティスとして明確に推奨されている場合（公式ドキュメント、PEP、プロジェクト内の既存コードの慣習など）のみに限定する。単なる慣習や過剰な実装を避ける。

## テスト

### 実行方法

```bash
# pytest 実行（導入後）
uv run pytest
```

### テスト方針

- Service 層のユニットテストを優先
- Router は必要最小限の統合テスト
- 外部エンジンを含む E2E テストはスコープ外

## ドキュメント更新

以下の変更時は関連ドキュメントを更新:

- **README.md**: セットアップ手順、API 仕様変更
- **CHANGELOG.md**: バージョン更新時（該当する場合）
- **example/**: サンプルコードの更新

---

*最終更新: 2026-03-26*
