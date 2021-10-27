import unittest

import model
import grouping as sut

class GroupTest(unittest.TestCase):

    def test_two_groups_different_path(self):
        # Setup
        # Different path, same file name with correct #
        image1 = model.ImageInfo(False, "unit/testing/data/test/foo_0001.jpg", [])
        image2 = model.ImageInfo(False, "unit/testing/data/test/foo_0002.jpg", [])
        image3 = model.ImageInfo(False, "unit/testing/data/test/foo_0003.jpg", [])
        image4 = model.ImageInfo(False, "unit/testing/data/diff/foo_0004.jpg", [])
        input = [ image1, image2, image3, image4 ]

        # Act
        result = sut.groupImages(input)

        # Test
        self.assertEqual( len(result), 2 )
        self.assertEqual( result[0], [image1, image2, image3] )
        self.assertEqual( result[1], [image4] )


    def test_two_groups_different_index(self):
        # Setup
        # Different path, same file name with correct #
        image1 = model.ImageInfo(False, "unit/testing/data/test/foo_0001.jpg", [])
        image2 = model.ImageInfo(False, "unit/testing/data/test/foo_0002.jpg", [])
        image3 = model.ImageInfo(False, "unit/testing/data/test/foo_0010.jpg", [])
        image4 = model.ImageInfo(False, "unit/testing/data/test/foo_0011.jpg", [])
        input = [ image1, image2, image3, image4 ]

        # Act
        result = sut.groupImages(input)

        # Test
        self.assertEqual( len(result), 2 )
        self.assertEqual( result[0], [image1, image2] )
        self.assertEqual( result[1], [image3, image4] )


if __name__ == '__main__':
    unittest.main()
