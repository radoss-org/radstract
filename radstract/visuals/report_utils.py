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

import os


def generate_css_styles(
    accent_color: str,
    header_color: str,
    page_color: str,
    background_color: str,
    background_color_light: str,
    text_color: str,
    border_color: str,
    text_color_light: str,
    footer_color: str,
) -> str:
    """
    Generate the complete CSS styles for the report.

    :param accent_color: Primary accent color
    :param header_color: Header background color
    :param page_color: Page background color
    :param background_color: Main background color
    :param background_color_light: Light background color
    :param text_color: Primary text color
    :param border_color: Border color
    :param text_color_light: Light text color
    :param footer_color: Footer background color
    :return: Complete CSS styles as string
    """
    return f"""
        @page {{
            size: A4;
            margin: 3.5cm 0 0 0;
            padding: 0;
            background-color: {page_color};
        }}

        html {{
            background-color: {page_color};
            height: 100%;
        }}

        body, html {{
            font-family: Arial, sans-serif;
            padding: 0;
            color: {text_color};
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
            background-color: {header_color};
            border-bottom: 4px solid {accent_color};
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
            color: {accent_color};
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
            background-color: {footer_color};
            border-top: 4px solid {accent_color};
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .footer-table {{
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            border-collapse: collapse;
        }}

        .footer-table td {{
            color: {text_color_light};
            font-size: 14px;
            vertical-align: middle;
            padding: 0 50px;
            height: 2cm;
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
            background-color: {background_color_light};
        }}
    """


def create_highlight_box(
    icon: str,
    icon_color: str,
    label: str,
    value: str,
    background_color: str,
    border_color: str,
    text_color: str,
    text_color_light: str,
) -> str:
    """
    Create a highlight box HTML element.

    :param icon: Icon character or symbol
    :param icon_color: Color for the icon
    :param label: Label text
    :param value: Value text
    :param background_color: Background color
    :param border_color: Border color
    :param text_color: Text color
    :param text_color_light: Light text color
    :return: HTML string for the highlight box
    """
    return f"""
        <div style="display: flex; align-items: center; justify-content: center; background-color: {background_color}; padding: 8px; border-radius: 6px; border: 1px solid {border_color}; min-width: 140px; flex: 1;">
            <div style="width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; margin-right: 8px; flex-shrink: 0; background-color: rgba({icon_color}, 0.2); color: {icon_color}; border: 2px solid {icon_color};">
                {icon}
            </div>
            <div style="flex: 1; min-width: 0; text-align: center;">
                <div style="font-size: 10px; color: {text_color_light}; margin-bottom: 2px; white-space: nowrap;">{label}</div>
                <div style="font-size: 12px; font-weight: bold; color: {text_color}; white-space: nowrap;">{value}</div>
            </div>
        </div>
    """


def create_attachment_info(
    attachments: list,
    background_color_light: str,
    border_color: str,
    accent_color: str,
    text_color: str,
    text_color_light: str,
) -> str:
    """
    Create HTML for attachment information section.

    :param attachments: List of attachment tuples (file_path, description)
    :param background_color_light: Light background color
    :param border_color: Border color
    :param accent_color: Accent color
    :param text_color: Text color
    :param text_color_light: Light text color
    :return: HTML string for attachment info
    """
    if not attachments:
        return ""

    attachment_info = f"""
    <div style="margin: 20px 0; padding: 15px; background-color: {background_color_light}; border: 1px solid {border_color}; border-radius: 6px;">
        <h4 style="color: {accent_color}; margin: 0 0 10px 0; font-family: Arial Black, Arial, sans-serif;">Attachments</h4>
        <p style="color: {text_color}; font-family: Arial, sans-serif; margin: 0 0 10px 0; font-size: 14px;">
            This report includes {len(attachments)} file attachment(s). To access attachments, open this PDF in Adobe Acrobat and go to <strong>View</strong> → <strong>Show/Hide</strong> → <strong>Side panels</strong> → <strong>Attachments</strong>.
            For detailed instructions, visit:
            <a href="https://helpx.adobe.com/ca/acrobat/using/links-attachments-pdfs.html#:~:text=Save%20the%20file.-,Open%20attachments,-You%20can%20open"
               style="color: {accent_color}; text-decoration: underline;">Adobe Acrobat - Links and Attachments in PDFs</a>
        </p>
        <div style="margin-top: 10px;">
    """

    for file_path, description in attachments:
        filename = os.path.basename(file_path)
        desc_text = description if description else "No description provided"
        attachment_info += f"""
            <div style="margin: 8px 0; padding: 8px; background-color: {background_color_light.replace(background_color_light, 'rgba(0,0,0,0.1)')}; border-radius: 4px; border-left: 3px solid {accent_color};">
                <div style="font-weight: bold; color: {text_color}; font-size: 13px;">{filename}</div>
                <div style="color: {text_color_light}; font-size: 12px; margin-top: 2px;">{desc_text}</div>
            </div>
        """

    attachment_info += """
        </div>
    </div>
    """
    return attachment_info
