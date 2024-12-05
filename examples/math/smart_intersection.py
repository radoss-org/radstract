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
A utility function for finding the intersection of two lines.

This function can handle vertical and horizontal lines.
"""

from radstract.math import smart_find_intersection

# Define the two lines
line1 = [(0, 0), (1, 1)]
line2 = [(0, 1), (1, 0)]

# Find the intersection
intersection = smart_find_intersection(line1[0], line1[1], line2[0], line2[1])

print(intersection)

# Scan also handle horizontal and vertical lines
line3 = [(0, 0), (0, 1)]
line4 = [(0, 0), (1, 0)]

intersection = smart_find_intersection(line3[0], line3[1], line4[0], line4[1])

print(intersection)
