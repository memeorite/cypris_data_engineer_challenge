# XML Document Number Extractor

Python solution for extracting `doc-number` values from patent XML documents with priority-based ordering.

## Priority Order

1. `format="epo"` AND `load-source="patent-office"` (both attributes)
2. `format="epo"` only
3. `load-source="patent-office"` only
4. All others

Within each priority group, document order is preserved.

## Installation

Requires Python 3.8+. Install dependencies using [uv](https://github.com/astral-sh/uv):

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Set up project
uv venv
uv pip install pytest

# Activate venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

Note: No package installation is needed to use the tool - it only uses Python's standard library. The `pytest` dependency is only for running tests.

## Usage

### Command Line

```bash
python extract_doc_numbers.py sample_patent.xml
```

Output:
```
Extracted 2 doc-number(s):
----------------------------------------
1. 999000888
2. 66667777
```

### Python Module

```python
from extract_doc_numbers import extract_doc_numbers

# From file
doc_numbers = extract_doc_numbers('patent.xml')

# From XML string
xml = """<root>
  <document-id format="epo">
    <doc-number>123456</doc-number>
  </document-id>
  <document-id load-source="patent-office">
    <doc-number>789012</doc-number>
  </document-id>
</root>"""
doc_numbers = extract_doc_numbers(xml)
print(doc_numbers)  # ['123456', '789012']
```

## Running Tests

```bash
pytest  # Run all tests
pytest -v  # Verbose output
pytest test_extract_doc_numbers.py::TestPriorityOrdering -v  # Specific class
```

**Test Coverage:** 23 tests covering priority ordering, edge cases, and error handling.

## Assumptions

**XML Structure:**
- `<document-id>` elements may have `format` and `load-source` attributes
- Multiple containing `application-reference` elements may be present, the output will contain the `<doc-number>` values from all
- Each `<document-id>` may contain a `<doc-number>` child element
- Attribute matching is case-insensitive

**Data Handling:**
- Empty or whitespace-only doc-numbers are skipped
- Duplicates are preserved (not deduplicated)
- Whitespace is trimmed from doc-number values

**Input Detection:**
- Allows for both XML strings and file paths as input, automatically detecting which based off of starting character `<`
- Files are assumed to be UTF-8 encoded

**Error Handling:**
- Malformed XML raises `XMLParsingError`
- Missing/unreadable files raise `FileReadError`
- Both exceptions include descriptive error messages

## Project Structure

```
├── extract_doc_numbers.py       # Main module
├── test_extract_doc_numbers.py  # Test suite
├── sample_patent.xml            # Sample input file
├── test_data/                   # Additional test files
├── pyproject.toml              # Project config (uv/pytest)
└── README.md                   # This file
```