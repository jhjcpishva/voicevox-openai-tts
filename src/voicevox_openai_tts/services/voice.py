from dataclasses import dataclass

import httpx

from ..api.voice_mappings import load_voice_mappings
from ..api.schemas.voices import AudioVoice
from ..settings import get_settings


@dataclass
class SpeakerInfo:
    """話者情報のデータクラス"""

    name: str
    styles: list[dict]


class VoiceService:
    """音声情報関連のビジネスロジックを担当するサービス"""

    def __init__(self, voicevox_engine_url: str | None = None):
        self.voicevox_url = voicevox_engine_url or get_settings().voicevox_engine_url

    def _build_voice_name(self, speaker_name: str, style_name: str) -> str:
        return f"{speaker_name} / {style_name}"

    def _flatten_speakers_to_voices(self, speakers: list[dict]) -> list[AudioVoice]:
        """
        VOICEVOXエンジンから取得した話者情報をAudioVoiceリストに変換

        Args:
            speakers: VOICEVOXエンジンから取得した話者情報のリスト

        Returns:
            list[AudioVoice]: 変換後の音声情報リスト
        """
        voices: list[AudioVoice] = []

        for speaker in speakers:
            speaker_name = speaker.get("name", "")

            for style in speaker.get("styles", []):
                style_id = style.get("id")
                style_name = style.get("name", "")

                if style_id is None:
                    continue

                voices.append(
                    AudioVoice(
                        id=str(style_id),
                        name=self._build_voice_name(speaker_name, style_name),
                    )
                )

        return voices

    def _get_mapping_aliases(self) -> list[AudioVoice]:
        """
        voice_mappingsのエイリアスをAudioVoiceリストに変換

        Returns:
            list[AudioVoice]: マッピングエイリアスの音声情報リスト
        """
        return [AudioVoice(id=alias, name=alias) for alias in load_voice_mappings()]

    async def get_available_voices(self) -> list[AudioVoice]:
        """
        利用可能な音声一覧を取得

        Returns:
            list[AudioVoice]: 利用可能な音声情報のリスト

        Raises:
            httpx.HTTPError: VOICEVOXエンジンとの通信に失敗した場合
        """
        speakers_url = f"{self.voicevox_url}/speakers"

        async with httpx.AsyncClient() as client:
            response = await client.get(speakers_url)
            response.raise_for_status()

        speakers_data = response.json()
        style_voices = self._flatten_speakers_to_voices(speakers_data)
        alias_voices = self._get_mapping_aliases()

        return style_voices + alias_voices
