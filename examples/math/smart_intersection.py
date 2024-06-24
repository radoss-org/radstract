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
