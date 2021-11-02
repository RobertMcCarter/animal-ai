import unittest

import model
import training_image_creation as sut

class CreateSmallerImageOffsetsTests(unittest.TestCase):

    def test_results_when_image_size_is_exact_multiple_of_block_size(self):
        # No setup needed
        # Act
        result = sut.createSmallerSubImageOffsets(block_size=10, image_size=40)
        result = list(result)

        # Test
        expected = [0, 10, 20, 30]
        self.assertEqual( result , expected)


    def test_results_when_image_size_is_not_multiple_of_block_size(self):
        # No setup needed

        # Act
        result = sut.createSmallerSubImageOffsets(block_size=10, image_size=45)
        result = list(result)

        # Test
        # Note that we expect the last two results to overlap with a block size of 10,
        # but we don't leave any pixels on the table
        expected = [0, 10, 20, 30, 35]
        self.assertEqual( result , expected)



class CreateSmallerSubImageRegions(unittest.TestCase):

    def test_results_when_image_size_is_exact_multiple_of_block_size(self):
        # No setup needed
        # Act
        result = sut.createSmallerSubImageRegions(block_size=model.Size(10,5), image_size=model.Size(20,10))
        result = list(result)

        # Test
        expected = [
            model.Region(x= 0, y=0, w=10, h=5),
            model.Region(x=10, y=0, w=10, h=5),

            model.Region(x= 0, y=5, w=10, h=5),
            model.Region(x=10, y=5, w=10, h=5),
        ]
        self.assertEqual( result , expected)


    def test_results_when_image_size_is_not_multiple_of_block_size(self):
        # No setup needed
        # Act
        result = sut.createSmallerSubImageRegions(block_size=model.Size(10,5), image_size=model.Size(25,12))
        result = list(result)

        # Test
        expected = [
            model.Region(x= 0, y=0, w=10, h=5),
            model.Region(x=10, y=0, w=10, h=5),
            model.Region(x=15, y=0, w=10, h=5),

            model.Region(x= 0, y=5, w=10, h=5),
            model.Region(x=10, y=5, w=10, h=5),
            model.Region(x=15, y=5, w=10, h=5),

            model.Region(x= 0, y=7, w=10, h=5),
            model.Region(x=10, y=7, w=10, h=5),
            model.Region(x=15, y=7, w=10, h=5),
        ]
        self.assertEqual( result , expected)


if __name__ == '__main__':
    unittest.main()
