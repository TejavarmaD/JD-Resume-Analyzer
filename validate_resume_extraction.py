
from pathlib import Path
import re
from difflib import SequenceMatcher

from extract_documents import extract_docx, extract_pdf


RESUME_DIR = Path(
    r"C:\Users\tejavarma.dommaraju\OneDrive - OneWorkplace\Desktop\Resume"
)

PDF_FILE = RESUME_DIR / "Tejavarma Dommaraju(Resume).pdf"
DOCX_FILE = RESUME_DIR / "Tejavarma Dommaraju_Resume.docx"

OUTPUT_DIR = Path("extraction_results")

# Headings and keywords expected in this resume.
EXPECTED_SECTIONS = [
    "EXECUTIVE SUMMARY",
    "WORK EXPERIENCE",
    "PROJECT WORK",
    "SKILLS",
    "EDUCATION",
    "CERTIFICATIONS",
]

IMPORTANT_TERMS = [
    "Omnicom Global Solutions",
    "Johnson Controls",
    "Renault",
    "Dacia",
    "Python",
    "SQL",
    "Power BI",
    "Snowflake",
    "Data Forge",
    "Revenue Insights",
    "Bachelor of Technology",
    "Google Data Analytics",
]


def normalize(text: str) -> str:
    """Normalize whitespace and case for content comparison."""
    text = text.casefold()
    return re.sub(r"\s+", " ", text).strip()


def extract_file(path: Path) -> tuple[str, int | None, list[int]]:
    """Extract text using the existing parser."""
    if not path.is_file():
        raise FileNotFoundError(f"Resume not found: {path}")

    if path.suffix.lower() == ".docx":
        return extract_docx(path), None, []

    if path.suffix.lower() == ".pdf":
        text, pages, empty_pages = extract_pdf(path)
        return text, pages, empty_pages

    raise ValueError(f"Unsupported file type: {path.suffix}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    results = {}

    for path in [PDF_FILE, DOCX_FILE]:
        text, pages, empty_pages = extract_file(path)
        results[path.suffix.lower()] = text

        # Save the complete extracted text locally.
        output_file = OUTPUT_DIR / f"{path.suffix[1:]}_extracted.txt"
        output_file.write_text(text, encoding="utf-8")

        print(f"\n{'=' * 60}")
        print(f"FILE: {path.name}")
        print(f"Extracted characters: {len(text)}")

        if pages is not None:
            print(f"PDF pages: {pages}")

        if not text.strip():
            print("FAIL: No readable text extracted.")
        elif len(text.strip()) < 1000:
            print("WARNING: Very little text extracted; inspect the source.")
        else:
            print("PASS: Non-empty text extracted.")

        if empty_pages:
            print(f"WARNING: PDF pages with no extracted text: {empty_pages}")

        normalized = normalize(text)

        print("\nExpected section checks:")
        for section in EXPECTED_SECTIONS:
            found = section.casefold() in normalized
            status = "FOUND" if found else "NOT FOUND"
            print(f"  {status}: {section}")

        print("\nImportant content checks:")
        for term in IMPORTANT_TERMS:
            found = term.casefold() in normalized
            status = "FOUND" if found else "NOT FOUND"
            print(f"  {status}: {term}")

    pdf_text = normalize(results[".pdf"])
    docx_text = normalize(results[".docx"])

    similarity = SequenceMatcher(
        None, pdf_text, docx_text
    ).ratio() * 100

    print(f"\n{'=' * 60}")
    print(f"Normalized text similarity: {similarity:.1f}%")
    print("Note: Similarity is a diagnostic, not a correctness score.")

    pdf_missing = [
        term for term in IMPORTANT_TERMS
        if term.casefold() not in pdf_text
        and term.casefold() in docx_text
    ]

    docx_missing = [
        term for term in IMPORTANT_TERMS
        if term.casefold() not in docx_text
        and term.casefold() in pdf_text
    ]

    print("\nImportant terms present in DOCX but absent from PDF:")
    print(pdf_missing if pdf_missing else "None detected")

    print("\nImportant terms present in PDF but absent from DOCX:")
    print(docx_missing if docx_missing else "None detected")

    print(f"\nFull extracted text saved in: {OUTPUT_DIR.resolve()}")
    print("Open both .txt files to inspect reading order and completeness.")


if __name__ == "__main__":
    main()
