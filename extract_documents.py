from pathlib import Path
import sys

import docx
import pdfplumber

def extract_docx(file_path: Path) -> str:
    """Extract paragraph and table text from a DOCX file."""
    document = docx.Document(file_path)
    sections = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            sections.append(text)

    for table in document.tables:
        for row in table.rows:
            cells = [
                cell.text.strip().replace("\n", " ")
                for cell in row.cells
            ]
            sections.append(" | ".join(cells))

    return "\n".join(sections)

def extract_pdf(file_path:Path) -> tuple[str, int, list[int]]:
    """Extract text from each page of a text-based PDF."""
    page_texts = []
    empty_pages = []

    with pdfplumber.open(file_path) as pdf:
        page_count = len(pdf.pages)

        for page_number, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or "").strip()
            page_texts.append(text)

            if not text:
                empty_pages.append(page_number)

    return "\n".join(page_texts), page_count, empty_pages

def main() -> None:
    if len(sys.argv) != 2:
        print(
            'Usage: python extract_documents.py "path\\to\\resume.docx"'
        )
        raise SystemExit(1)
    
    file_path = Path(sys.argv[1])

    if not file_path.is_file():
        print("Error: File not found.")
        raise SystemExit(1)

    try:
        if file_path.suffix.lower() == ".docx":
            text = extract_docx(file_path)
            page_count = None
            empty_pages = []

        elif file_path.suffix.lower() == ".pdf":
            text, page_count, empty_pages = extract_pdf(file_path)

        else:
            print("Error: Only .docx and .pdf files are supported.")
            raise SystemExit(1)

        print(f"File: {file_path.name}")
        if page_count is not None:
            print(f"PDF pages: {page_count}")
        print(f"Extracted characters: {len(text)}")

        if empty_pages:
            print(
                "Warning: No text extracted from page(s): "
                + ", ".join(map(str, empty_pages))
            )
            print("These pages may be scanned or contain no text.")

        if not text.strip():
            print("Warning: No readable text was extracted.")
        else:
            print("\n--- Complete extracted resume text ---\n")
            print(text)
            print("\n--- End of extracted resume text ---")

    except Exception as error:
        print(f"Extraction failed: {type(error).__name__}: {error}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()