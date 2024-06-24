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

    ALL_TYPES = [
        SERIES,
        SERIES_ANONYMIZED,
        SINGLE,
        DEFAULT,
    ]

    ALL_SERIES = [
        SERIES,
        SERIES_ANONYMIZED,
    ]

    ANON = [
        SERIES_ANONYMIZED,
        SINGLE_ANONYMIZED,
    ]
