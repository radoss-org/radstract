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

"""
This example shows how to create a report with various content types
using the minimal API provided by ReportGenerator.
"""

from radstract.testdata import Cases, download_case
from radstract.visuals import ReportGenerator

video_file, img_file, logo = download_case(Cases.ULTRASOUND_REPORT_TEST)


def main():
    # Create a report generator with comprehensive custom colors
    report_gen = ReportGenerator(
        title="Radstract Report",
        footer_text="Test/Example report created by https://github.com/radoss-org/radstract",
        footer_website="https://radoss.org",
        footer_email="info@radoss.org",
        logo_path=logo,
    )

    # Build the report by calling methods in sequence
    # The order of these calls determines the order in the report

    report_gen.add_subtitle("Medical Analysis Report", level=1)

    report_gen.add_paragraph(
        "This report contains the results of our comprehensive medical analysis. "
        "The data has been processed and validated according to standard protocols."
    )

    # Add highlights section with success/failure indicator and additional highlights
    report_gen.add_highlights(
        report_success=True,
        highlight1="Radstract",
        highlight1_label="Analysis Type",
        highlight2="High",
        highlight2_label="Data Quality",
    )

    report_gen.add_subtitle("Patient Information", level=2)

    # Add a table with patient data
    patient_data = [
        ["John Doe", "45", "Male", "Hypertension"],
        ["Jane Smith", "32", "Female", "None"],
        ["Bob Johnson", "58", "Male", "Diabetes"],
    ]

    report_gen.add_table(
        data=patient_data, headers=["Name", "Age", "Gender", "Conditions"]
    )

    report_gen.add_subtitle("Analysis Results", level=2)

    report_gen.add_paragraph(
        "The analysis revealed several key findings that require attention. "
        "All measurements were taken using standardized protocols."
    )

    # Add JSON data
    analysis_results = {
        "blood_pressure": {
            "systolic": 140,
            "diastolic": 90,
            "status": "Elevated",
        },
        "cholesterol": {
            "total": 200,
            "hdl": 45,
            "ldl": 130,
            "status": "Borderline High",
        },
    }

    report_gen.add_json(analysis_results, title="Detailed Analysis Results")

    report_gen.add_subtitle("Media Content", level=2)

    # Note: To add an actual image, you would use:
    report_gen.add_image(img_file, caption="Patient scan")

    # Add the image as an attachment for high-resolution access
    report_gen.add_attachment(
        file_path=img_file,
        description="Patient scan - high resolution image file",
    )

    report_gen.add_video(
        video_file, caption="Ultrasound examination recording"
    )

    report_gen.add_attachment(
        file_path=video_file,
        description="Ultrasound examination recording - original video file",
    )

    report_gen.add_subtitle("Conclusions", level=2)

    report_gen.add_paragraph(
        "Based on the comprehensive analysis, we recommend regular monitoring "
        "and lifestyle modifications. Follow-up appointments should be scheduled "
        "within 3 months."
    )

    success = report_gen.save_pdf("debug/medical_report.pdf")

    if success:
        print("✅ PDF report generated successfully: debug/medical_report.pdf")
    else:
        print("❌ Failed to generate PDF report")

    # Save as HTML for preview
    html_success = report_gen.save_html("debug/medical_report.html")
    if html_success:
        print(
            "✅ HTML report generated successfully: debug/medical_report.html"
        )
    else:
        print("❌ Failed to generate HTML report")

    # Alternative: Get PDF as bytes
    pdf_bytes = report_gen.get_pdf_bytes()
    if pdf_bytes:
        print(f"📄 PDF generated as bytes: {len(pdf_bytes)} bytes")

    # Clear and reuse the generator
    report_gen.clear()


if __name__ == "__main__":
    main()
