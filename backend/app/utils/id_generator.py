import hashlib
import uuid


def generate_note_id() -> str:
    return f"note_{uuid.uuid4().hex[:12]}"


def generate_block_id() -> str:
    return f"blk_{uuid.uuid4().hex[:8]}"


def generate_block_id_from_content(block_type: str, start: int, content: str) -> str:
    """ブロックの内容から決定論的にIDを生成"""
    hash_input = f"{block_type}:{start}:{content[:100]}"
    hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    return f"blk_{hash_value}"
