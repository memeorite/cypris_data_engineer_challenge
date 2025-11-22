"""
XML Document Number Extraction Module

Extracts doc-number values from patent XML documents with priority-based ordering.

PRIORITY ORDER:
1. format="epo" AND load-source="patent-office" (both attributes)
2. format="epo" only
3. load-source="patent-office" only
4. All others

ASSUMPTIONS:
- XML contains <document-id> elements with optional 'format' and 'load-source' attributes
- Each <document-id> may contain a <doc-number> child with text content
- Empty or whitespace-only doc-numbers are skipped
- Document order is preserved within each priority group
- Duplicates are not removed
- Input can be a file path or XML string (detected by checking if file exists or starts with '<')
- Files are UTF-8 encoded
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple, Union


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class XMLParsingError(Exception):
    """Raised when XML cannot be parsed."""
    pass


class FileReadError(Exception):
    """Raised when file cannot be read."""
    pass

class FileNotFound(Exception):
    """Raised when file cannot be read."""
    pass

def _get_priority(format_attr: str, load_source_attr: str) -> int:
    """
    Determine priority based on format and load-source attributes.

    Returns:
        1: format="epo" AND load-source="patent-office"
        2: format="epo" only
        3: load-source="patent-office" only
        4: everything else
    """
    has_epo = format_attr == "epo"
    has_patent_office = load_source_attr == "patent-office"

    if has_epo and has_patent_office:
        return 1
    elif has_epo:
        return 2
    elif has_patent_office:
        return 3
    else:
        return 4


def extract_doc_numbers(source: Union[str, Path]) -> List[str]:
    """
    Extract doc-number values from patent XML in priority order.

    Args:
        source: File path or XML content string

    Returns:
        List of doc-number values ordered by priority

    Raises:
        FileReadError: If file cannot be read
        XMLParsingError: If XML is malformed
    """
    # Read XML content
    source_str = str(source)
    path = Path(source_str)

    if source_str.strip().startswith('<'):
        xml_content = source_str
    elif path.exists():
        try:
            xml_content = path.read_text(encoding='utf-8')
            logger.info(f"Read file: {source}")
        except Exception as e:
            raise FileReadError(f"Failed to read {source}: {e}") from e
    else:
        raise ValueError("Input must be either the path to an existing file or an XML string starting with '<'.")

    # Parse XML
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise XMLParsingError(f"Invalid XML: {e}") from e

    # Extract doc-numbers with priorities
    entries: List[Tuple[int, str]] = []  # (priority, doc_number)

    for doc_id in root.findall('.//document-id'):
        format_attr = doc_id.get('format', '').lower()
        load_source_attr = doc_id.get('load-source', '').lower()

        doc_num_elem = doc_id.find('doc-number')
        if doc_num_elem is None or not doc_num_elem.text:
            continue

        doc_number = doc_num_elem.text.strip()
        if not doc_number:
            continue

        priority = _get_priority(format_attr, load_source_attr)
        entries.append((priority, doc_number))

    # Sort by priority and extract doc-numbers
    entries.sort(key=lambda x: x[0])
    return [doc_num for _, doc_num in entries]


def main():
    """Command-line interface."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extract_doc_numbers.py <xml_file>")
        sys.exit(1)

    try:
        doc_numbers = extract_doc_numbers(sys.argv[1])
        print(f"\nExtracted {len(doc_numbers)} doc-number(s):")
        print("-" * 40)
        for i, doc_num in enumerate(doc_numbers, 1):
            print(f"{i}. {doc_num}")
    except (FileReadError, XMLParsingError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
