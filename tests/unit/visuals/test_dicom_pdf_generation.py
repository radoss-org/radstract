"""
Unit tests for DICOM PDF generation functionality in ReportGenerator.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pydicom

from radstract.data.dicom.utils import Modalities
from radstract.visuals.report_generator import ReportGenerator


class TestDicomPdfGeneration(unittest.TestCase):
    """Test cases for DICOM PDF generation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ReportGenerator(
            title="Test Report",
            accent_color="#00bbff",
            footer_text="Test Footer",
        )

        # Add some content to make the report meaningful
        self.generator.add_subtitle("Test Section")
        self.generator.add_paragraph("This is a test paragraph.")
        self.generator.add_table(
            [["A", "B"], ["1", "2"]], headers=["Col1", "Col2"]
        )

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_to_dicom_study_success(self):
        """Test successful DICOM PDF generation."""
        output_path = os.path.join(self.temp_dir, "test_report.dcm")

        # Create DICOM tags dataset
        dicom_tags = pydicom.Dataset()
        dicom_tags.PatientName = "Test^Patient"
        dicom_tags.PatientID = "TEST001"
        dicom_tags.StudyInstanceUID = pydicom.uid.generate_uid()
        dicom_tags.StudyID = "TEST001"
        dicom_tags.StudyDescription = "Test Study"

        result = self.generator.save_to_dicom_study(
            output_path=output_path,
            dicom_tags=dicom_tags,
            series_description="Test Series",
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))

        # Verify DICOM file structure
        ds = pydicom.dcmread(output_path)

        # Check SOP Class UID for Encapsulated PDF
        self.assertEqual(ds.SOPClassUID, Modalities.ENCAPSULATED_PDF.modality)

        # Check patient information
        self.assertEqual(ds.PatientName, "Test^Patient")
        self.assertEqual(ds.PatientID, "TEST001")

        # Check study information - StudyDescription is not transferred, only in important_tags_for_transfer
        # Only StudyInstanceUID, StudyID, PatientName, PatientID are transferred from dicom_tags
        self.assertEqual(ds.StudyInstanceUID, dicom_tags.StudyInstanceUID)
        self.assertEqual(ds.StudyID, "TEST001")
        self.assertEqual(ds.SeriesDescription, "Test Series")

        # Check document information
        self.assertEqual(ds.DocumentTitle, "Test Report")
        self.assertEqual(ds.MIMETypeOfEncapsulatedDocument, "application/pdf")
        self.assertEqual(ds.Modality, "DOC")

        # Check that PDF data exists and is not empty
        self.assertIsNotNone(ds.EncapsulatedDocument)
        self.assertGreater(len(ds.EncapsulatedDocument), 0)

        # Verify the PDF data starts with PDF header
        pdf_data = ds.EncapsulatedDocument
        self.assertTrue(pdf_data.startswith(b"%PDF"))

    def test_save_to_dicom_study_with_default_parameters(self):
        """Test DICOM generation with default parameters."""
        output_path = os.path.join(self.temp_dir, "test_default.dcm")

        # Create minimal dicom_tags to avoid NoneType error
        dicom_tags = pydicom.Dataset()

        result = self.generator.save_to_dicom_study(
            output_path, dicom_tags=dicom_tags
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))

        ds = pydicom.dcmread(output_path)

        # Check default values
        self.assertEqual(ds.SeriesDescription, "PDF Report")

    def test_save_to_dicom_study_hide_videos(self):
        """Test DICOM generation with videos hidden."""
        # Add a video to the report (this would normally fail, but we're testing the parameter)
        output_path = os.path.join(self.temp_dir, "test_no_videos.dcm")

        # Create minimal dicom_tags to avoid NoneType error
        dicom_tags = pydicom.Dataset()

        result = self.generator.save_to_dicom_study(
            output_path=output_path, dicom_tags=dicom_tags, hide_videos=True
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))

    @patch("radstract.visuals.report_generator.ReportGenerator.get_pdf_bytes")
    def test_save_to_dicom_study_pdf_generation_failure(
        self, mock_get_pdf_bytes
    ):
        """Test DICOM generation when PDF generation fails."""
        mock_get_pdf_bytes.return_value = None

        output_path = os.path.join(self.temp_dir, "test_fail.dcm")

        # Create minimal dicom_tags to avoid NoneType error
        dicom_tags = pydicom.Dataset()

        result = self.generator.save_to_dicom_study(
            output_path, dicom_tags=dicom_tags
        )

        self.assertFalse(result)
        self.assertFalse(os.path.exists(output_path))

    @patch("pydicom.Dataset.save_as")
    def test_save_to_dicom_study_save_failure(self, mock_save_as):
        """Test DICOM generation when DICOM save fails."""
        mock_save_as.side_effect = Exception("Save failed")

        output_path = os.path.join(self.temp_dir, "test_save_fail.dcm")

        # Create minimal dicom_tags to avoid NoneType error
        dicom_tags = pydicom.Dataset()

        result = self.generator.save_to_dicom_study(
            output_path, dicom_tags=dicom_tags
        )

        self.assertFalse(result)

    def test_extracted_pdf_functionality(self):
        """Test that PDF can be extracted from DICOM and is valid."""
        output_path = os.path.join(self.temp_dir, "test_extract.dcm")
        pdf_path = os.path.join(self.temp_dir, "extracted.pdf")

        # Create minimal dicom_tags to avoid NoneType error
        dicom_tags = pydicom.Dataset()

        # Generate DICOM
        result = self.generator.save_to_dicom_study(
            output_path, dicom_tags=dicom_tags
        )
        self.assertTrue(result)

        # Extract PDF
        ds = pydicom.dcmread(output_path)
        pdf_data = ds.EncapsulatedDocument

        with open(pdf_path, "wb") as f:
            f.write(pdf_data)

        # Verify extracted PDF
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 0)

        # Verify PDF structure
        with open(pdf_path, "rb") as f:
            content = f.read()
            self.assertTrue(content.startswith(b"%PDF"))
            self.assertTrue(b"%%EOF" in content)

    def test_dicom_metadata_completeness(self):
        """Test that all required DICOM metadata is present."""
        output_path = os.path.join(self.temp_dir, "test_metadata.dcm")

        # Create DICOM tags dataset
        dicom_tags = pydicom.Dataset()
        dicom_tags.PatientName = "Complete^Test"
        dicom_tags.PatientID = "COMP001"
        dicom_tags.StudyInstanceUID = pydicom.uid.generate_uid()
        dicom_tags.StudyID = "COMP001"

        result = self.generator.save_to_dicom_study(
            output_path=output_path,
            dicom_tags=dicom_tags,
        )

        self.assertTrue(result)

        ds = pydicom.dcmread(output_path)

        # Check required modules are present - only test attributes that are actually set by the method
        required_attributes = [
            # SOP Common Module
            "SOPClassUID",
            "SOPInstanceUID",
            # Patient Module (from dicom_tags)
            "PatientName",
            "PatientID",
            # General Study Module (from dicom_tags)
            "StudyInstanceUID",
            "StudyID",
            # Encapsulated Document Series Module
            "Modality",
            "SeriesInstanceUID",
            "SeriesNumber",
            # SC Equipment Module
            "ConversionType",
            "SecondaryCaptureDeviceManufacturer",
            "SecondaryCaptureDeviceManufacturerModelName",
            "SecondaryCaptureDeviceSoftwareVersions",
            # Encapsulated Document Module
            "InstanceNumber",
            "DocumentTitle",
            "MIMETypeOfEncapsulatedDocument",
            "EncapsulatedDocument",
        ]

        for attr in required_attributes:
            with self.subTest(attribute=attr):
                self.assertTrue(
                    hasattr(ds, attr), f"Missing required attribute: {attr}"
                )

    def test_multiple_dicom_files_unique_uids(self):
        """Test that multiple DICOM files have unique UIDs."""
        paths = []
        datasets = []

        for i in range(3):
            path = os.path.join(self.temp_dir, f"test_unique_{i}.dcm")
            paths.append(path)

            # Create dicom_tags with StudyInstanceUID to ensure it's transferred
            dicom_tags = pydicom.Dataset()
            dicom_tags.StudyInstanceUID = pydicom.uid.generate_uid()

            result = self.generator.save_to_dicom_study(
                path, dicom_tags=dicom_tags
            )
            self.assertTrue(result)

            ds = pydicom.dcmread(path)
            datasets.append(ds)

        # Check that all UIDs are unique
        sop_instance_uids = [ds.SOPInstanceUID for ds in datasets]
        study_instance_uids = [ds.StudyInstanceUID for ds in datasets]
        series_instance_uids = [ds.SeriesInstanceUID for ds in datasets]

        self.assertEqual(
            len(set(sop_instance_uids)),
            3,
            "SOP Instance UIDs should be unique",
        )
        self.assertEqual(
            len(set(study_instance_uids)),
            3,
            "Study Instance UIDs should be unique",
        )
        self.assertEqual(
            len(set(series_instance_uids)),
            3,
            "Series Instance UIDs should be unique",
        )

    def test_encapsulated_pdf_modality_constant(self):
        """Test that the ENCAPSULATED_PDF modality is correctly defined."""
        self.assertEqual(
            Modalities.ENCAPSULATED_PDF.modality,
            "1.2.840.10008.5.1.4.1.1.104.1",
        )
        self.assertEqual(Modalities.ENCAPSULATED_PDF.name, "DOC")
        self.assertIn("DOC", Modalities.ALL_MODALITIES)


if __name__ == "__main__":
    unittest.main()
