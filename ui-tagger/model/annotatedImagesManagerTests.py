import unittest
import model
import dataAccessLayer
import testData

from .region2d import Size2d


class TestClearImagesOutsideRange(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the clearImagesOutsideRange() function"""

    async def test_loadImage_async(self):
        """Ensure that images outside the given range are cleared from memory"""

        # Setup
        testDataFolder = testData.getTestDataFolder()
        annotations = dataAccessLayer.createAnnotatedImagesFromDirectory(testDataFolder)

        # Our core keep images in memory window
        index = 10
        before = 5
        after = 5

        # Load an image before our keep window
        await dataAccessLayer.loadImageForAnnotation(annotations[2])
        annotations[2].scaleImage(1.0)

        # Load an image in our keep window
        await dataAccessLayer.loadImageForAnnotation(annotations[10])
        annotations[10].scaleImage(1.0)

        # Load an image after our keep window
        await dataAccessLayer.loadImageForAnnotation(annotations[25])
        annotations[25].scaleImage(1.0)

        # Action
        model.clearImagesOutsideRange(annotations, index, before, after)

        # Test that item 10 still has its images
        self.assertIsNotNone( annotations[10].image )
        self.assertIsNotNone( annotations[10].scaledImage )

        # Test - that before index (10-before) no images are loaded
        for i in range(0, index-before):
            self.assertIsNone( annotations[i].image, f"Image #{i} expected to be NOT None"  )

        # Test - that AFTER index (10 + after) no image is loaded
        for i in range(index+after, len(annotations)):
            self.assertIsNone( annotations[i].image, f"After image #{i} expected to be None"  )


class TestAnnotatedImage(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the AnnotatedImage class"""

    async def test_scale_image_creates_scaled_image(self):
        """ Ensure that scaling an image with a scale factor actually stores
            the correctly scaled image and stores the scale itself.
        """

        # Setup
        testDataImage = testData.getTestDataFilePath()
        sut = model.AnnotatedImage(testDataImage)
        sut.image = await dataAccessLayer.loadImage(testDataImage)
        originalWidth = sut.image.width
        originalHeight = sut.image.height
        scale = 0.5

        # Act
        sut.scaleImage(scale)

        # Ensure we now have a scaled image
        self.assertEqual(scale, sut.scale)
        self.assertIsNotNone(sut.scaledImage)

        expectedWidth  = int(originalWidth * scale)
        expectedHeight = int(originalHeight * scale)
        self.assertEqual(expectedWidth, sut.scaledImage.width)   # type: ignore
        self.assertEqual(expectedHeight, sut.scaledImage.height) # type: ignore


    async def test_set_image_to_None_clears_scaled_image_info(self):
        """ When we set the image to None the scaled image info should also
            be cleared
        """

        # Setup
        testDataImage = testData.getTestDataFilePath()
        sut = model.AnnotatedImage(testDataImage)
        sut.image = await dataAccessLayer.loadImage(testDataImage)
        sut.scaleImage(0.5)

        # Ensure out setup is correct and we have scaled image data
        self.assertEqual(0.5, sut.scale)
        self.assertIsNotNone(sut.scaledImage)

        # Act - set the image to None
        sut.image = None

        # Test
        self.assertEqual(0.0, sut.scale)
        self.assertIsNone(sut.scaledImage)


    async def test_scale_image_to_size_creates_scaled_image(self):
        """ Scaling an image to a size correctly calculates the scale,
            and then scales the image and stores the scale value
        """

        # Setup
        testDataImage = testData.getTestDataFilePath()
        sut = model.AnnotatedImage(testDataImage)
        sut.image = await dataAccessLayer.loadImage(testDataImage)
        originalWidth = sut.image.width
        originalHeight = sut.image.height
        expectedScale = 0.5

        expectedWidth  = int(originalWidth * expectedScale)

        # Use a VERY large height so it doesn't impact our scale calculation
        # (which will try and keep the aspect ratio)
        size = Size2d(expectedWidth, 5000)

        # Act
        sut.scaleImageForSize(size)

        # Ensure we now have a scaled image
        self.assertAlmostEqual(expectedScale, sut.scale, 2)
        self.assertIsNotNone(sut.scaledImage)

        # Calculate the expected height with the actual scale used
        expectedHeight = int(originalHeight * sut.scale)
        self.assertEqual(expectedWidth, sut.scaledImage.width)   # type: ignore
        self.assertAlmostEqual(expectedHeight, sut.scaledImage.height) # type: ignore



if __name__ == '__main__':
    unittest.main()
