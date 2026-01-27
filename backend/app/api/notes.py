from fastapi import APIRouter, HTTPException

from app.models.note import Note, NoteCreate, NoteUpdate
from app.services import parser, storage
from app.utils.id_generator import generate_note_id

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=Note)
def create_note_endpoint(note_create: NoteCreate) -> Note:
    note = Note(note_id=generate_note_id(), title=note_create.title)
    return storage.create_note(note)


@router.get("/{note_id}", response_model=Note)
def get_note_endpoint(note_id: str) -> Note:
    note = storage.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=Note)
def update_note_endpoint(note_id: str, note_update: NoteUpdate) -> Note:
    note = storage.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    note.latex_source = note_update.latex_source

    parse_result = parser.parse_latex(note_update.latex_source)
    note.blocks = parse_result.blocks
    note.symbols = parse_result.symbols
    note.todos = parse_result.todos

    return storage.update_note(note)
