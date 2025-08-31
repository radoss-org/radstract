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
import io
import json
import os
import random
import re
from datetime import datetime
from typing import Dict, List, Optional, Union

import pydicom
from pydicom.uid import generate_uid
from weasyprint import HTML, Attachment

from ..data.dicom.utils import Modalities
from .report_utils import (
    create_attachment_info,
    create_highlight_box,
    generate_css_styles,
)


class ReportGenerator:
    """
    A minimal report generator using WeasyPrint.

    Build PDFs or HTML Files by calling methods in sequence - the order of method calls
    determines the order of content in the final PDF or HTML file.
    """

    def __init__(
        self,
        title: str = "Generated Report",
        accent_color: str = "#00bbff",
        header_color: str = "#2a2a2a",
        page_color: str = "#0f0f0f",
        background_color: str = "#1f1f1f",
        background_color_light: str = "#404040",
        text_color: str = "#ffffff",
        border_color: str = "#696969",
        text_color_light: str = "#9c9c9c",
        footer_color: str = "#2a2a2a",
        footer_text: Optional[str] = None,
        footer_website: Optional[str] = None,
        footer_email: Optional[str] = None,
        logo_path: Optional[str] = None,
    ):
        """
        Initialize the generator with comprehensive color scheme.

        :param title: Title of the report (default: "Generated Report")
        :param accent_color: Primary accent color for headings and highlights (default: bright blue)
        :param header_color: Color for the header background (default: dark gray)
        :param page_color: Main background color (default: dark gray)
        :param background_color: Main background color (default: dark gray)
        :param background_color_light: Light alternating row color for tables (default: medium gray)
        :param text_color: Primary text color (default: white)
        :param border_color: Color for borders (default: gray)
        :param footer_color: Color for the footer background (default: dark gray)
        :param footer_text: Optional text to display in the footer
        :param footer_website: Optional website URL to link in the footer
        :param footer_email: Optional email address to link in the footer
        :param logo_path: Optional path to logo image file
        """
        self.title = title
        self.accent_color = accent_color
        self.header_color = header_color
        self.background_color = background_color
        self.text_color = text_color
        self.page_color = page_color
        self.background_color_light = background_color_light
        self.border_color = border_color
        self.text_color_light = text_color_light
        self.footer_color = footer_color
        self.footer_text = footer_text
        self.footer_website = footer_website
        self.footer_email = footer_email
        self.logo_path = logo_path
        self.content_sections = []
        self._attachments = []
        self.first_subtitle_made = False

    def _add_content_section(
        self, section_type: str, content: str
    ) -> "ReportGenerator":
        """Helper method to add content sections."""
        self.content_sections.append(
            {"type": section_type, "content": content}
        )
        return self

    def add_subtitle(self, text: str, level: int = 2) -> "ReportGenerator":
        """
        Add a subtitle/heading to the report.

        :param text: Text of the subtitle
        :param level: Level of the subtitle (1-6)
        """
        margin_top = "0px" if not self.first_subtitle_made else "15px"
        self.first_subtitle_made = True

        tag = f"h{min(max(level, 1), 6)}"
        font_size = 20 - (level - 2) * 2

        content = f'<{tag} style="color: {self.accent_color}; font-family: Arial Black, Arial, sans-serif; font-size: {font_size}px; margin: {margin_top} 0 10px 0; border-bottom: 2px solid {self.accent_color}; padding-bottom: 5px;">{text}</{tag}>'

        return self._add_content_section("subtitle", content)

    def _make_links_clickable(self, text: str) -> str:
        """Convert URLs in text to clickable HTML links."""
        # Simple URL regex pattern
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'

        def replace_url(match):
            url = match.group(0)
            if url.startswith("www."):
                url = "https://" + url
            return f'<a href="{url}" style="color: {self.accent_color}; text-decoration: underline;" target="_blank">{match.group(0)}</a>'

        return re.sub(url_pattern, replace_url, text)

    def add_paragraph(self, text: str) -> "ReportGenerator":
        """
        Add a paragraph of text to the report.

        :param text: Text of the paragraph
        """
        text_with_links = self._make_links_clickable(text)
        content = f'<p style="color: {self.text_color}; font-family: Arial, sans-serif; margin: 10px 0; line-height: 1.4;">{text_with_links}</p>'
        return self._add_content_section("paragraph", content)

    def add_warning(self, text: str) -> "ReportGenerator":
        """
        Add warning text to the report in accent color and bold.

        :param text: Warning text to display
        """
        text_with_links = self._make_links_clickable(text)
        content = f'<p style="color: {self.accent_color}; font-family: Arial, sans-serif; font-weight: bold; margin: 10px 0; line-height: 1.4;">⚠ {text_with_links}</p>'
        return self._add_content_section("warning", content)

    def add_table(
        self, data: List[List[str]], headers: Optional[List[str]] = None
    ) -> "ReportGenerator":
        """
        Add a table to the report.

        :param data: List of lists of strings
        :param headers: List of strings for the headers
        """
        table_html = f'<table style="width: 100%; border-collapse: collapse; margin: 15px 0; border: 1px solid {self.border_color};">'

        # Add headers if provided
        if headers:
            table_html += "<thead><tr>"
            for header in headers:
                table_html += f'<th style="background-color: {self.accent_color}; color: black; padding: 10px; text-align: center; font-weight: bold; border: 1px solid {self.border_color};">{header}</th>'
            table_html += "</tr></thead>"

        # Add data rows
        table_html += "<tbody>"
        for i, row in enumerate(data):
            bg_color = (
                self.background_color_light
                if i % 2 == 0
                else self.background_color
            )
            table_html += "<tr>"
            for cell in row:
                table_html += f'<td style="padding: 8px; text-align: center; border: 1px solid {self.border_color}; background-color: {bg_color}; color: {self.text_color};">{cell}</td>'
            table_html += "</tr>"
        table_html += "</tbody></table>"

        return self._add_content_section("table", table_html)

    def add_highlights(
        self,
        report_success: Optional[bool] = True,
        status_text: Optional[str] = None,
        highlight1: Optional[str] = None,
        highlight2: Optional[str] = None,
        highlight1_label: str = "Analysis Type",
        highlight2_label: str = "Data Quality",
    ) -> "ReportGenerator":
        """
        Add a highlights section with success/failure indicator and additional highlights.

        :param report_success: Whether the report generation was successful (True/False/None)
        :param status_text: Custom text to display for the status (overrides default text)
        :param highlight1: First additional highlight value
        :param highlight2: Second additional highlight value
        :param highlight1_label: Label for the first highlight
        :param highlight2_label: Label for the second highlight
        """
        # Create highlights container
        highlights_html = f'<div style="background-color: {self.background_color_light}; border-radius: 8px; padding: 12px; margin: 20px 0; border: 1px solid {self.border_color};">'
        highlights_html += f'<h3 style="color: {self.accent_color}; font-family: Arial Black, Arial, sans-serif; font-size: 16px; margin: 3px 0 8px 0; border-bottom: 2px solid {self.accent_color}; padding-bottom: 3px;">Highlights</h3>'
        highlights_html += f'<div style="display: flex; flex-direction: row; gap: 8px; flex-wrap: nowrap; justify-content: center;">'

        # Add success/failure indicator
        if report_success is None:
            success_icon = "⚠"
            display_text = (
                status_text if status_text is not None else "Warning"
            )
            success_color = "#ff8800"
        elif report_success:
            success_icon = "✓"
            display_text = (
                status_text if status_text is not None else "Success"
            )
            success_color = "#00ff00"
        else:
            success_icon = "✗"
            display_text = status_text if status_text is not None else "Failed"
            success_color = "#ff4444"

        highlights_html += create_highlight_box(
            success_icon,
            success_color,
            "Report Status",
            display_text,
            self.background_color,
            self.border_color,
            self.text_color,
            self.text_color_light,
        )

        # Add additional highlights
        if highlight1:
            highlights_html += create_highlight_box(
                "ℹ",
                "#0096ff",
                highlight1_label,
                highlight1,
                self.background_color,
                self.border_color,
                self.text_color,
                self.text_color_light,
            )

        if highlight2:
            highlights_html += create_highlight_box(
                "ℹ",
                "#0096ff",
                highlight2_label,
                highlight2,
                self.background_color,
                self.border_color,
                self.text_color,
                self.text_color_light,
            )

        highlights_html += "</div></div>"
        return self._add_content_section("highlights", highlights_html)

    def add_image(
        self,
        image_path: str,
        caption: Optional[str] = None,
        max_width: str = "50%",
    ) -> "ReportGenerator":
        """
        Add an image to the report.

        :param image_path: Path to the image
        :param caption: Caption for the image
        :param max_width: Maximum width of the image
        """
        try:
            # Read and encode image
            with open(image_path, "rb") as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode("utf-8")

            # Determine image type from file extension
            img_type = image_path.split(".")[-1].lower()
            if img_type == "jpg":
                img_type = "jpeg"

            image_html = f'<div style="text-align: center; margin: 20px 0;">'
            image_html += f'<img src="data:image/{img_type};base64,{img_base64}" style="max-width: {max_width}; height: auto; border-radius: 8px; border: 4px solid {self.border_color};">'

            if caption:
                image_html += f'<p style="color: {self.text_color}; font-style: italic; margin-top: 10px; font-size: 14px;">{caption}</p>'

            image_html += "</div>"

            return self._add_content_section("image", image_html)
        except Exception as e:
            error_content = f'<p style="color: red;">Error loading image {image_path}: {str(e)}</p>'
            return self._add_content_section("paragraph", error_content)

    def add_video(
        self, video_path: str, caption: Optional[str] = None
    ) -> "ReportGenerator":
        """
        Add a video to the report. For HTML output, the video will be embedded. For PDF output, a placeholder will be shown.

        :param video_path: Path to the video
        :param caption: Caption for the video
        """
        try:
            # Read and encode video
            with open(video_path, "rb") as video_file:
                video_data = video_file.read()
                video_base64 = base64.b64encode(video_data).decode("utf-8")

            # Determine video type from file extension
            video_type = video_path.split(".")[-1].lower()
            if video_type == "mp4":
                video_type = "mp4"
            elif video_type == "webm":
                video_type = "webm"
            elif video_type == "ogg":
                video_type = "ogg"
            else:
                video_type = "mp4"  # Default to mp4

            video_html = f'<div style="text-align: center; margin: 20px 0;">'
            video_html += f'<video controls style="max-width: 50%; height: auto; border-radius: 8px; border: 4px solid {self.border_color};">'
            video_html += f'<source src="data:video/{video_type};base64,{video_base64}" type="video/{video_type}">'
            video_html += f"Your browser does not support the video tag. Video file: {video_path}"
            video_html += "</video>"

            if caption:
                video_html += f'<p style="color: {self.text_color}; font-style: italic; margin-top: 10px; font-size: 14px;">{caption}</p>'

            video_html += "</div>"

            return self._add_content_section("video", video_html)
        except Exception as e:
            # Fallback to placeholder if video loading fails
            placeholder_html = f'<div style="text-align: center; margin: 20px 0; padding: 40px; background-color: {self.background_color}; border: 4px dashed {self.accent_color}; border-radius: 8px; max-width: 50%; margin-left: auto; margin-right: auto;">'
            placeholder_html += f'<p style="color: {self.accent_color}; font-size: 18px; margin: 0;">🎥 Video Content</p>'
            placeholder_html += f'<p style="color: {self.text_color}; font-size: 14px; margin: 10px 0 0 0;">{video_path}</p>'
            placeholder_html += f'<p style="color: red; font-size: 12px; margin: 5px 0 0 0;">Error loading video: {str(e)}</p>'

            if caption:
                placeholder_html += f'<p style="color: {self.text_color}; font-style: italic; margin-top: 10px; font-size: 14px;">{caption}</p>'

            placeholder_html += "</div>"
            return self._add_content_section("video", placeholder_html)

    def add_json(
        self, data: Union[Dict, List], title: Optional[str] = None
    ) -> "ReportGenerator":
        """
        Add JSON data as formatted text to the report.

        :param data: Dictionary or list of data
        :param title: Title for the JSON block
        """
        json_html = f'<div style="background-color: {self.background_color_light}; border: 1px solid {self.border_color}; border-radius: 6px; padding: 15px; margin: 15px 0;">'

        if title:
            json_html += f'<h4 style="color: {self.accent_color}; margin: 0 0 10px 0; font-family: Arial Black, Arial, sans-serif;">{title}</h4>'

        json_html += f'<pre style="color: {self.text_color_light}; padding: 10px; font-family: monospace; font-size: 12px; margin: 0; white-space: pre-wrap; background-color: {self.background_color};">{json.dumps(data, indent=2)}</pre>'
        json_html += "</div>"

        return self._add_content_section("json", json_html)

    def add_page_break(self) -> "ReportGenerator":
        """
        Add a page break to the report.
        """
        return self._add_content_section(
            "page_break", "<div style='page-break-after: always;'></div>"
        )

    def _create_header_html(self) -> str:
        """Create the header HTML with logo and title."""
        header_html = '<header><div class="header-content">'

        if self.logo_path:
            try:
                # Read and encode logo
                with open(self.logo_path, "rb") as logo_file:
                    logo_data = logo_file.read()
                    logo_base64 = base64.b64encode(logo_data).decode("utf-8")

                # Determine logo type from file extension
                logo_type = self.logo_path.split(".")[-1].lower()
                if logo_type == "jpg":
                    logo_type = "jpeg"

                header_html += f'<img src="data:image/{logo_type};base64,{logo_base64}" alt="Logo" class="header-logo">'
            except Exception:
                pass  # Skip logo if loading fails

        header_html += f"<h1>{self.title}</h1></div></header>"
        return header_html

    def _create_footer_html(self) -> str:
        """Create the footer HTML with text, website, and email."""
        footer_html = (
            '<footer><table class="footer-table"><tr><td class="footer-left">'
        )

        if self.footer_text:
            footer_html += self.footer_text

        footer_html += '</td><td class="footer-right">'

        if self.footer_website:
            footer_html += f"<div>{self.footer_website}</div>"
        if self.footer_email:
            footer_html += f"<div>{self.footer_email}</div>"

        footer_html += "</td></tr></table></footer>"
        return footer_html

    def generate_html(
        self, hide_videos: bool = False, hide_attachments: bool = False
    ) -> str:
        """
        Generate the complete HTML content.

        :param hide_videos: If True, video sections will be hidden from the output
        :param hide_attachments: If True, attachment information will be hidden from the output
        """
        css_styles = generate_css_styles(
            self.accent_color,
            self.header_color,
            self.page_color,
            self.background_color,
            self.background_color_light,
            self.text_color,
            self.border_color,
            self.text_color_light,
            self.footer_color,
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.title}</title>
            <meta charset="UTF-8">
            <style>
                {css_styles}
            </style>
        </head>
        <body>
            {self._create_header_html()}
            <div class="content-wrapper">
        """

        # Add all content sections, filtering out videos if hide_videos is True
        for section in self.content_sections:
            if hide_videos and section["type"] == "video":
                continue
            html_content += section["content"]

        # Add attachment information if any attachments are present and not hidden
        if self._attachments and not hide_attachments:
            html_content += create_attachment_info(
                self._attachments,
                self.background_color_light,
                self.border_color,
                self.accent_color,
                self.text_color,
                self.text_color_light,
            )

        html_content += """
            </div>
        """
        html_content += self._create_footer_html()
        html_content += """
        </body>
        </html>
        """

        return html_content

    def _create_attachments_list(self) -> List[Attachment]:
        """Create list of WeasyPrint Attachment objects."""
        attachments = []
        for file_path, description in self._attachments:
            with open(file_path, "rb") as f:
                file_obj = io.BytesIO(f.read())
            attachments.append(
                Attachment(
                    name=os.path.basename(file_path),
                    file_obj=file_obj,
                    description=description,
                )
            )
        return attachments

    def save_pdf(self, output_path: str, hide_videos=True) -> bool:
        """
        Save the report as a PDF file.

        :param output_path: Path where to save the PDF file
        """
        try:
            html_content = self.generate_html(hide_videos=hide_videos)
            html_doc = HTML(string=html_content)

            if self._attachments:
                html_doc.write_pdf(
                    output_path, attachments=self._create_attachments_list()
                )
            else:
                html_doc.write_pdf(output_path)

            return True
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return False

    def save_html(self, output_path: str, hide_attachments=True) -> bool:
        """
        Save the report as an HTML file.

        :param output_path: Path where to save the HTML file
        """
        try:
            with open(output_path, "w") as f:
                f.write(self.generate_html(hide_attachments=hide_attachments))
            return True
        except Exception as e:
            print(f"Error saving HTML: {str(e)}")
            return False

    def get_pdf_bytes(self, hide_videos=True) -> Optional[bytes]:
        """
        Get the PDF as bytes instead of saving to file.

        :return: PDF content as bytes, or None if failed
        """
        try:
            html_content = self.generate_html(hide_videos=hide_videos)
            html_doc = HTML(string=html_content)

            if self._attachments:
                pdf_bytes = html_doc.write_pdf(
                    attachments=self._create_attachments_list()
                )
            else:
                pdf_bytes = html_doc.write_pdf()

            return pdf_bytes
        except Exception as e:
            print(f"Error generating PDF bytes: {str(e)}")
            return None

    def save_to_dicom_study(
        self,
        output_path: str,
        dicom_tags: pydicom.Dataset = None,
        series_number: int = 999,
        series_description: str = "PDF Report",
        hide_videos: bool = True,
    ) -> bool:
        """
        Save the report as a DICOM Encapsulated PDF file.

        :param output_path: Path where to save the DICOM file
        :param patient_name: Patient name for the DICOM file
        :param patient_id: Patient ID for the DICOM file
        :param study_description: Study description
        :param series_description: Series description
        :param hide_videos: If True, videos will be hidden from the PDF
        :return: True if successful, False otherwise
        """
        try:
            # Generate PDF bytes
            pdf_bytes = self.get_pdf_bytes(hide_videos=hide_videos)
            if not pdf_bytes:
                return False

            # Create file meta information
            file_meta = pydicom.dataset.FileMetaDataset()
            file_meta.MediaStorageSOPClassUID = (
                Modalities.ENCAPSULATED_PDF.modality
            )
            file_meta.MediaStorageSOPInstanceUID = generate_uid()
            file_meta.ImplementationClassUID = generate_uid()
            file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

            # Create the main dataset
            ds = pydicom.Dataset()
            ds.file_meta = file_meta
            ds.is_little_endian = True
            ds.is_implicit_VR = False

            important_tags_for_transfer = [
                "StudyInstanceUID",
                "StudyID",
                "PatientName",
                "PatientID",
            ]

            for tag in important_tags_for_transfer:
                if tag in dicom_tags:
                    setattr(ds, tag, dicom_tags[tag].value)

            ds.SeriesNumber = series_number
            ds.SeriesDescription = series_description

            # SOP Common Module
            ds.SOPClassUID = Modalities.ENCAPSULATED_PDF.modality
            ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID

            # Encapsulated Document Series Module
            ds.Modality = "DOC"
            ds.SeriesInstanceUID = generate_uid()

            # SC Equipment Module (required for encapsulated documents)
            ds.ConversionType = "WSD"  # Workstation
            ds.SecondaryCaptureDeviceManufacturer = "RADSTRACT"
            ds.SecondaryCaptureDeviceManufacturerModelName = "Report Generator"
            ds.SecondaryCaptureDeviceSoftwareVersions = "1.0"

            # Encapsulated Document Module
            ds.InstanceNumber = random.randint(1, 1000000)
            ds.DocumentTitle = self.title
            ds.MIMETypeOfEncapsulatedDocument = "application/pdf"
            ds.EncapsulatedDocument = pdf_bytes

            # Write the DICOM file
            ds.save_as(output_path, write_like_original=False)

            return True
        except Exception as e:
            print(f"Error generating DICOM: {str(e)}")
            return False

    def clear(self) -> "ReportGenerator":
        """Clear all content sections and attachments."""
        self.content_sections = []
        self._attachments = []
        return self

    def add_attachment(
        self, file_path: str, description: Optional[str] = None
    ) -> "ReportGenerator":
        """
        Add a file attachment to the PDF report.

        :param file_path: Path to the file to attach
        :param description: Optional description for the attachment
        :return: Self for method chaining
        """
        self._attachments.append((file_path, description))
        return self

    def clear_attachments(self) -> "ReportGenerator":
        """Clear all attachments."""
        self._attachments = []
        return self
