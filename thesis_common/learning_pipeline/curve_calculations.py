import math
import time
from datetime import datetime


class CurveDiffCalculator(object):
    """
    Class to calculate the relative difference between two curves.
    Relative to a max value.
    """

    def __init__(self, curve1, curve2, max):
        """
        :param curve1: a list of points
        :param curve2: a list of points
        :param max: the max to which the relative difference will be compared
        """
        self.curve1 = curve1
        self.curve2 = curve2
        self.max = max

    def get_relative_difference(self):
        """
        Calculates the relative difference between two curves i.e.:
        the total area of the polygons created by the two curves
        divided by the total area
        :return: the difference expressed in percentage
        """
        self.curve1 = sorted(self.curve1)
        self.curve2 = sorted(self.curve2)
        l = self.curve1[-1].datetime - self.curve1[0].datetime
        #assert l != 0, "this curve has len zero"
        try:
            assert l == self.curve2[-1].datetime - self.curve2[0].datetime
        except:
            pass
        polygon_area = sum([x.area for x in self.get_polygons()])
        total_area = self.max * l.total_seconds()
        return polygon_area / float(total_area)

    def get_intersections(self):
        """
        Calculate the intersections of the curves
        :return:
        """
        intersections = []
        for i in range(1, len(self.curve1)):
            line1 = Line(self.curve1[i - 1], self.curve1[i])
            other_lines = self._get_lines_between(curve=self.curve2, point1=self.curve1[i - 1], point2=self.curve1[i])
            for line2 in other_lines:
                intersection_point = line1.get_intersection_point(line2)
                if intersection_point is not None and line1.within_x_range(intersection_point) and line2.within_x_range(
                        intersection_point):
                    intersections.append(intersection_point)
                    break
        return sorted(list(set(intersections)))

    def _get_lines_between(self, curve, point1, point2):
        """
        :precondition: the curve needs to be sorted
        :param point1:
        :param point2:
        :return:
        """
        lines = []
        # The next code is not done with a list comprehension for optimization
        points = []
        for p in curve:
            if point1 <= p <= point2:
                points.append(p)
            elif p > point2:
                break
        if len(points) != 0:
            index_first_point = curve.index(points[0])
            index_last_point = curve.index(points[-1])
            # adding the previous point:
            if index_first_point > 0:
                points.append(curve[index_first_point - 1])
            # adding the last point
            if index_last_point < len(curve) - 1:
                points.append(curve[index_last_point + 1])
        else:
            """
            The current line lays completely within the range of another line.
            Therefor no points are found, so we search this absorbing line.
            """
            points = self._find_absorbing_line(curve, point1, point2)
        assert len(points) > 1
        points = sorted(points)
        for i in range(1, len(points)):
            lines.append(Line(points[i - 1], points[i]))
        return lines

    @staticmethod
    def _find_absorbing_line(curve, point1, point2):

        for i in range(1, len(curve)):
            if curve[i - 1] <= point1 and point2 <= curve[i]:
                return [curve[i - 1], curve[i]]
        raise ValueError("Some wrong points or curve was supplied")

    def get_polygons(self):
        """
        It calculates all the different polygons created by the curves.
        If there are no intersections one polygon is given back
        :return:
        """
        polygons = []
        intersections = self.get_intersections()

        # If there were no intersections
        if len(intersections) == 0:
            polygons.append(Polygon(self.curve1 + self.curve2))
            return polygons

        # Everything except the edge cases
        for i in range(1, len(intersections)):
            line = Line(intersections[i - 1], intersections[i])
            corners1 = [p for p in self.curve1 if line.within_x_range(p)]
            corners2 = [p for p in self.curve2 if line.within_x_range(p)]
            corners = [intersections[i - 1]] + corners1 + [intersections[i]] + corners2
            polygons.append(Polygon(corners))

        # Edge case: points before first intersection
        corners1 = [p for p in self.curve1 if p <= intersections[0]]
        corners2 = [p for p in self.curve2 if p <= intersections[0]]
        corners = corners1 + [intersections[0]] + corners2
        if len(corners) > 1:
            polygons.append(Polygon(corners))

        # Edge case: points after last intersection
        corners1 = [p for p in self.curve1 if p >= intersections[-1]]
        corners2 = [p for p in self.curve2 if p >= intersections[-1]]
        corners = corners1 + [intersections[-1]] + corners2
        if len(corners) > 1:
            polygons.append(Polygon(corners))

        return polygons


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __le__(self, other):
        return self.x <= other.x

    def __lt__(self, other):
        return self.x <= other.x

    def __hash__(self):
        return int((self.x + self.y) * 1000000) % 97


class DatePoint(Point):
    def __init__(self, datetime_object, y):
        super(DatePoint, self).__init__(time.mktime(datetime_object.timetuple()), y)
        self.datetime = datetime_object


class Line(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.equation = LineEquation(self.p1, self.p2)

    def get_intersection_point(self, other_line):
        if self.equation == other_line.equation:
            return None
        if other_line.equation.b - self.equation.b == 0:
            x = 0
        else:
            if self.equation.slope - other_line.equation.slope != 0:
                x = (other_line.equation.b - self.equation.b) / float(self.equation.slope - other_line.equation.slope)
            else:
                return None
        y = self.equation.get_y(x)
        return Point(x, y)

    def get_intersection_date_point(self, other_line):
        point = self.get_intersection_date_point(other_line)
        dt = datetime.fromtimestamp(point.x)
        return DatePoint(dt, point.y)

    def within_x_range(self, point):
        """
        Checks if the given point falls within the x_range of this line
        :param point:
        :return:
        """
        x_min = min(self.p1.x, self.p2.x)
        x_max = max(self.p1.x, self.p2.x)
        return x_min <= point.x <= x_max


class LineEquation(object):
    def __init__(self, p1, p2):
        if p2.x - p1.x != 0:
            self.slope = (p2.y - p1.y) / float(p2.x - p1.x)
        else:
            self.slope = 0
        self.b = -self.slope * p1.x + p1.y

    def get_y(self, x):
        """
        Given x calculate y
        :param x:
        :return: y
        """
        return self.slope * x + self.b

    def get_x(self, y):
        """
        Given y calculate x
        :param y:
        :return: x
        """
        return (y - self.b) / float(self.slope)

    def __eq__(self, other):
        return self.slope == other.slope and self.b == other.b


class Polygon(object):
    """
    Area calculation adapted from here:
    http://code.activestate.com/recipes/578047-area-of-polygon-using-shoelace-formula/
    """

    def __init__(self, corner_points):
        """
        The corners are first sorted
        :param corner_points: the corners of the polygon, they might be unsorted
        """
        # First sort
        self.corners = self.sort_polygon([(p.x, p.y) for p in corner_points])
        self.area = self.calculate_area(self.corners)

    @staticmethod
    def calculate_area(corners):
        n = len(corners)  # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += corners[i][0] * corners[j][1]
            area -= corners[j][0] * corners[i][1]
        area = abs(area) / 2.0
        return area

    @staticmethod
    def sort_polygon(corners):
        """
        sort corners in counter-clockwise direction
        :param corners: to be sorted
        :return: a list of tuples of sorted corners in counter-clockwise direction
        """
        # calculate centroid of the polygon
        n = len(corners)  # of corners
        cx = float(sum(x for x, y in corners)) / n
        cy = float(sum(y for x, y in corners)) / n
        # create a new list of corners which includes angles
        cornersWithAngles = []
        for x, y in corners:
            an = (math.atan2(y - cy, x - cx) + 2.0 * math.pi) % (2.0 * math.pi)
            cornersWithAngles.append((x, y, an))
        # sort it using the angles
        cornersWithAngles.sort(key=lambda tup: tup[2])
        # return the sorted corners w/ angles removed
        return [(x, y) for (x, y, an) in cornersWithAngles]
