from datetime import datetime as dt
from unittest import TestCase
from thesis_common.learning_pipeline.curve_calculations import *


class TestDatePoint(TestCase):
    def test_constructor(self):
        datetime_object = dt.now()
        y = 100
        date_point = DatePoint(datetime_object, y)
        self.assertEqual(float, type(date_point.x))

    def test_comparison(self):
        p1 = Point(0, 0)
        p2 = Point(2, 2)
        p3 = Point(2, 2)
        self.assertFalse(p1 == p2)
        self.assertTrue(p2 == p3)


class TestLineEquation(TestCase):
    def test_constructor_simple(self):
        p1 = Point(0, 0)
        p2 = Point(5, 5)
        lin_eq = LineEquation(p1, p2)
        self.assertEqual(1, lin_eq.slope)
        self.assertEqual(0, lin_eq.b)

    def test_constructor(self):
        p1 = Point(0, 2)
        p2 = Point(2, 3)
        lin_eq = LineEquation(p1, p2)
        self.assertEqual(0.5, lin_eq.slope)
        self.assertEqual(2, lin_eq.b)

    def test_get_y(self):
        p1 = Point(0, 2)
        p2 = Point(2, 3)
        lin_eq = LineEquation(p1, p2)
        self.assertEqual(2.5, lin_eq.get_y(1))

    def test_get_x(self):
        p1 = Point(0, 2)
        p2 = Point(2, 3)
        lin_eq = LineEquation(p1, p2)
        self.assertEqual(1, lin_eq.get_x(2.5))


class TestLine(TestCase):
    def test_get_intersection_point_simple(self):
        p1 = Point(0, 0)
        p2 = Point(2, 2)
        l1 = Line(p1, p2)
        p3 = Point(-1, 1)
        p4 = Point(1, -1)
        l2 = Line(p3, p4)
        intersection_point = l1.get_intersection_point(l2)
        self.assertEqual(0, intersection_point.x)
        self.assertEqual(0, intersection_point.y)

    def test_get_intersection_point(self):
        p1 = Point(0, 1)
        p2 = Point(2, 2)
        l1 = Line(p1, p2)
        p3 = Point(1, 1)
        p4 = Point(-1, -1)
        l2 = Line(p3, p4)
        intersection_point = l1.get_intersection_point(l2)
        self.assertEqual(2, intersection_point.x)
        self.assertEqual(2, intersection_point.y)

    def test_get_intersection_no_point(self):
        p1 = Point(0, 0)
        p2 = Point(1, 0)
        l1 = Line(p1, p2)
        p3 = Point(0, 1)
        p4 = Point(1, 1)
        l2 = Line(p3, p4)
        intersection_point = l1.get_intersection_point(l2)
        self.assertEqual(None, intersection_point)


class TestPolygon(TestCase):
    def test_area(self):
        """
        Example from wikipedia:
        polygon defined by the points (3,4), (5,11), (12,8), (9,5), and (5,6)
        the area should be 30
        :return: void
        """
        corners = [Point(3, 4), Point(5, 11), Point(12, 8), Point(9, 5), Point(5, 6)]
        polygon = Polygon(corners)
        self.assertEqual(30, polygon.area)

        # make the corners unsorted and test again:
        corners = [Point(3, 4), Point(5, 6), Point(5, 11), Point(12, 8), Point(9, 5)]
        polygon = Polygon(corners)
        self.assertEqual(30, polygon.area)

    def test_area_six_point(self):
        corners1 = [Point(1, 3), Point(2, 5), Point(5, 5), Point(5, 5), Point(6, 3), Point(5, 1), Point(2, 1)]
        polygon1 = Polygon(corners1)
        corners2 = [Point(1, 3), Point(2, 5), Point(5, 5), Point(6, 3), Point(2, 1), Point(5, 1)]
        polygon2 = Polygon(corners2)
        self.assertEqual(polygon1.area, polygon2.area)

    def test_no_area(self):
        corners1 = [Point(0, 1), Point(1, 1), Point(2, 1)]
        polygon1 = Polygon(corners1)
        self.assertEqual(0, polygon1.area)


class TestCurveDiffCalculator(TestCase):
    def test_get_intersections_simple(self):
        p1 = Point(0, 1)
        p2 = Point(3, 1)
        p3 = Point(5, 3)
        p4 = Point(7, 3)
        curve1 = [p1, p2, p3, p4]
        p5 = Point(0, 3)
        p6 = Point(3, 3)
        p7 = Point(5, 1)
        p8 = Point(7, 1)
        curve2 = [p5, p6, p7, p8]

        curve_diff_calc = CurveDiffCalculator(curve1, curve2, 4)
        intersections = curve_diff_calc.get_intersections()
        self.assertEqual(1, len(intersections))
        self.assertEqual(4, intersections[0].x)
        self.assertEqual(2, intersections[0].y)

    def test_get_intersections(self):
        p1 = Point(0, 4)
        p2 = Point(1, 4)
        p3 = Point(2, 3)
        p4 = Point(3, 2)
        p5 = Point(4, 2)
        p6 = Point(5, 3)
        p7 = Point(6, 4)
        p8 = Point(7, 4)
        p9 = Point(8, 3)
        p10 = Point(9, 2)
        curve1 = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10]
        p11 = Point(0, 2)
        p12 = Point(4, 5)
        p13 = Point(5, 3)
        p14 = Point(7, 2)
        p15 = Point(9, 4)
        curve2 = [p11, p12, p13, p14, p15]
        curve_diff_calc = CurveDiffCalculator(curve1, curve2, 4)
        intersections = curve_diff_calc.get_intersections()
        self.assertEqual(3, len(intersections))
        self.assertTrue(any([inter for inter in intersections if inter.x == 5]))
        self.assertTrue(any([inter for inter in intersections if inter.x == 8]))
        self.assertTrue(any([inter for inter in intersections if inter.y == 3]))

    def test_get_polygons_one_intersection(self):
        p1 = Point(0, 1)
        p2 = Point(3, 1)
        p3 = Point(5, 3)
        p4 = Point(7, 3)
        curve1 = [p1, p2, p3, p4]
        p5 = Point(0, 3)
        p6 = Point(3, 3)
        p7 = Point(5, 1)
        p8 = Point(7, 1)
        curve2 = [p5, p6, p7, p8]

        curve_diff_calc = CurveDiffCalculator(curve1, curve2, 4)
        polygons = curve_diff_calc.get_polygons()
        self.assertEqual(2, len(polygons))
        self.assertEqual(7, polygons[0].area)
        self.assertEqual(5, polygons[1].area)

    def test_get_polygons_no_intersection(self):
        p1 = Point(0, 1)
        p2 = Point(3, 1)
        p7 = Point(5, 1)
        p8 = Point(7, 1)
        curve1 = [p1, p2, p7, p8]
        p5 = Point(0, 3)
        p6 = Point(3, 3)
        p3 = Point(5, 3)
        p4 = Point(7, 3)
        curve2 = [p5, p6, p3, p4]

        curve_diff_calc = CurveDiffCalculator(curve1, curve2, 4)
        polygons = curve_diff_calc.get_polygons()
        self.assertEqual(1, len(polygons))
        self.assertEqual(14, polygons[0].area)

    def test_get_polygons_four_intersections(self):
        p1 = Point(0, 0)
        p2 = Point(2, 2)
        p3 = Point(4, 0)
        p4 = Point(6, 2)
        p5 = Point(8, 0)
        curve1 = [p1, p2, p3, p4, p5]
        p6 = Point(0, 1)
        p7 = Point(4, 1)
        p8 = Point(8, 1)
        curve2 = [p6, p7, p8]

        curve_diff_calc = CurveDiffCalculator(curve1, curve2, 4)
        polygons = curve_diff_calc.get_polygons()
        self.assertEqual(5, len(polygons))
        self.assertEqual(1, polygons[0].area)
        self.assertEqual(1, polygons[1].area)
        self.assertEqual(1, polygons[2].area)
        self.assertEqual(0.5, polygons[3].area)
        self.assertEqual(0.5, polygons[4].area)

    def test_get_relative_difference(self):
        p1 = DatePoint(dt.fromtimestamp(0), 0)
        p2 = DatePoint(dt.fromtimestamp(2), 2)
        p3 = DatePoint(dt.fromtimestamp(4), 0)
        p4 = DatePoint(dt.fromtimestamp(6), 2)
        p5 = DatePoint(dt.fromtimestamp(8), 0)
        curve1 = [p1, p2, p3, p4, p5]
        p6 = DatePoint(dt.fromtimestamp(0), 1)
        p7 = DatePoint(dt.fromtimestamp(4), 1)
        p8 = DatePoint(dt.fromtimestamp(8), 1)
        curve2 = [p6, p7, p8]

        curve_diff_calc = CurveDiffCalculator(curve1, curve2, 2)
        polygons = curve_diff_calc.get_polygons()
        self.assertEqual(5, len(polygons))
        rel_diff = curve_diff_calc.get_relative_difference()
        self.assertEqual(0.25, rel_diff)