import unittest
import src.model as model


class TestRegion2d(unittest.TestCase):
    """Unit tests for the simple Region2d class"""

    def test_args_saved_correctly(self):
        """Just check that the constructor correctly saves the arguments"""
        expectedX = 2334
        expectedY = 9623
        expectedW = 500
        expectedH = 750

        sut = model.Region2d(expectedX, expectedY, expectedW, expectedH)

        self.assertEqual(expectedX, sut.x)
        self.assertEqual(expectedY, sut.y)
        self.assertEqual(expectedW, sut.w)
        self.assertEqual(expectedH, sut.h)

        self.assertEqual(expectedX + expectedW, sut.x2)
        self.assertEqual(expectedY + expectedH, sut.y2)

        self.assertEqual(expectedX + expectedW, sut.right_x)
        self.assertEqual(expectedY + expectedH, sut.bottom_y)

    def test_scale_region(self):
        """Just check that the constructor correctly saves the arguments"""
        x = 23
        y = 96
        w = 50
        h = 75
        scale = 2.0

        sut = model.Region2d(x, y, w, h)
        result = model.scale(sut, scale)

        expectedX = int(x * scale)
        expectedY = int(y * scale)
        expectedW = int(w * scale)
        expectedH = int(h * scale)
        self.assertEqual(expectedX, result.x)
        self.assertEqual(expectedY, result.y)
        self.assertEqual(expectedW, result.w)
        self.assertEqual(expectedH, result.h)

    def test_normalize_region_on_already_normalized_region(self):
        """Just check that the constructor correctly saves the arguments"""
        x = 23
        y = 96
        w = 50
        h = 75

        sut = model.Region2d(x, y, w, h)
        result = model.normalize(sut)

        self.assertEqual(result, sut)

    def test_normalize_region(self):
        """Just check that the constructor correctly saves the arguments"""
        x = 110
        y = 225
        w = -50
        h = -75

        sut = model.Region2d(x, y, w, h)
        result = model.normalize(sut)

        expectedX = x - -w
        expectedY = y - -h
        expectedW = -w
        expectedH = -h
        self.assertEqual(expectedX, result.x)
        self.assertEqual(expectedY, result.y)
        self.assertEqual(expectedW, result.w)
        self.assertEqual(expectedH, result.h)


class Region2dInserectionTest(unittest.TestCase):
    def test_region1_above_region2_does_not_intersect(self):
        # Setup
        region1 = model.Region2d(10, 10, 10, 10)
        region2 = model.Region2d(10, 25, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertFalse(result)

    def test_region1_below_region2_does_not_intersect(self):
        # Setup
        region1 = model.Region2d(10, 25, 10, 10)
        region2 = model.Region2d(10, 10, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertFalse(result)

    def test_region1_left_of_region2_does_not_intersect(self):
        # Setup
        region1 = model.Region2d(10, 10, 10, 10)
        region2 = model.Region2d(30, 10, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertFalse(result)

    def test_region1_right_of_region2_does_not_intersect(self):
        # Setup
        region1 = model.Region2d(30, 10, 10, 10)
        region2 = model.Region2d(10, 10, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertFalse(result)

    def test_region1_inside_region2_does_intersect(self):
        # Setup
        region1 = model.Region2d(10, 10, 100, 100)
        region2 = model.Region2d(20, 20, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertTrue(result)

    def test_region2_inside_region1_does_intersect(self):
        # Setup
        region1 = model.Region2d(20, 20, 10, 10)
        region2 = model.Region2d(10, 10, 100, 100)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertTrue(result)

    def test_region1_overlaps_region2_does_intersect(self):
        # Setup
        region1 = model.Region2d(20, 20, 10, 10)
        region2 = model.Region2d(20, 15, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertTrue(result)


class Region2dInserectionAnyTest(unittest.TestCase):
    def test_region1_not_in_empty_region_list(self):
        # Setup
        region = model.Region2d(10, 10, 10, 10)

        # Act
        result = model.intersectsAny(region, [])

        # Test
        self.assertFalse(result)

    def test_region1_not_in_any_region(self):
        # Setup
        region1 = model.Region2d(10, 10, 10, 10)
        region2a = model.Region2d(10, 25, 10, 10)
        region2b = model.Region2d(25, 10, 10, 10)

        # Act
        result = model.intersectsAny(region1, [region2a, region2b])

        # Test
        self.assertFalse(result)

    def test_region1_does_intersect_with_a_region(self):
        # Setup
        region1 = model.Region2d(10, 10, 10, 10)
        region2a = model.Region2d(10, 25, 10, 10)
        region2b = model.Region2d(5, 10, 10, 10)

        # Act
        result = model.intersectsAny(region1, [region2a, region2b])

        # Test
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
