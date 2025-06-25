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
from typing import Dict, List, Optional, Union

from weasyprint import HTML, Attachment


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

    def add_subtitle(self, text: str, level: int = 2) -> "ReportGenerator":
        """
        Add a subtitle/heading to the report.

        :param text: Text of the subtitle
        :param level: Level of the subtitle (1-6)
        """

        if not self.first_subtitle_made:
            margin_top = "0px"
            self.first_subtitle_made = True
        else:
            margin_top = "15px"

        tag = f"h{min(max(level, 1), 6)}"
        self.content_sections.append(
            {
                "type": "subtitle",
                "content": f'<{tag} style="color: {self.accent_color}; font-family: Arial Black, Arial, sans-serif; font-size: {20 - (level-2)*2}px; margin: {margin_top} 0 10px 0; border-bottom: 2px solid {self.accent_color}; padding-bottom: 5px;">{text}</{tag}>',
            }
        )
        return self

    def add_paragraph(self, text: str) -> "ReportGenerator":
        """
        Add a paragraph of text to the report.

        :param text: Text of the paragraph
        """
        self.content_sections.append(
            {
                "type": "paragraph",
                "content": f'<p style="color: {self.text_color}; font-family: Arial, sans-serif; margin: 10px 0; line-height: 1.4;">{text}</p>',
            }
        )
        return self

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
            table_html += "<thead>"
            table_html += "<tr>"
            for header in headers:
                table_html += f'<th style="background-color: {self.accent_color}; color: black; padding: 10px; text-align: center; font-weight: bold; border: 1px solid {self.border_color};">{header}</th>'
            table_html += "</tr>"
            table_html += "</thead>"

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
        table_html += "</tbody>"
        table_html += "</table>"

        self.content_sections.append({"type": "table", "content": table_html})
        return self

    def add_highlights(
        self,
        report_success: bool = True,
        highlight1: Optional[str] = None,
        highlight2: Optional[str] = None,
        highlight1_label: str = "Analysis Type",
        highlight2_label: str = "Data Quality",
    ) -> "ReportGenerator":
        """
        Add a highlights section with success/failure indicator and additional highlights.

        :param report_success: Whether the report generation was successful
        :param highlight1: First additional highlight value
        :param highlight2: Second additional highlight value
        :param highlight1_label: Label for the first highlight
        :param highlight2_label: Label for the second highlight
        """
        # Create highlights container
        highlights_html = f'<div style="background-color: {self.background_color_light}; border-radius: 8px; padding: 12px; margin: 20px 0; border: 1px solid {self.border_color};">'

        # Add highlights title
        highlights_html += f'<h3 style="color: {self.accent_color}; font-family: Arial Black, Arial, sans-serif; font-size: 16px; margin: 3px 0 8px 0; border-bottom: 2px solid {self.accent_color}; padding-bottom: 3px;">Highlights</h3>'

        # Create highlights grid in a single row with no wrap
        highlights_html += f'<div style="display: flex; flex-direction: row; gap: 8px; flex-wrap: nowrap; overflow-x: auto; justify-content: center;">'

        # Add success/failure indicator
        success_icon = "✓" if report_success else "✗"
        success_text = "Success" if report_success else "Failed"
        success_color = "#00ff00" if report_success else "#ff4444"

        highlights_html += f"""
        <div style="display: flex; align-items: center; justify-content: center; background-color: {self.background_color}; padding: 8px; border-radius: 6px; border: 1px solid {self.border_color}; min-width: 140px; flex: 1;">
            <div style="width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; margin-right: 8px; flex-shrink: 0; background-color: rgba({success_color}, 0.2); color: {success_color}; border: 2px solid {success_color};">
                {success_icon}
            </div>
            <div style="flex: 1; min-width: 0; text-align: center;">
                <div style="font-size: 10px; color: {self.text_color_light}; margin-bottom: 2px; white-space: nowrap;">Report Status</div>
                <div style="font-size: 12px; font-weight: bold; color: {self.text_color}; white-space: nowrap;">{success_text}</div>
            </div>
        </div>
        """

        # Add first additional highlight if provided
        if highlight1:
            highlights_html += f"""
            <div style="display: flex; align-items: center; justify-content: center; background-color: {self.background_color}; padding: 8px; border-radius: 6px; border: 1px solid {self.border_color}; min-width: 140px; flex: 1;">
                <div style="width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; margin-right: 8px; flex-shrink: 0; background-color: rgba(0, 150, 255, 0.2); color: #0096ff; border: 2px solid #0096ff;">
                    ℹ
                </div>
                <div style="flex: 1; min-width: 0; text-align: center;">
                    <div style="font-size: 10px; color: {self.text_color_light}; margin-bottom: 2px; white-space: nowrap;">{highlight1_label}</div>
                    <div style="font-size: 12px; font-weight: bold; color: {self.text_color}; white-space: nowrap;">{highlight1}</div>
                </div>
            </div>
            """

        # Add second additional highlight if provided
        if highlight2:
            highlights_html += f"""
            <div style="display: flex; align-items: center; justify-content: center; background-color: {self.background_color}; padding: 8px; border-radius: 6px; border: 1px solid {self.border_color}; min-width: 140px; flex: 1;">
                <div style="width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; margin-right: 8px; flex-shrink: 0; background-color: rgba(0, 150, 255, 0.2); color: #0096ff; border: 2px solid #0096ff;">
                    ℹ
                </div>
                <div style="flex: 1; min-width: 0; text-align: center;">
                    <div style="font-size: 10px; color: {self.text_color_light}; margin-bottom: 2px; white-space: nowrap;">{highlight2_label}</div>
                    <div style="font-size: 12px; font-weight: bold; color: {self.text_color}; white-space: nowrap;">{highlight2}</div>
                </div>
            </div>
            """

        highlights_html += "</div></div>"

        self.content_sections.append(
            {"type": "highlights", "content": highlights_html}
        )
        return self

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

            self.content_sections.append(
                {"type": "image", "content": image_html}
            )
        except Exception as e:
            self.content_sections.append(
                {
                    "type": "paragraph",
                    "content": f'<p style="color: red;">Error loading image {image_path}: {str(e)}</p>',
                }
            )

        return self

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

            self.content_sections.append(
                {"type": "video", "content": video_html}
            )
        except Exception as e:
            # Fallback to placeholder if video loading fails
            video_html = f'<div style="text-align: center; margin: 20px 0; padding: 40px; background-color: {self.background_color}; border: 4px dashed {self.accent_color}; border-radius: 8px; max-width: 50%; margin-left: auto; margin-right: auto;">'
            video_html += f'<p style="color: {self.accent_color}; font-size: 18px; margin: 0;">🎥 Video Content</p>'
            video_html += f'<p style="color: {self.text_color}; font-size: 14px; margin: 10px 0 0 0;">{video_path}</p>'
            video_html += f'<p style="color: red; font-size: 12px; margin: 5px 0 0 0;">Error loading video: {str(e)}</p>'

            if caption:
                video_html += f'<p style="color: {self.text_color}; font-style: italic; margin-top: 10px; font-size: 14px;">{caption}</p>'

            video_html += "</div>"

            self.content_sections.append(
                {"type": "video", "content": video_html}
            )

        return self

    def add_json(
        self, data: Union[Dict, List], title: Optional[str] = None
    ) -> "ReportGenerator":
        """
        Add JSON data as formatted text to the report.

        :param data: Dictionary or list of data
        :param title: Title for the JSON block
        """
        json_html = f'<div style="background-color: {self.background_color_light}; border: 1px solid {self.border_color}; border-radius: 6px; padding: 15px; margin: 15px 0; overflow-x: auto;">'

        if title:
            json_html += f'<h4 style="color: {self.accent_color}; margin: 0 0 10px 0; font-family: Arial Black, Arial, sans-serif;">{title}</h4>'

        json_html += f'<pre style="color: {self.text_color_light}; padding: 10px; font-family: monospace; font-size: 12px; margin: 0; white-space: pre-wrap; background-color: {self.background_color};">{json.dumps(data, indent=2)}</pre>'
        json_html += "</div>"

        self.content_sections.append({"type": "json", "content": json_html})
        return self

    def generate_html(
        self, hide_videos: bool = False, hide_attachments: bool = False
    ) -> str:
        """
        Generate the complete HTML content.

        :param hide_videos: If True, video sections will be hidden from the output
        :param hide_attachments: If True, attachment information will be hidden from the output
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.title}</title>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: A4;
                    margin: 3.5cm 0 0 0;
                    padding: 0;
                    background-color: {self.page_color};
                }}

                html {{
                    background-color: {self.page_color};
                    height: 100%;
                }}

                body, html {{
                    font-family: Arial, sans-serif;
                    padding: 0;
                    color: {self.text_color};
                    margin: 0;
                }}

                @media screen {{
                    header, footer {{
                        position: static !important;
                    }}

                    .content-wrapper {{
                        padding-top: 40px;
                        padding-bottom: 50px;
                    }}
                }}

                header {{
                    position: fixed;
                    left: 0;
                    right: 0;
                    top: -3.5cm;
                    height: 2.7cm;
                    padding: 0 50px;
                    background-color: {self.header_color};
                    border-bottom: 4px solid {self.accent_color};
                    display: flex;
                    align-items: center;
                    justify-content: flex-start;
                }}

                .header-content {{
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    width: 100%;
                    max-width: 800px;
                    margin: 0 auto;
                }}

                .header-logo {{
                    height: 40px;
                    width: auto;
                    flex-shrink: 0;
                }}

                header h1 {{
                    color: {self.accent_color};
                    margin: 0;
                    font-size: 24px;
                    font-family: 'Arial Black', Arial, sans-serif;
                    text-align: left;
                }}

                footer {{
                    position: fixed;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    height: 2.4cm;
                    background-color: {self.footer_color};
                    border-top: 4px solid {self.accent_color};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}

                .footer-table {{
                    width: 100%;
                    max-width: 800px;
                    margin: 0 auto;
                    border-collapse: collapse; /* Important for tables */
                }}

                .footer-table td {{
                    color: {self.text_color_light};
                    font-size: 14px;
                    vertical-align: middle; /* Vertically centers the content */
                    padding: 0 50px;
                    height: 2cm; /* Match the footer height */
                }}

                .footer-left {{
                    text-align: left;
                    width: 60%;
                }}

                .footer-right {{
                    text-align: right;
                    width: 40%;
                }}

                .content-wrapper {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding-right: 80px;
                    padding-left: 80px;
                }}

                h4 {{
                    background-color: {self.background_color_light};
                }}

            </style>
        </head>
        <body>
            <header>
                <div class="header-content">
        """

        # Add logo if provided
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

                html_content += f'<img src="data:image/{logo_type};base64,{logo_base64}" alt="Logo" class="header-logo">'
            except Exception as e:
                # If logo loading fails, don't add it
                pass

        html_content += f"""
                    <h1>{self.title}</h1>
                </div>
            </header>
            <div class="content-wrapper">
        """

        # Add all content sections, filtering out videos if hide_videos is True
        for section in self.content_sections:
            if hide_videos and section["type"] == "video":
                continue
            html_content += section["content"]

        # Add attachment information if any attachments are present and not hidden
        if self._attachments and not hide_attachments:
            attachment_info = f"""
            <div style="margin: 20px 0; padding: 15px; background-color: {self.background_color_light}; border: 1px solid {self.border_color}; border-radius: 6px;">
                <h4 style="color: {self.accent_color}; margin: 0 0 10px 0; font-family: Arial Black, Arial, sans-serif;">Attachments</h4>
                <p style="color: {self.text_color}; font-family: Arial, sans-serif; margin: 0 0 10px 0; font-size: 14px;">
                    This report includes {len(self._attachments)} file attachment(s). To access attachments, open this PDF in Adobe Acrobat and go to <strong>View</strong> → <strong>Show/Hide</strong> → <strong>Side panels</strong> → <strong>Attachments</strong>.
                    For detailed instructions, visit:
                    <a href="https://helpx.adobe.com/ca/acrobat/using/links-attachments-pdfs.html#:~:text=Save%20the%20file.-,Open%20attachments,-You%20can%20open"
                       style="color: {self.accent_color}; text-decoration: underline;">Adobe Acrobat - Links and Attachments in PDFs</a>
                </p>
                <div style="margin-top: 10px;">
            """

            # Add individual attachment descriptions
            for i, (file_path, description) in enumerate(self._attachments, 1):
                filename = os.path.basename(file_path)
                desc_text = (
                    description if description else "No description provided"
                )
                attachment_info += f"""
                    <div style="margin: 8px 0; padding: 8px; background-color: {self.background_color}; border-radius: 4px; border-left: 3px solid {self.accent_color};">
                        <div style="font-weight: bold; color: {self.text_color}; font-size: 13px;">{filename}</div>
                        <div style="color: {self.text_color_light}; font-size: 12px; margin-top: 2px;">{desc_text}</div>
                    </div>
                """

            attachment_info += """
                </div>
            </div>
            """
            html_content += attachment_info

        html_content += """
            </div>
            <footer>
                <table class="footer-table">
                    <tr>
                        <td class="footer-left">
        """
        # Add footer text to the left cell
        if self.footer_text:
            html_content += self.footer_text

        html_content += """
                        </td>
                        <td class="footer-right">
        """
        # Add website and email to the right cell
        if self.footer_website:
            html_content += f"<div>{self.footer_website}</div>"
        if self.footer_email:
            html_content += f"<div>{self.footer_email}</div>"

        html_content += """
                        </td>
                    </tr>
                </table>
            </footer>
        </body>
        </html>
        """

        return html_content

    def save_pdf(self, output_path: str, hide_videos=True) -> bool:
        """
        Save the report as a PDF file.

        :param output_path: Path where to save the PDF file
        """
        try:
            html_content = self.generate_html(hide_videos=hide_videos)

            # Create HTML object from string
            html_doc = HTML(string=html_content)

            # Write PDF to file with attachments if any
            if self._attachments:
                attachments = []

                for attachment in self._attachments:
                    with open(attachment[0], "rb") as f:
                        file_obj = io.BytesIO(f.read())
                    attachments.append(
                        Attachment(
                            name=os.path.basename(attachment[0]),
                            file_obj=file_obj,
                            description=attachment[1],
                        )
                    )

                html_doc.write_pdf(output_path, attachments=attachments)
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
        with open(output_path, "w") as f:
            f.write(self.generate_html(hide_attachments=hide_attachments))
        return True

    def get_pdf_bytes(self, hide_videos=True) -> Optional[bytes]:
        """
        Get the PDF as bytes instead of saving to file.

        :return: PDF content as bytes, or None if failed
        """
        try:
            html_content = self.generate_html(hide_videos=hide_videos)

            # Create HTML object from string
            html_doc = HTML(string=html_content)

            # Write PDF to bytes with attachments if any
            if self._attachments:
                attachments = []

                for attachment in self._attachments:
                    with open(attachment[0], "rb") as f:
                        file_obj = io.BytesIO(f.read())
                    attachments.append(
                        Attachment(
                            name=os.path.basename(attachment[0]),
                            file_obj=file_obj,
                            description=attachment[1],
                        )
                    )

                pdf_bytes = html_doc.write_pdf(attachments=attachments)
            else:
                pdf_bytes = html_doc.write_pdf()

            return pdf_bytes

        except Exception as e:
            print(f"Error generating PDF bytes: {str(e)}")
            return None

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
