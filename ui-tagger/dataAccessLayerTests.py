"""
Unit tests for the data access layer
"""
import unittest
from model.region2d import ScaledRegion2d
import testData
import dataAccessLayer

import model

class TestLoadImage(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the DAL async loadImage() function"""

    async def test_loadImage_async(self):
        """Ensure that we can correctly load the image asynchronously"""

        # Setup
        testFile = testData.getTestDataFilePath("cat-01.jpg")

        # Action
        image = await dataAccessLayer.loadImage(testFile)

        # Test
        self.assertIsNotNone(image)
        self.assertEqual(image.width, 137)
        self.assertEqual(image.height, 150)


class TestCreateAnnotatedImagesFromDirectory(unittest.TestCase):
    """Unit tests for the createAnnotatedImagesFromDirectory() function"""

    def test_creates_annotation_for_all_three_images_in_order(self):
        testDataDir = testData.getTestDataFolder()

        # Act - run the subject under test
        result = dataAccessLayer.createAnnotatedImagesFromDirectory(testDataDir)

        # Test
        self.assertEqual(30, len(result))
        self.assertEqual("cat-01.jpg", result[0].fileName)
        self.assertEqual("cat-02.jpg", result[1].fileName)
        self.assertEqual("cat-03.jpg", result[2].fileName)


class TestLoadNearbyImages(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the complex DAL loadNearbyImage() function"""

    async def test_loadImage_async(self):
        """Ensure that we can correctly load the image asynchronously"""

        # Setup
        testDataFolder = testData.getTestDataFolder()
        annotations = dataAccessLayer.createAnnotatedImagesFromDirectory(testDataFolder)

        # Action
        targetSize = model.Size2d(500,500)
        await dataAccessLayer.loadNearbyImages(annotations, 10, targetSize)

        # Test - that before index (10) - previous (2) no image is loaded
        for i in range(0,8):
            self.assertIsNone( annotations[i].image, f"Previous image #{i} expected to be None" )

        for i in range(10, 15):
            self.assertIsNotNone( annotations[i].image, f"Image #{i} expected to be NOT None"  )

        # Test - that AFTER index (10) + next (5) no image is loaded
        for i in range(16, len(annotations)):
            self.assertIsNone( annotations[i].image, f"After image #{i} expected to be None"  )



class Region2dSerialization(unittest.TestCase):
    """ Unit tests for the serialization of a Region2d into a JSON dict
        and back again.
    """

    def test_serialize_and_deserialize_returns_same_region2d(self):
        """ Serialize a Region2d and then deserialize it,
            ensuring the results are what we started with
        """
        # Setup
        expectedRegion = model.Region2d(2396, 23, 234, 96)

        # Act - Serialize and then deserialize
        serialized = dataAccessLayer.serializeRegion2dToDict(expectedRegion)
        result = dataAccessLayer.deSerializeRegion2d(serialized)

        # Test
        self.assertEqual(expectedRegion.x, result.x)
        self.assertEqual(expectedRegion.y, result.y)
        self.assertEqual(expectedRegion.w, result.w)
        self.assertEqual(expectedRegion.h, result.h)


class AnnotatedImageSerialization(unittest.TestCase):
    """ Unit tests for the serialization of an AnnotatedImage into a JSON dict
        and back again.
    """

    def test_serialize_and_deserialize_returns_expected_annotatedImage(self):
        """ Serialize a Region2d and then deserialize it,
            ensuring the results are what we started with
        """
        # Setup
        expectedRegion0 = model.Region2d(23,   1, 111, 25)
        expectedRegion1 = model.Region2d(39,  10, 222, 50)
        expectedRegion2 = model.Region2d(96, 100, 333, 75)
        expectedFilePath = "/tmp/somewhere/else.jpg"
        image = model.AnnotatedImage(expectedFilePath)
        image.addRegion( ScaledRegion2d(None, expectedRegion0) )
        image.addRegion( ScaledRegion2d(None, expectedRegion1) )
        image.addRegion( ScaledRegion2d(None, expectedRegion2) )

        # Act - Serialize and then deserialize
        serialized = dataAccessLayer.serializeAnnotatedImageToDict(image)
        result = dataAccessLayer.deSerializeAnnotatedImage(serialized)

        # Test
        self.assertEqual(expectedFilePath, result.filePath)
        self.assertEqual(3, len(result.regions))

        # Test the first region
        self.assertEqual(expectedRegion0.x, result.regions[0].imageRegion.x)
        self.assertEqual(expectedRegion0.y, result.regions[0].imageRegion.y)
        self.assertEqual(expectedRegion0.w, result.regions[0].imageRegion.w)
        self.assertEqual(expectedRegion0.h, result.regions[0].imageRegion.h)

        # Test the second region
        self.assertEqual(expectedRegion1.x, result.regions[1].imageRegion.x)
        self.assertEqual(expectedRegion1.y, result.regions[1].imageRegion.y)
        self.assertEqual(expectedRegion1.w, result.regions[1].imageRegion.w)
        self.assertEqual(expectedRegion1.h, result.regions[1].imageRegion.h)

        # Test the third region
        self.assertEqual(expectedRegion2.x, result.regions[2].imageRegion.x)
        self.assertEqual(expectedRegion2.y, result.regions[2].imageRegion.y)
        self.assertEqual(expectedRegion2.w, result.regions[2].imageRegion.w)
        self.assertEqual(expectedRegion2.h, result.regions[2].imageRegion.h)


if __name__ == '__main__':
    unittest.main()
