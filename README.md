<div align="center">

![Image](https://github.com/user-attachments/assets/e47df212-9f09-4c43-8a66-ced8e1b1fb7c)

# 🎤 VOICEVOX OpenAI TTS API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.13%2B-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-009688)](https://fastapi.tiangolo.com/)

VOICEVOX/AivisSpeechエンジンをOpenAIの音声合成APIフォーマットで利用するためのAPIサーバーです。

</div>

## 🌟 特徴

- VOICEVOX互換エンジンによる日本語音声合成をOpenAI TTS APIと互換のフォーマットで音声合成が可能
- VOIVEVOX, AivisSpeech等に対応
- OpenWebUI からの読み上げに対応
- // TODO: voice_mappings について書く

## 🚀 Quick Start

### 方法1: Docker Composeですべて起動（推奨）

VOICEVOX Engine や AivisSpeech Engine の音声合成をセットで起動します。

事前に Docker と Docker Compose がインストールされている必要があります。

```bash
# リポジトリをクローン
git clone <...>
cd voicevox-openai-tts

# VOICEVOX（CPU版）で使う場合
docker compose up -d

# VOICEVOX（GPU NVIDIA）を使う場合
docker compose -f docker-compose.gpu.yml up -d

# AivisSpeech（CPU版）を使う場合
docker compose -f docker-compose.aivis-speech.yml up -d
```

OpenAI 互換のAPIが `http://localhost:8000/v1` にて理想可能です

### 方法2: ローカルでエンジンを起動 + Docker で API サーバーを起動

すでにローカルで VOICEVOX/AivisSpeech エンジンを起動している場合は、API サーバーだけを Docker で起動できます。

#### Step 1: ローカルでエンジンを起動

- [VOICEVOX](https://voicevox.hiroshiba.jp/) をダウンロードして起動（デフォルトでポート `50021` ）
- または [AivisSpeech](https://aivis-project.com/) を起動（デフォルトでポート `10101` ）

#### Step 2: API サーバーを Docker で起動

```bash
# VOICEVOX をローカルで起動している場合（Mac/Linux 例）
docker run --rm -p 8000:8000 \
  -e VOICEVOX_ENGINE_URL=http://host.docker.internal:50021 \
  ghcr.io/...

# AivisSpeech をローカルで起動している場合（Mac/Linux 例）
docker run --rm -p 8000:8000 \
  -e VOICEVOX_ENGINE_URL=http://host.docker.internal:10101 \
  ghcr.io/...
```

#### Step 3: OpenWebUI などでの設定

- OpenAI 互換のAPIが `http://localhost:8000/v1` or `http://host.docker.internal:8000/v1` にて利用可能
- OpenWebUI の設定例：
  - Settings → Audio → Text-to-Speech で「OpenAI」を選択
  - API Base URL: `http://localhost:8000/v1` or `http://host.docker.internal:8000/v1`
  - API Key: 任意の値（`sk-1234`など）
  - Model: `voicevox-v1`
  - Voice: `alloy`（または `/v1/audio/voices` で取得した `id` を使用）

### 方法3: 手動で起動（開発・カスタマイズ用）

Docker を使わずに、ローカルで開発環境を構築して起動する方法です。

#### Step 1: ローカルでエンジンを起動

- [VOICEVOX](https://voicevox.hiroshiba.jp/) をダウンロードして起動（デフォルトでポート 50021）
- または [AivisSpeech](https://aivis-project.com/) を起動（デフォルトでポート 10101）

#### Step 2: 依存関係をインストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd voicevox-openai-tts

# 依存関係をインストール
uv sync
```

#### Step 3: 環境変数を設定

```bash
# VOICEVOX の場合
export VOICEVOX_ENGINE_URL=http://localhost:50021

# AivisSpeech の場合
export VOICEVOX_ENGINE_URL=http://localhost:10101
```

#### Step 4: API サーバーを起動

```bash
# 開発サーバーを起動（ホットリロード付き）
uv run uvicorn voicevox_openai_tts.main:app --host 0.0.0.0 --port 8000 --reload
```

API が `http://localhost:8000` で利用可能になります。

## 📡 API仕様

### エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| POST | `/v1/audio/speech` | テキストを音声に変換 |
| GET | `/v1/audio/voices` | 利用可能な音声一覧を取得 |
| GET | `/health` | ヘルスチェック |

`http://localhost:8000/docs` で Swagger UI も利用可能です

### POST /v1/audio/speech

テキストを音声に変換します（OpenAI TTS API互換）。

**リクエスト例:**

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "voicevox-v1",
    "input": "こんにちは、音声合成のテストです。",
    "voice": "alloy",
    "speed": 1.0
  }' \
  --output output.mp3
```

**リクエストパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `model` | string | Yes | モデル名（"voicevox-v1"固定） |
| `input` | string | Yes | 読み上げるテキスト |
| `voice` | string | Yes | 話者ID（VOICEVOX StyleID, `/v1/audio/voices` で取得可能）またはOpenAI互換名（alloy, ash等） |
| `speed` | float | No | 読み上げ速度（0.5〜2.0、デフォルト: 1.0） |

**レスポンス:**

- Content-Type: `audio/mpeg`
- Body: MP3形式の音声データ（バイナリ）

### GET /v1/audio/voices

利用可能な音声一覧を取得します（OpenWebUI互換）。

**リクエスト例:**

```bash
curl http://localhost:8000/v1/audio/voices
```

**レスポンス例:**

```json
{
  "voices": [
    {
      "id": "2",
      "name": "四国めたん / ノーマル"
    },
    {
      "id": "0",
      "name": "四国めたん / あまあま"
    },
    ...
    {
      "id": "alloy",
      "name": "alloy"
    },
    ...
  ]
}
```


```python
from openai import OpenAI

# カスタムベースURLを持つOpenAIクライアントを作成
client = OpenAI(base_url="http://localhost:8000", api_key="sk-1234")

# 音声を生成
response = client.audio.speech.create(
    model="voicevox-v1",
    voice="1",
    input="こんにちは、音声合成のテストです。",
    speed=1.0
)

# 音声ファイルを保存（ストリーミングレスポンスを使用）
with response.with_streaming_response.stream_to_file("output.mp3"):
    pass
```

## 📁 プロジェクト構造

```
.
├── docker-compose.yml                          # VOICEVOX CPU版
├── docker-compose.gpu.yml                      # VOICEVOX GPU版
├── docker-compose.aivis-speech.yml             # AivisSpeech Docker版
├── docker-compose.aivis-speech-api-only.yml    # AivisSpeech（ローカル実行）用APIブリッジ
├── Dockerfile                                  # APIサーバーのビルド設定
├── pyproject.toml                              # Pythonパッケージ設定
├── voice_mappings/                             # 各エンジン用の話者IDマッピング
│   ├── voicevox.json
│   └── aivis-speech.json
├── src/
│   └── voicevox_openai_tts/                    # OpenAI互換APIの実装
│       ├── main.py                             # アプリケーションエントリポイント
│       ├── api/                                # API層
│       │   ├── create_app.py                  # FastAPIアプリケーション作成
│       │   ├── routers/                       # APIルーター
│       │   │   ├── speech.py                  # 音声合成エンドポイント
│       │   │   ├── voices.py                  # 音声一覧エンドポイント
│       │   │   └── core.py                    # 基本エンドポイント（health等）
│       │   ├── schemas/                       # Pydanticスキーマ
│       │   └── voice_mappings.py              # 音声マッピング設定
│       └── services/                          # ビジネスロジック層
│           ├── speech.py                      # 音声合成サービス
│           └── voice.py                       # 音声情報サービス
├── tests/                                      # テストコード
└── example/                                    # 使用例
    ├── tts_example.py
    └── simple_tts_example.py
```


## 🔧 環境変数

| 変数名 | デフォルト | 説明 |
|--------|-----------|------|
| `VOICEVOX_ENGINE_URL` | `http://localhost:50021` | VOICEVOX/AivisSpeechエンジンのURL |
| `VOICE_MAPPINGS_PATH` | - | 音声マッピングJSONファイルのパス |

## 🔒 ライセンス

MITライセンス

---

*このプロジェクトは [litagin02/voicevox-openai-tts](https://github.com/Sunwood-ai-labs/voicevox-openai-tts) をフォーク・リファクタリングしたものです。*
