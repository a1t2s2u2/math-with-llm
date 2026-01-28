import uuid


def generate_note_id() -> str:
    return f"note_{uuid.uuid4().hex[:12]}"


def generate_block_id() -> str:
    return f"blk_{uuid.uuid4().hex[:8]}"
