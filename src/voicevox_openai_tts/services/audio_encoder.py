import io
import wave
from typing import Protocol

import lameenc


class AudioEncodingError(Exception):
    """音声エンコードに失敗した場合のエラー"""


class AudioEncoder(Protocol):
    """音声エンコーダーが実装するインターフェイス"""

    media_type: str

    def encode(self, wav_data: bytes) -> bytes:
        """WAVデータを変換し、失敗時はAudioEncodingErrorを送出する。"""


class WavPassthroughEncoder:
    """WAVデータを変換せずに返す。"""

    media_type = "audio/wav"

    def encode(self, wav_data: bytes) -> bytes:
        return wav_data


class LameMp3Encoder:
    """lameencを使用してWAVデータをMP3へ変換する。"""

    media_type = "audio/mpeg"

    def __init__(self, bit_rate: int = 64, quality: int = 7):
        self.bit_rate = bit_rate
        self.quality = quality

    def encode(self, wav_data: bytes) -> bytes:
        try:
            with wave.open(io.BytesIO(wav_data), "rb") as wav_file:
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                sample_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
        except (EOFError, wave.Error) as error:
            raise AudioEncodingError("Invalid WAV data") from error

        if sample_width != 2:
            raise AudioEncodingError(
                f"Unsupported WAV sample width: {sample_width * 8} bits"
            )
        if channels not in (1, 2):
            raise AudioEncodingError(f"Unsupported WAV channel count: {channels}")

        try:
            encoder = lameenc.Encoder()
            encoder.silence()
            encoder.set_bit_rate(self.bit_rate)
            encoder.set_quality(self.quality)
            encoder.set_in_sample_rate(sample_rate)
            encoder.set_channels(channels)
            encoded = encoder.encode(frames) + encoder.flush()
        except (RuntimeError, ValueError) as error:
            raise AudioEncodingError("MP3 encoding failed") from error

        if not encoded:
            raise AudioEncodingError("MP3 encoder returned empty audio data")

        return bytes(encoded)
