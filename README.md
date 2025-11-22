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
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Set up project
uv venv
uv pip install -e ".[dev]"

# Activate venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

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
- Allows for both XML strings and file paths as input, automatically detecting which using the following rules
  - Strings starting with `<` are treated as XML content
  - Existing file paths are read as files
  - Strings ending in `.xml` or `.txt` or containing `/` or `\` are treated as file paths
- Files are assumed to be UTF-8 encoded

**Error Handling:**
- Malformed XML raises `XMLParsingError`
- Missing/unreadable files raise `FileReadError`
- Both exceptions include descriptive error messages

## Project Structure

```
├── extract_doc_numbers.py       # Main module (~145 lines)
├── test_extract_doc_numbers.py  # Test suite (23 tests)
├── sample_patent.xml            # Sample input file
├── test_data/                   # Additional test files
├── pyproject.toml              # Project config (uv/pytest)
└── README.md                   # This file
```

## Examples

### All Priority Levels

```python
xml = """
<root>
  <document-id format="epo" load-source="patent-office">
    <doc-number>P1</doc-number>  <!-- Priority 1 -->
  </document-id>
  <document-id format="epo">
    <doc-number>P2</doc-number>  <!-- Priority 2 -->
  </document-id>
  <document-id load-source="patent-office">
    <doc-number>P3</doc-number>  <!-- Priority 3 -->
  </document-id>
  <document-id>
    <doc-number>P4</doc-number>  <!-- Priority 4 -->
  </document-id>
</root>
"""
extract_doc_numbers(xml)  # ['P1', 'P2', 'P3', 'P4']
```

### Error Handling

```python
from extract_doc_numbers import extract_doc_numbers, XMLParsingError, FileReadError

try:
    doc_numbers = extract_doc_numbers('missing.xml')
except FileReadError as e:
    print(f"File error: {e}")

try:
    doc_numbers = extract_doc_numbers('<invalid>xml')
except XMLParsingError as e:
    print(f"Parse error: {e}")
```

## Design Decisions

**Simplicity:** Standard library only (xml.etree.ElementTree) - no external dependencies for core functionality.

**Priority Logic:** Simple integer priorities (1-4) with tuple sorting make the logic clear and maintainable.

**Input Flexibility:** Supports both file paths and XML strings without requiring explicit flags.

**Production Ready:** Logging, custom exceptions, comprehensive tests, and proper error messages.

## Author

Cypris Data Engineer Challenge - 2025
