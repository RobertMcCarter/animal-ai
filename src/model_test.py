import unittest

import model

class RegionInserectionTest(unittest.TestCase):

    def test_region1_above_region2_does_not_intersect(self):
        # Setup
        region1 = model.Region(10, 10, 10, 10)
        region2 = model.Region(10, 25, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertFalse( result )


    def test_region1_below_region2_does_not_intersect(self):
        # Setup
        region1 = model.Region(10, 25, 10, 10)
        region2 = model.Region(10, 10, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertFalse( result )


    def test_region1_left_of_region2_does_not_intersect(self):
        # Setup
        region1 = model.Region(10, 10, 10, 10)
        region2 = model.Region(30, 10, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertFalse( result )


    def test_region1_right_of_region2_does_not_intersect(self):
        # Setup
        region1 = model.Region(30, 10, 10, 10)
        region2 = model.Region(10, 10, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertFalse( result )


    def test_region1_inside_region2_does_intersect(self):
        # Setup
        region1 = model.Region(10, 10, 100, 100)
        region2 = model.Region(20, 20, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertTrue( result )


    def test_region2_inside_region1_does_intersect(self):
        # Setup
        region1 = model.Region(20, 20, 10, 10)
        region2 = model.Region(10, 10, 100, 100)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertTrue( result )


    def test_region1_overlaps_region2_does_intersect(self):
        # Setup
        region1 = model.Region(20, 20, 10, 10)
        region2 = model.Region(20, 15, 10, 10)

        # Act
        result = model.intersects(region1, region2)

        # Test
        self.assertTrue( result )


class RegionInserectionAnyTest(unittest.TestCase):

    def test_region1_not_in_empty_region_list(self):
        # Setup
        region  = model.Region(10, 10, 10, 10)

        # Act
        result = model.intersectsAny(region, [])

        # Test
        self.assertFalse( result )


    def test_region1_not_in_any_region(self):
        # Setup
        region1  = model.Region(10, 10, 10, 10)
        region2a = model.Region(10, 25, 10, 10)
        region2b = model.Region(25, 10, 10, 10)

        # Act
        result = model.intersectsAny(region1, [region2a, region2b])

        # Test
        self.assertFalse( result )


    def test_region1_does_intersect_with_a_region(self):
        # Setup
        region1  = model.Region(10, 10, 10, 10)
        region2a = model.Region(10, 25, 10, 10)
        region2b = model.Region( 5, 10, 10, 10)

        # Act
        result = model.intersectsAny(region1, [region2a, region2b])

        # Test
        self.assertTrue( result )


if __name__ == '__main__':
    unittest.main()
