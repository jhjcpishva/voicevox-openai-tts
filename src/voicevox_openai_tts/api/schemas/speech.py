from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VoicevoxOptions(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    intonation_scale: float | None = Field(
        default=None,
        ge=0,
        le=2,
        serialization_alias="intonationScale",
        description="両方対応。VOICEVOXでは抑揚、AivisSpeechではスタイルの強さ。AivisSpeechのノーマルスタイルでは無視されます。",
    )
    tempo_dynamics_scale: float | None = Field(
        default=None,
        ge=0,
        le=2,
        serialization_alias="tempoDynamicsScale",
        description="AivisSpeech専用。話すテンポの緩急。",
    )
    pitch_scale: float | None = Field(
        default=None,
        ge=-0.15,
        le=0.15,
        serialization_alias="pitchScale",
        description="両方対応。音高。AivisSpeechでは変更すると音質が低下する可能性があります。",
    )
    volume_scale: float | None = Field(
        default=None,
        ge=0,
        le=2,
        serialization_alias="volumeScale",
        description="両方対応。音量の倍率。0で無音になります。",
    )
    pre_phoneme_length: float | None = Field(
        default=None,
        ge=0,
        serialization_alias="prePhonemeLength",
        description="両方対応。音声の開始前の無音時間（秒）。",
    )
    post_phoneme_length: float | None = Field(
        default=None,
        ge=0,
        serialization_alias="postPhonemeLength",
        description="両方対応。音声の終了後の無音時間（秒）。",
    )
    pause_length: float | None = Field(
        default=None,
        ge=0,
        serialization_alias="pauseLength",
        description="VOICEVOX専用。句読点などの無音時間（秒）。AivisSpeechでは無視されます。",
    )
    pause_length_scale: float | None = Field(
        default=None,
        ge=0,
        serialization_alias="pauseLengthScale",
        description="VOICEVOX専用。句読点などの無音時間の倍率。AivisSpeechでは無視されます。",
    )
    enable_interrogative_upspeak: bool | None = Field(
        default=None,
        description="VOICEVOX専用。疑問文の語尾を自動調整するか。AivisSpeechでは無視されます。",
    )


class SpeechRequest(BaseModel):
    """
    OpenAI TTS API互換のリクエストモデル

    Attributes:
        model: 使用するモデル（現在は"voicevox-v1"のみサポート）
        input: 読み上げるテキスト
        voice: 音声指定（音声名またはVOICEVOXのスピーカーID）
               音声名: "alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"
               または直接スピーカーIDを指定（例: "1"）
        response_format: 出力フォーマット（"mp3"または"wav"）
        speed: 読み上げ速度（1.0がデフォルト）
    """

    model: str
    input: str
    voice: str
    response_format: Literal["mp3", "wav"] = "mp3"
    speed: float = 1.0
    voicevox: VoicevoxOptions = Field(
        default_factory=VoicevoxOptions,
        description="VOICEVOX/AivisSpeech向けオプション。接続先の種類・対応可否は判定せず、指定値をエンジンへ渡します。未指定・nullはエンジンの既定動作を維持します。",
    )
