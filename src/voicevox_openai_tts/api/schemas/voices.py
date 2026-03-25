from pydantic import BaseModel


class AudioVoice(BaseModel):
    id: str
    name: str


class AudioVoicesResponse(BaseModel):
    voices: list[AudioVoice]
