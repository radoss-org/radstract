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
