"""
Test suite for extract_doc_numbers module.

Tests verify:
- Correct priority ordering (format="epo" and load-source="patent-office")
- Error handling for malformed XML and missing files
- Edge cases (empty values, whitespace, missing attributes)
"""

import pytest
from pathlib import Path
from extract_doc_numbers import extract_doc_numbers, XMLParsingError, FileReadError


class TestPriorityOrdering:
    """Test correct priority ordering based on format and load-source attributes."""

    def test_sample_patent_xml(self):
        """Test the provided sample with format=epo and load-source=patent-office."""
        xml = """
        <root>
          <application-reference>
            <document-id format="epo" load-source="docdb">
              <doc-number>999000888</doc-number>
            </document-id>
            <document-id format="original" load-source="patent-office">
              <doc-number>66667777</doc-number>
            </document-id>
          </application-reference>
        </root>
        """
        result = extract_doc_numbers(xml)
        # format=epo first (priority 2), then load-source=patent-office (priority 3)
        assert result == ['999000888', '66667777']

    def test_all_priority_levels(self):
        """Test all four priority levels."""
        xml = """
        <root>
          <document-id format="other" load-source="other">
            <doc-number>P4</doc-number>
          </document-id>
          <document-id format="epo" load-source="patent-office">
            <doc-number>P1</doc-number>
          </document-id>
          <document-id format="epo" load-source="docdb">
            <doc-number>P2</doc-number>
          </document-id>
          <document-id format="original" load-source="patent-office">
            <doc-number>P3</doc-number>
          </document-id>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['P1', 'P2', 'P3', 'P4']

    def test_priority_1_both_attributes(self):
        """Test priority 1: format=epo AND load-source=patent-office."""
        xml = """
        <root>
          <document-id format="epo" load-source="docdb">
            <doc-number>SECOND</doc-number>
          </document-id>
          <document-id format="epo" load-source="patent-office">
            <doc-number>FIRST</doc-number>
          </document-id>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['FIRST', 'SECOND']

    def test_priority_2_epo_only(self):
        """Test priority 2: format=epo without patent-office."""
        xml = """
        <root>
          <document-id format="original">
            <doc-number>LAST</doc-number>
          </document-id>
          <document-id format="epo">
            <doc-number>FIRST</doc-number>
          </document-id>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['FIRST', 'LAST']

    def test_priority_3_patent_office_only(self):
        """Test priority 3: load-source=patent-office without epo."""
        xml = """
        <root>
          <document-id load-source="other">
            <doc-number>LAST</doc-number>
          </document-id>
          <document-id load-source="patent-office">
            <doc-number>FIRST</doc-number>
          </document-id>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['FIRST', 'LAST']

    def test_document_order_within_priority(self):
        """Test that document order is preserved within same priority."""
        xml = """
        <root>
          <document-id format="epo">
            <doc-number>EPO1</doc-number>
          </document-id>
          <document-id format="epo">
            <doc-number>EPO2</doc-number>
          </document-id>
          <document-id format="epo">
            <doc-number>EPO3</doc-number>
          </document-id>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['EPO1', 'EPO2', 'EPO3']

    def test_case_insensitive_attributes(self):
        """Test that attribute matching is case-insensitive."""
        xml = """
        <root>
          <document-id format="EPO" load-source="PATENT-OFFICE">
            <doc-number>TEST</doc-number>
          </document-id>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['TEST']


class TestBasicExtraction:
    """Test basic extraction functionality."""

    def test_extract_from_file(self):
        """Test extraction from file path."""
        result = extract_doc_numbers('sample_patent.xml')
        assert len(result) == 2
        assert '999000888' in result
        assert '66667777' in result

    def test_single_doc_number(self):
        """Test single doc-number extraction."""
        xml = '<root><document-id><doc-number>12345</doc-number></document-id></root>'
        result = extract_doc_numbers(xml)
        assert result == ['12345']

    def test_no_doc_numbers(self):
        """Test XML with no doc-numbers."""
        xml = '<root><document-id><country>US</country></document-id></root>'
        result = extract_doc_numbers(xml)
        assert result == []

    def test_empty_xml(self):
        """Test empty XML."""
        xml = '<root></root>'
        result = extract_doc_numbers(xml)
        assert result == []


class TestEdgeCases:
    """Test edge cases and data quality issues."""

    def test_empty_doc_number(self):
        """Test empty doc-number is skipped."""
        xml = """
        <root>
          <document-id><doc-number></doc-number></document-id>
          <document-id><doc-number>VALID</doc-number></document-id>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['VALID']

    def test_whitespace_only_doc_number(self):
        """Test whitespace-only doc-number is skipped."""
        xml = """
        <root>
          <document-id><doc-number>   </doc-number></document-id>
          <document-id><doc-number>VALID</doc-number></document-id>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['VALID']

    def test_whitespace_trimmed(self):
        """Test leading/trailing whitespace is trimmed."""
        xml = '<root><document-id><doc-number>  12345  </doc-number></document-id></root>'
        result = extract_doc_numbers(xml)
        assert result == ['12345']

    def test_missing_attributes(self):
        """Test missing format and load-source attributes."""
        xml = """
        <root>
          <document-id format="epo">
            <doc-number>FIRST</doc-number>
          </document-id>
          <document-id>
            <doc-number>LAST</doc-number>
          </document-id>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['FIRST', 'LAST']

    def test_duplicates_not_removed(self):
        """Test duplicate doc-numbers are preserved."""
        xml = """
        <root>
          <document-id><doc-number>12345</doc-number></document-id>
          <document-id><doc-number>12345</doc-number></document-id>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['12345', '12345']


class TestErrorHandling:
    """Test error handling."""

    def test_malformed_xml(self):
        """Test malformed XML raises XMLParsingError."""
        xml = '<root><document-id><doc-number>12345</root>'
        with pytest.raises(XMLParsingError):
            extract_doc_numbers(xml)

    def test_invalid_xml(self):
        """Test invalid XML content."""
        with pytest.raises(XMLParsingError):
            extract_doc_numbers('This is not XML')

    def test_nonexistent_file(self):
        """Test nonexistent file raises FileReadError."""
        with pytest.raises(FileReadError, match="not found"):
            extract_doc_numbers('nonexistent.xml')

    def test_directory_instead_of_file(self):
        """Test directory path raises FileReadError."""
        with pytest.raises(FileReadError):
            extract_doc_numbers('test_data')


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_nested_structure(self):
        """Test deeply nested XML."""
        xml = """
        <root>
          <level1>
            <level2>
              <document-id format="epo">
                <doc-number>NESTED</doc-number>
              </document-id>
            </level2>
          </level1>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['NESTED']

    def test_multiple_application_references(self):
        """Test multiple application-reference elements."""
        xml = """
        <root>
          <application-reference>
            <document-id load-source="patent-office">
              <doc-number>P3-1</doc-number>
            </document-id>
            <document-id format="epo">
              <doc-number>P2-1</doc-number>
            </document-id>
          </application-reference>
          <application-reference>
            <document-id format="epo" load-source="patent-office">
              <doc-number>P1-1</doc-number>
            </document-id>
            <document-id>
              <doc-number>P4-1</doc-number>
            </document-id>
          </application-reference>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['P1-1', 'P2-1', 'P3-1', 'P4-1']

    def test_full_patent_metadata(self):
        """Test realistic patent XML with all metadata."""
        xml = """
        <root>
          <patent-info>
            <application-reference ucid="US-12345678-A">
              <document-id mxw-id="ABC123" load-source="docdb" format="epo">
                <country>US</country>
                <doc-number>999000888</doc-number>
                <kind>A</kind>
                <date>20051213</date>
              </document-id>
              <document-id mxw-id="XYZ789" load-source="patent-office" format="original">
                <country>US</country>
                <doc-number>66667777</doc-number>
              </document-id>
            </application-reference>
          </patent-info>
        </root>
        """
        result = extract_doc_numbers(xml)
        assert result == ['999000888', '66667777']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
