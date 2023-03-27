import unittest

from eval_graph import *


class TestGraphEvalFunc(unittest.TestCase):
    """Test eval_graph.py"""

    def test_vector_dot_product(self):
        """Test method vector_dot_product(v0, v1)"""
        self.assertEqual(6, vector_dot_product((1, 1, 1), (2, 2, 2)))
        self.assertEqual(0, vector_dot_product((1, 1, 1), (0, 0, 0)))

    def test_point_distance_to_line_segment_squared(self):
        """Test method point_distance_to_line((point0, point1, dir1)"""
        self.assertEqual(25, point_distance_to_line_segment_squared((3, 4, 0), (0, 0, 0), (0, 0, 1), 1))
        self.assertEqual(29, point_distance_to_line_segment_squared((2, 3, 4), (0, 0, 0), (10, 0, 0), 0.5))
        self.assertEqual(25, point_distance_to_line_segment_squared((4, 3, 1), (0, 0, 0), (0, 0, -1), 2))
        self.assertEqual(26, point_distance_to_line_segment_squared((4, 3, 1), (0, 0, 0), (0, 0, 1), 1))
        self.assertEqual(26, point_distance_to_line_segment_squared((4, 3, 1), (0, 0, 0), (-4, -3, -1), 1))
        self.assertEqual(0, point_distance_to_line_segment_squared((4, 3, 1), (0, 0, 0), (-4, -3, -1), 50))
        self.assertEqual(26, point_distance_to_line_segment_squared((4, 3, 1), (0, 0, 0), (0, 0, 0), 1))


if __name__ == '__main__':
    unittest.main()
