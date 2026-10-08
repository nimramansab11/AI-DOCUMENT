from pathlib import Path
from pypdf import PdfReader


class DocumentIngestion:
    def __init__(self, chunk_size=1000, chunk_overlap=150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_document(self, file_path):
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == ".pdf":
            return self._read_pdf(path)

        if extension in [".txt", ".md"]:
            return path.read_text(encoding="utf-8")

        raise ValueError(f"Unsupported file type: {extension}")

    def _read_pdf(self, path):
        reader = PdfReader(str(path))

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if text.strip():
                pages.append(
                    f"[Page {page_number}]\n{text}"
                )

        return "\n\n".join(pages)

    def chunk_text(self, text):
        text = text.strip()

        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += self.chunk_size - self.chunk_overlap

        return chunks