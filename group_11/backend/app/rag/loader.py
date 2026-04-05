"""
Document loaders — ingest PDF, CSV, JSON, XLSX into text chunks.
Each loader returns a list of LangChain Document objects.
"""

import json
import tempfile
from pathlib import Path

from langchain_core.documents import Document


def load_pdf(file_path: str) -> list[Document]:
    """Extract text from a PDF using pdfplumber (handles tables well)."""
    import pdfplumber

    docs: list[Document] = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            # Also extract tables as text
            tables = page.extract_tables() or []
            table_texts: list[str] = []
            for table in tables:
                rows = [" | ".join(str(cell or "") for cell in row) for row in table if row]
                table_texts.append("\n".join(rows))

            full_text = text
            if table_texts:
                full_text += "\n\nTABLES:\n" + "\n\n".join(table_texts)

            if full_text.strip():
                docs.append(Document(
                    page_content=full_text.strip(),
                    metadata={"source": file_path, "page": i + 1, "type": "pdf"},
                ))
    return docs


def load_csv(file_path: str) -> list[Document]:
    """Convert CSV rows to natural language documents."""
    import pandas as pd

    df = pd.read_csv(file_path)
    docs: list[Document] = []

    # Create a summary document
    summary = f"CSV with {len(df)} rows and {len(df.columns)} columns.\n"
    summary += f"Columns: {', '.join(df.columns.tolist())}\n"
    summary += f"Summary stats:\n{df.describe().to_string()}"
    docs.append(Document(
        page_content=summary,
        metadata={"source": file_path, "type": "csv", "section": "summary"},
    ))

    # Convert each row to natural language
    for i, row in df.iterrows():
        row_text = " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
        docs.append(Document(
            page_content=row_text,
            metadata={"source": file_path, "type": "csv", "row": int(i)},
        ))
        if int(i) >= 200:  # Cap at 200 rows for now
            break

    return docs


def load_json(file_path: str) -> list[Document]:
    """Convert JSON to natural language documents."""
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    docs: list[Document] = []

    def _flatten(obj: dict | list, prefix: str = "") -> list[str]:
        lines: list[str] = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, (dict, list)):
                    lines.extend(_flatten(v, key))
                else:
                    lines.append(f"{key}: {v}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                lines.extend(_flatten(item, f"{prefix}[{i}]"))
        return lines

    lines = _flatten(data)
    # Chunk into groups of ~20 lines
    chunk_size = 20
    for i in range(0, len(lines), chunk_size):
        chunk = "\n".join(lines[i : i + chunk_size])
        docs.append(Document(
            page_content=chunk,
            metadata={"source": file_path, "type": "json", "chunk": i // chunk_size},
        ))

    return docs


def load_xlsx(file_path: str) -> list[Document]:
    """Convert Excel file to documents (similar to CSV)."""
    import pandas as pd

    docs: list[Document] = []
    xls = pd.ExcelFile(file_path)

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        summary = f"Sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns.\n"
        summary += f"Columns: {', '.join(df.columns.tolist())}"
        docs.append(Document(
            page_content=summary,
            metadata={"source": file_path, "type": "xlsx", "sheet": sheet_name, "section": "summary"},
        ))
        for i, row in df.iterrows():
            row_text = " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
            docs.append(Document(
                page_content=row_text,
                metadata={"source": file_path, "type": "xlsx", "sheet": sheet_name, "row": int(i)},
            ))
            if int(i) >= 200:
                break

    return docs


def load_image(file_path: str) -> list[Document]:
    """Extract text from an image using a vision LLM (Gemini Flash via OpenRouter)."""
    import base64

    from langchain_core.messages import HumanMessage
    from langchain_openai import ChatOpenAI

    from app.settings import get_settings

    settings = get_settings()

    # Read and base64-encode the image
    with open(file_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    ext = Path(file_path).suffix.lstrip(".").lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")

    # Use vision model via OpenRouter (Gemini Flash supports vision)
    if settings.llm_provider == "openrouter" and settings.openrouter_api_key:
        llm = ChatOpenAI(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            temperature=0.1,
            timeout=60,
            default_headers={
                "HTTP-Referer": "https://demoai-one.vercel.app",
                "X-Title": "DemoAI Vision",
            },
        )
    else:
        llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.1,
            timeout=60,
        )

    message = HumanMessage(
        content=[
            {"type": "text", "text": (
                "Extract ALL text and data from this financial document image. "
                "Include every number, name, date, account, transaction, and detail you can see. "
                "Format as plain text with key: value pairs where possible. "
                "If it's a table, reproduce the rows. Be thorough — extract everything."
            )},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_data}"}},
        ]
    )

    response = llm.invoke([message])
    text = response.content if isinstance(response.content, str) else str(response.content)

    docs: list[Document] = []
    if text.strip():
        # Chunk into ~500 char segments
        chunk_size = 500
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            docs.append(Document(
                page_content=chunk.strip(),
                metadata={"source": file_path, "type": "image", "chunk": i // chunk_size},
            ))

    return docs


# Registry — maps file extension to loader
LOADERS = {
    "pdf": load_pdf,
    "csv": load_csv,
    "json": load_json,
    "xlsx": load_xlsx,
    "png": load_image,
    "jpg": load_image,
    "jpeg": load_image,
    "webp": load_image,
}


def load_document(file_path: str) -> list[Document]:
    """Load a document using the appropriate loader based on file extension."""
    ext = Path(file_path).suffix.lstrip(".").lower()
    loader = LOADERS.get(ext)
    if not loader:
        raise ValueError(f"Unsupported file type: .{ext}. Supported: {', '.join(LOADERS.keys())}")
    return loader(file_path)


def load_from_bytes(content: bytes, filename: str) -> list[Document]:
    """Load a document from raw bytes (e.g., from file upload)."""
    ext = Path(filename).suffix.lstrip(".").lower()
    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        return load_document(tmp.name)
