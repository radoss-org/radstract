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
Radstract Visuals Subpackage. For generating reports and visuals.

This subpackage contains:
- ReportGenerator: A class for generating reports and visuals.

Examples: https://github.com/radoss-org/Radstract/tree/main/examples/visuals/report_generation.py
"""

from .report_generator import ReportGenerator

__all__ = ["ReportGenerator"]
