# Copyright 2024 Adam McArthur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json
import os
import tempfile
import unittest
from io import BytesIO
from unittest.mock import MagicMock, mock_open, patch

from radstract.visuals.report_generator import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    """Test cases for the ReportGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.generator = ReportGenerator(title="Test Report")
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test method."""
        # Clean up temporary files
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

        try:
            os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"Error removing temp directory {self.temp_dir}: {e}")

    def test_init_default_values(self):
        """Test ReportGenerator initialization with default values."""
        generator = ReportGenerator()

        self.assertEqual(generator.title, "Generated Report")
        self.assertEqual(generator.accent_color, "#00bbff")
        self.assertEqual(generator.header_color, "#2a2a2a")
        self.assertEqual(generator.page_color, "#0f0f0f")
        self.assertEqual(generator.background_color, "#1f1f1f")
        self.assertEqual(generator.background_color_light, "#404040")
        self.assertEqual(generator.text_color, "#ffffff")
        self.assertEqual(generator.border_color, "#696969")
        self.assertEqual(generator.text_color_light, "#9c9c9c")
        self.assertEqual(generator.footer_color, "#2a2a2a")
        self.assertIsNone(generator.footer_text)
        self.assertIsNone(generator.footer_website)
        self.assertIsNone(generator.footer_email)
        self.assertIsNone(generator.logo_path)
        self.assertEqual(generator.content_sections, [])
        self.assertEqual(generator._attachments, [])
        self.assertFalse(generator.first_subtitle_made)

    def test_init_custom_values(self):
        """Test ReportGenerator initialization with custom values."""
        generator = ReportGenerator(
            title="Custom Report",
            accent_color="#ff0000",
            header_color="#000000",
            page_color="#ffffff",
            background_color="#f0f0f0",
            background_color_light="#e0e0e0",
            text_color="#000000",
            border_color="#cccccc",
            text_color_light="#666666",
            footer_color="#000000",
            footer_text="Custom Footer",
            footer_website="https://example.com",
            footer_email="test@example.com",
            logo_path="/path/to/logo.png",
        )

        self.assertEqual(generator.title, "Custom Report")
        self.assertEqual(generator.accent_color, "#ff0000")
        self.assertEqual(generator.header_color, "#000000")
        self.assertEqual(generator.page_color, "#ffffff")
        self.assertEqual(generator.background_color, "#f0f0f0")
        self.assertEqual(generator.background_color_light, "#e0e0e0")
        self.assertEqual(generator.text_color, "#000000")
        self.assertEqual(generator.border_color, "#cccccc")
        self.assertEqual(generator.text_color_light, "#666666")
        self.assertEqual(generator.footer_color, "#000000")
        self.assertEqual(generator.footer_text, "Custom Footer")
        self.assertEqual(generator.footer_website, "https://example.com")
        self.assertEqual(generator.footer_email, "test@example.com")
        self.assertEqual(generator.logo_path, "/path/to/logo.png")

    def test_add_subtitle_first(self):
        """Test adding the first subtitle."""
        result = self.generator.add_subtitle("Test Subtitle")

        self.assertIs(result, self.generator)  # Test method chaining
        self.assertEqual(len(self.generator.content_sections), 1)
        self.assertEqual(
            self.generator.content_sections[0]["type"], "subtitle"
        )
        self.assertIn(
            "Test Subtitle", self.generator.content_sections[0]["content"]
        )
        self.assertTrue(self.generator.first_subtitle_made)

    def test_add_subtitle_subsequent(self):
        """Test adding subsequent subtitles."""
        self.generator.add_subtitle("First Subtitle")
        result = self.generator.add_subtitle("Second Subtitle")

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 2)
        self.assertIn(
            "margin: 15px 0 10px 0",
            self.generator.content_sections[1]["content"],
        )

    def test_add_subtitle_level_boundaries(self):
        """Test subtitle level boundaries."""
        # Test level below minimum (should be clamped to 1)
        self.generator.add_subtitle("Level 0", level=0)
        self.assertIn("h1", self.generator.content_sections[0]["content"])

        # Test level above maximum (should be clamped to 6)
        self.generator.add_subtitle("Level 10", level=10)
        self.assertIn("h6", self.generator.content_sections[1]["content"])

    def test_add_paragraph(self):
        """Test adding a paragraph."""
        result = self.generator.add_paragraph("Test paragraph text")

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 1)
        self.assertEqual(
            self.generator.content_sections[0]["type"], "paragraph"
        )
        self.assertIn(
            "Test paragraph text",
            self.generator.content_sections[0]["content"],
        )

    def test_add_table_with_headers(self):
        """Test adding a table with headers."""
        data = [["Row1Col1", "Row1Col2"], ["Row2Col1", "Row2Col2"]]
        headers = ["Header1", "Header2"]

        result = self.generator.add_table(data, headers)

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 1)
        self.assertEqual(self.generator.content_sections[0]["type"], "table")
        content = self.generator.content_sections[0]["content"]

        # Check that headers are present
        self.assertIn("Header1", content)
        self.assertIn("Header2", content)
        # Check that data is present
        self.assertIn("Row1Col1", content)
        self.assertIn("Row2Col2", content)

    def test_add_table_without_headers(self):
        """Test adding a table without headers."""
        data = [["Row1Col1", "Row1Col2"], ["Row2Col1", "Row2Col2"]]

        result = self.generator.add_table(data)

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 1)
        self.assertEqual(self.generator.content_sections[0]["type"], "table")
        content = self.generator.content_sections[0]["content"]

        # Check that data is present but no thead
        self.assertIn("Row1Col1", content)
        self.assertIn("Row2Col2", content)
        self.assertNotIn("<thead>", content)

    def test_add_highlights_success(self):
        """Test adding highlights with success status."""
        result = self.generator.add_highlights(
            report_success=True,
            highlight1="Test Analysis",
            highlight2="High Quality",
            highlight1_label="Analysis Type",
            highlight2_label="Data Quality",
        )

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 1)
        self.assertEqual(
            self.generator.content_sections[0]["type"], "highlights"
        )
        content = self.generator.content_sections[0]["content"]

        # Check for success indicator
        self.assertIn("✓", content)
        self.assertIn("Success", content)
        # Check for highlights
        self.assertIn("Test Analysis", content)
        self.assertIn("High Quality", content)

    def test_add_highlights_failure(self):
        """Test adding highlights with failure status."""
        result = self.generator.add_highlights(
            report_success=False,
            highlight1="Failed Analysis",
            highlight2="Low Quality",
        )

        self.assertIs(result, self.generator)
        content = self.generator.content_sections[0]["content"]

        # Check for failure indicator
        self.assertIn("✗", content)
        self.assertIn("Failed", content)

    def test_add_highlights_partial(self):
        """Test adding highlights with only some values."""
        result = self.generator.add_highlights(
            report_success=True, highlight1="Only First"
        )

        self.assertIs(result, self.generator)
        content = self.generator.content_sections[0]["content"]

        self.assertIn("Only First", content)
        # Should still have success indicator
        self.assertIn("Success", content)

    @patch(
        "builtins.open", new_callable=mock_open, read_data=b"fake_image_data"
    )
    def test_add_image_success(self, mock_file):
        """Test adding an image successfully."""
        result = self.generator.add_image(
            image_path="test.png", caption="Test Caption", max_width="75%"
        )

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 1)
        self.assertEqual(self.generator.content_sections[0]["type"], "image")
        content = self.generator.content_sections[0]["content"]

        # Check for image and caption
        self.assertIn("data:image/png;base64,", content)
        self.assertIn("Test Caption", content)
        self.assertIn("max-width: 75%", content)

    def test_add_image_error(self):
        """Test adding an image with file error."""
        result = self.generator.add_image("nonexistent.png")

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 1)
        self.assertEqual(
            self.generator.content_sections[0]["type"], "paragraph"
        )
        content = self.generator.content_sections[0]["content"]

        # Should contain error message
        self.assertIn("Error loading image", content)
        self.assertIn("nonexistent.png", content)

    @patch(
        "builtins.open", new_callable=mock_open, read_data=b"fake_video_data"
    )
    def test_add_video_success(self, mock_file):
        """Test adding a video successfully."""
        result = self.generator.add_video(
            video_path="test.mp4", caption="Test Video Caption"
        )

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 1)
        self.assertEqual(self.generator.content_sections[0]["type"], "video")
        content = self.generator.content_sections[0]["content"]

        # Check for video and caption
        self.assertIn("data:video/mp4;base64,", content)
        self.assertIn("Test Video Caption", content)

    def test_add_video_error(self):
        """Test adding a video with file error."""
        result = self.generator.add_video("nonexistent.mp4")

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 1)
        self.assertEqual(self.generator.content_sections[0]["type"], "video")
        content = self.generator.content_sections[0]["content"]

        # Should contain placeholder content
        self.assertIn("🎥 Video Content", content)
        self.assertIn("nonexistent.mp4", content)

    def test_add_json_dict(self):
        """Test adding JSON data as dictionary."""
        data = {"key1": "value1", "key2": {"nested": "value2"}}

        result = self.generator.add_json(data, title="Test JSON")

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 1)
        self.assertEqual(self.generator.content_sections[0]["type"], "json")
        content = self.generator.content_sections[0]["content"]

        # Check for title and JSON content
        self.assertIn("Test JSON", content)
        self.assertIn("key1", content)
        self.assertIn("value1", content)

    def test_add_json_list(self):
        """Test adding JSON data as list."""
        data = ["item1", "item2", {"key": "value"}]

        result = self.generator.add_json(data)

        self.assertIs(result, self.generator)
        content = self.generator.content_sections[0]["content"]

        # Check for JSON content
        self.assertIn("item1", content)
        self.assertIn("item2", content)

    def test_generate_html_basic(self):
        """Test basic HTML generation."""
        self.generator.add_subtitle("Test Title")
        self.generator.add_paragraph("Test paragraph")

        html = self.generator.generate_html()

        # Check basic structure
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html>", html)
        self.assertIn("<head>", html)
        self.assertIn("<body>", html)
        self.assertIn("Test Report", html)  # Title
        self.assertIn("Test Title", html)  # Subtitle
        self.assertIn("Test paragraph", html)  # Paragraph

    def test_generate_html_hide_videos(self):
        """Test HTML generation with videos hidden."""
        self.generator.add_paragraph("Regular content")
        self.generator.add_video("test.mp4")
        self.generator.add_paragraph("More content")

        html = self.generator.generate_html(hide_videos=True)

        # Should contain regular content but not video
        self.assertIn("Regular content", html)
        self.assertIn("More content", html)
        self.assertNotIn("🎥 Video Content", html)

    def test_generate_html_with_attachments(self):
        """Test HTML generation with attachments."""
        self.generator.add_attachment("test.txt", "Test attachment")
        self.generator.add_paragraph("Content")

        html = self.generator.generate_html(hide_attachments=False)

        # Should contain attachment information
        self.assertIn("Attachments", html)
        self.assertIn("test.txt", html)
        self.assertIn("Test attachment", html)

    def test_generate_html_hide_attachments(self):
        """Test HTML generation with attachments hidden."""
        self.generator.add_attachment("test.txt", "Test attachment")
        self.generator.add_paragraph("Content")

        html = self.generator.generate_html(hide_attachments=True)

        # Should not contain attachment information
        self.assertNotIn("Attachments", html)
        self.assertNotIn("test.txt", html)

    def test_save_html(self):
        """Test saving HTML to file."""
        self.generator.add_paragraph("Test content")

        output_path = os.path.join(self.temp_dir, "test.html")
        result = self.generator.save_html(output_path)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))

        # Check file content
        with open(output_path, "r") as f:
            content = f.read()
            self.assertIn("Test content", content)

    @patch("radstract.visuals.report_generator.HTML")
    def test_save_pdf_success(self, mock_html):
        """Test successful PDF generation."""
        # Mock the HTML object and its write_pdf method
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance

        self.generator.add_paragraph("Test content")
        output_path = os.path.join(self.temp_dir, "test.pdf")

        result = self.generator.save_pdf(output_path)

        self.assertTrue(result)
        mock_html.assert_called_once()
        mock_html_instance.write_pdf.assert_called_once_with(output_path)

    @patch("radstract.visuals.report_generator.HTML")
    def test_save_pdf_with_attachments(self, mock_html):
        """Test PDF generation with attachments."""
        # Create a temporary file for attachment
        attachment_path = os.path.join(self.temp_dir, "attachment.txt")
        with open(attachment_path, "w") as f:
            f.write("test attachment content")

        # Mock the HTML object and its write_pdf method
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance

        self.generator.add_attachment(attachment_path, "Test attachment")
        self.generator.add_paragraph("Test content")
        output_path = os.path.join(self.temp_dir, "test.pdf")

        result = self.generator.save_pdf(output_path)

        self.assertTrue(result)
        mock_html_instance.write_pdf.assert_called_once()
        # Check that attachments were passed
        call_args = mock_html_instance.write_pdf.call_args
        self.assertIn("attachments", call_args[1])

    @patch("radstract.visuals.report_generator.HTML")
    def test_save_pdf_error(self, mock_html):
        """Test PDF generation with error."""
        # Mock the HTML object to raise an exception
        mock_html.side_effect = Exception("PDF generation failed")

        self.generator.add_paragraph("Test content")
        output_path = os.path.join(self.temp_dir, "test.pdf")

        result = self.generator.save_pdf(output_path)

        self.assertFalse(result)

    @patch("radstract.visuals.report_generator.HTML")
    def test_get_pdf_bytes_success(self, mock_html):
        """Test getting PDF as bytes."""
        # Mock the HTML object and its write_pdf method
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance
        mock_html_instance.write_pdf.return_value = b"fake_pdf_bytes"

        self.generator.add_paragraph("Test content")

        result = self.generator.get_pdf_bytes()

        self.assertEqual(result, b"fake_pdf_bytes")
        mock_html_instance.write_pdf.assert_called_once()

    @patch("radstract.visuals.report_generator.HTML")
    def test_get_pdf_bytes_error(self, mock_html):
        """Test getting PDF bytes with error."""
        # Mock the HTML object to raise an exception
        mock_html.side_effect = Exception("PDF generation failed")

        self.generator.add_paragraph("Test content")

        result = self.generator.get_pdf_bytes()

        self.assertIsNone(result)

    def test_clear(self):
        """Test clearing all content and attachments."""
        self.generator.add_paragraph("Test content")
        self.generator.add_attachment("test.txt", "Test attachment")

        result = self.generator.clear()

        self.assertIs(result, self.generator)
        self.assertEqual(self.generator.content_sections, [])
        self.assertEqual(self.generator._attachments, [])

    def test_add_attachment(self):
        """Test adding an attachment."""
        result = self.generator.add_attachment("test.txt", "Test description")

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator._attachments), 1)
        self.assertEqual(
            self.generator._attachments[0], ("test.txt", "Test description")
        )

    def test_add_attachment_no_description(self):
        """Test adding an attachment without description."""
        result = self.generator.add_attachment("test.txt")

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator._attachments), 1)
        self.assertEqual(self.generator._attachments[0], ("test.txt", None))

    def test_clear_attachments(self):
        """Test clearing attachments."""
        self.generator.add_attachment("test1.txt", "Description 1")
        self.generator.add_attachment("test2.txt", "Description 2")

        result = self.generator.clear_attachments()

        self.assertIs(result, self.generator)
        self.assertEqual(self.generator._attachments, [])

    def test_method_chaining(self):
        """Test that all methods support method chaining."""
        result = (
            self.generator.add_subtitle("Title")
            .add_paragraph("Paragraph")
            .add_table([["data"]], ["header"])
            .add_highlights(True, "test", "test2")
            .add_json({"key": "value"})
            .add_attachment("test.txt")
        )

        self.assertIs(result, self.generator)
        self.assertEqual(len(self.generator.content_sections), 5)
        self.assertEqual(len(self.generator._attachments), 1)

    def test_html_structure_with_logo(self):
        """Test HTML generation with logo."""
        # Create a temporary logo file
        logo_path = os.path.join(self.temp_dir, "logo.png")
        with open(logo_path, "wb") as f:
            f.write(b"fake_logo_data")

        generator = ReportGenerator(title="Test Report", logo_path=logo_path)
        generator.add_paragraph("Test content")

        html = generator.generate_html()

        # Should contain logo data
        self.assertIn("data:image/png;base64,", html)

    def test_html_structure_with_footer(self):
        """Test HTML generation with footer content."""
        generator = ReportGenerator(
            title="Test Report",
            footer_text="Footer Text",
            footer_website="https://example.com",
            footer_email="test@example.com",
        )
        generator.add_paragraph("Test content")

        html = generator.generate_html()

        # Should contain footer content
        self.assertIn("Footer Text", html)
        self.assertIn("https://example.com", html)
        self.assertIn("test@example.com", html)


if __name__ == "__main__":
    unittest.main()
