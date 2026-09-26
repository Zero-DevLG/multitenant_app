import base64, uuid
from pathlib import Path

UPLOAD_DIR = Path("uploads/operator_documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def save_uploaded_file(operator_id: int, field_code: str, file_base64: str) -> str:
    raw_bytes = base64.b64decode(file_base64)
    filename = f"{operator_id}_{field_code}_{uuid.uuid4().hex}"
    path = UPLOAD_DIR / filename
    path.write_bytes(raw_bytes)
    return str(path)