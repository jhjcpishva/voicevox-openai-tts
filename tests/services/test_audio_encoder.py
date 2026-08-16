import io
import wave

import pytest

from voicevox_openai_tts.services.audio_encoder import AudioEncodingError
from voicevox_openai_tts.services.audio_encoder import LameMp3Encoder
from voicevox_openai_tts.services.audio_encoder import WavPassthroughEncoder


def create_wav(
    *, channels: int = 1, sample_width: int = 2, sample_rate: int = 24000
) -> bytes:
    buffer = io.BytesIO()
    with wave.Wave_write(buffer) as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        frame_count = channels * sample_width * sample_rate // 10
        wav_file.writeframes(b"\x00" * frame_count)
    return buffer.getvalue()


class TestLameMp3Encoder:
    def test_encode_returns_mp3_data(self):
        encoded = LameMp3Encoder().encode(create_wav())

        assert isinstance(encoded, bytes)
        assert encoded
        assert not encoded.startswith(b"RIFF")
        assert encoded[0] == 0xFF
        assert encoded[1] & 0xE0 == 0xE0

    def test_encode_uses_wav_parameters(self, monkeypatch):
        encoder_calls = {}

        class FakeEncoder:
            def silence(self):
                encoder_calls["silence"] = True

            def set_bit_rate(self, value):
                encoder_calls["bit_rate"] = value

            def set_quality(self, value):
                encoder_calls["quality"] = value

            def set_in_sample_rate(self, value):
                encoder_calls["sample_rate"] = value

            def set_channels(self, value):
                encoder_calls["channels"] = value

            def encode(self, frames):
                encoder_calls["frames"] = frames
                return b"encoded"

            def flush(self):
                return b"flushed"

        monkeypatch.setattr(
            "voicevox_openai_tts.services.audio_encoder.lameenc.Encoder",
            FakeEncoder,
        )

        encoded = LameMp3Encoder(bit_rate=96, quality=5).encode(
            create_wav(channels=2, sample_rate=48000)
        )

        assert encoded == b"encodedflushed"
        assert encoder_calls["silence"] is True
        assert encoder_calls["bit_rate"] == 96
        assert encoder_calls["quality"] == 5
        assert encoder_calls["sample_rate"] == 48000
        assert encoder_calls["channels"] == 2
        assert encoder_calls["frames"]

    def test_encode_rejects_invalid_wav(self):
        with pytest.raises(AudioEncodingError, match="Invalid WAV data"):
            LameMp3Encoder().encode(b"not a wav file")

    def test_encode_rejects_unsupported_sample_width(self):
        with pytest.raises(AudioEncodingError, match="24 bits"):
            LameMp3Encoder().encode(create_wav(sample_width=3))


class TestWavPassthroughEncoder:
    def test_encode_returns_original_wav_data(self):
        wav_data = create_wav()

        encoded = WavPassthroughEncoder().encode(wav_data)

        assert encoded is wav_data
        assert WavPassthroughEncoder.media_type == "audio/wav"
