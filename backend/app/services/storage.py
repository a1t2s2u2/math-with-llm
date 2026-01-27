import json
from pathlib import Path

from app.config import settings
from app.models.note import Note


def _get_note_path(note_id: str) -> Path:
    return settings.data_dir / f"{note_id}.json"


def create_note(note: Note) -> Note:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    note_path = _get_note_path(note.note_id)

    temp_path = note_path.with_suffix(".tmp")
    temp_path.write_text(note.model_dump_json(indent=2), encoding="utf-8")
    temp_path.rename(note_path)

    return note


def get_note(note_id: str) -> Note | None:
    note_path = _get_note_path(note_id)
    if not note_path.exists():
        return None

    note_data = json.loads(note_path.read_text(encoding="utf-8"))
    return Note(**note_data)


def update_note(note: Note) -> Note:
    note_path = _get_note_path(note.note_id)

    temp_path = note_path.with_suffix(".tmp")
    temp_path.write_text(note.model_dump_json(indent=2), encoding="utf-8")
    temp_path.rename(note_path)

    return note
