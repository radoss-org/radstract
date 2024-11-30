"""
Utility class for the different supported types of Dicom data.

Down the line, this could include modality or even scanner specific types.
"""


class DicomTypes:
    SERIES = "SERIES"
    SERIES_ANONYMIZED = "SERIES_ANONYMIZED"
    SINGLE = "SINGLE"
    SINGLE_ANONYMIZED = "SINGLE_ANONYMIZED"
    DEFAULT = SERIES

    ALL_TYPES = [SERIES, SERIES_ANONYMIZED, SINGLE, DEFAULT, SINGLE_ANONYMIZED]

    ALL_SERIES = [
        SERIES,
        SERIES_ANONYMIZED,
    ]

    ANON = [
        SERIES_ANONYMIZED,
        SINGLE_ANONYMIZED,
    ]


class Modalities:
    ULTRASOUND = "1.2.840.10008.5.1.4.1.1.1"

    ALL_MODALITIES = [
        ULTRASOUND,
    ]
