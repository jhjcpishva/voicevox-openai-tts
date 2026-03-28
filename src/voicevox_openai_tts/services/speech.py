import httpx

from ..api.voice_mappings import load_voice_mappings
from ..settings import get_settings


class SpeechServiceError(Exception):
    """Speechサービス関連のエラー"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidVoiceError(SpeechServiceError):
    """無効な音声指定時のエラー"""

    def __init__(self, voice: str, available_voices: list[str]):
        message = (
            f"Invalid voice: {voice}. Available voices: {', '.join(available_voices)}"
        )
        super().__init__(message, status_code=400)


class SpeechService:
    """音声合成関連のビジネスロジックを担当するサービス"""

    def __init__(self, voicevox_engine_url: str | None = None):
        self.voicevox_url = voicevox_engine_url or get_settings().voicevox_engine_url

    def _get_speaker_id(self, voice: str) -> int:
        """
        音声名またはIDからスピーカーIDを取得

        Args:
            voice: 音声名または音声ID

        Returns:
            int: スピーカーID

        Raises:
            InvalidVoiceError: 無効な音声指定時
        """
        mappings = load_voice_mappings()

        # マッピングに存在する場合はマッピングされたIDを返す
        if voice in mappings:
            return int(mappings[voice])

        # 直接数値が指定された場合はそのまま返す
        try:
            return int(voice)
        except ValueError:
            available = list(mappings.keys())
            raise InvalidVoiceError(voice, available)

    async def synthesize_speech(
        self, text: str, voice: str, speed: float = 1.0
    ) -> tuple[bytes, str]:
        """
        テキストを音声に変換

        Args:
            text: 読み上げるテキスト
            voice: 音声名または音声ID
            speed: 読み上げ速度（デフォルト: 1.0）

        Returns:
            tuple[bytes, str]: 音声データとメディアタイプ

        Raises:
            SpeechServiceError: 音声合成に失敗した場合
        """
        speaker_id = self._get_speaker_id(voice)
        audio_query_url = f"{self.voicevox_url}/audio_query"
        synthesis_url = f"{self.voicevox_url}/synthesis"

        try:
            async with httpx.AsyncClient() as client:
                # VOICEVOXのクエリを作成
                query_response = await client.post(
                    audio_query_url, params={"text": text, "speaker": speaker_id}
                )
                query_response.raise_for_status()
                query_data = query_response.json()

                # 読み上げ速度を設定
                query_data["speedScale"] = speed

                # 音声合成を実行
                synthesis_response = await client.post(
                    synthesis_url, params={"speaker": speaker_id}, json=query_data
                )
                synthesis_response.raise_for_status()

            return synthesis_response.content, "audio/mpeg"

        except httpx.HTTPError as e:
            raise SpeechServiceError(
                f"VOICEVOXエンジンとの通信に失敗しました: {str(e)}",
                status_code=500,
            )
