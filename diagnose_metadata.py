
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "structured_results"

PDF_FILE = RESULTS_DIR / "Tejavarma Dommaraju(Resume)_entities.json"
DOCX_FILE = RESULTS_DIR / "Tejavarma Dommaraju_Resume_entities.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def compare_values(pdf_value, docx_value, path="$"):
    if isinstance(pdf_value, dict) and isinstance(docx_value, dict):
        for key in sorted(set(pdf_value) | set(docx_value)):
            if key not in pdf_value:
                print(f"MISSING IN PDF: {path}.{key}")
            elif key not in docx_value:
                print(f"MISSING IN DOCX: {path}.{key}")
            else:
                compare_values(
                    pdf_value[key], docx_value[key], f"{path}.{key}"
                )

    elif isinstance(pdf_value, list) and isinstance(docx_value, list):
        if len(pdf_value) != len(docx_value):
            print(
                f"LENGTH DIFFERENCE: {path} "
                f"(PDF={len(pdf_value)}, DOCX={len(docx_value)})"
            )

        for index, (pdf_item, docx_item) in enumerate(
            zip(pdf_value, docx_value)
        ):
            compare_values(pdf_item, docx_item, f"{path}[{index}]")

    elif pdf_value != docx_value:
        print(f"\nDIFFERENCE: {path}")
        print(f"PDF : {pdf_value!r}")
        print(f"DOCX: {docx_value!r}")


def main():
    pdf_data = load_json(PDF_FILE)
    docx_data = load_json(DOCX_FILE)

    print("SOURCE SECTION TEXT")
    print("=" * 60)
    compare_values(
        pdf_data.get("source_section_text", {}),
        docx_data.get("source_section_text", {}),
        "source_section_text",
    )

    print("\nCERTIFICATIONS AND ACTIVITIES")
    print("=" * 60)
    compare_values(
        pdf_data.get("certifications_and_activities", {}),
        docx_data.get("certifications_and_activities", {}),
        "certifications_and_activities",
    )


if __name__ == "__main__":
    main()
