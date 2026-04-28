def transcribe_voice(audio_file_id: str | None, voice_file_id: str | None) -> str:
    source = audio_file_id or voice_file_id or "unknown"
    return f"[MOCK STT] Расшифровка голосового сообщения ({source}): нужно проверить результаты моделирования и подготовить отчет."
