import unittest

# from src import dataAccessLayer

from src import model


class TestAnnotatedImage(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the AnnotatedImage class"""

    async def test_scale_image_creates_scaled_image(self):
        """Ensure that scaling an image with a scale factor actually stores
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

        expectedWidth = int(originalWidth * scale)
        expectedHeight = int(originalHeight * scale)
        self.assertEqual(expectedWidth, sut.scaledImage.width)  # type: ignore
        self.assertEqual(expectedHeight, sut.scaledImage.height)  # type: ignore

    async def test_set_image_to_None_clears_scaled_image_info(self):
        """When we set the image to None the scaled image info should also
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
        """Scaling an image to a size correctly calculates the scale,
        and then scales the image and stores the scale value
        """

        # Setup
        testDataImage = testData.getTestDataFilePath()
        sut = model.AnnotatedImage(testDataImage)
        sut.image = await dataAccessLayer.loadImage(testDataImage)
        originalWidth = sut.image.width
        originalHeight = sut.image.height
        expectedScale = 0.5

        expectedWidth = int(originalWidth * expectedScale)

        # Use a VERY large height so it doesn't impact our scale calculation
        # (which will try and keep the aspect ratio)
        size = model.Size2d(expectedWidth, 5000)

        # Act
        sut.scaleImageForSize(size)

        # Ensure we now have a scaled image
        self.assertAlmostEqual(expectedScale, sut.scale, 2)
        self.assertIsNotNone(sut.scaledImage)

        # Calculate the expected height with the actual scale used
        expectedHeight = int(originalHeight * sut.scale)
        self.assertEqual(expectedWidth, sut.scaledImage.width)  # type: ignore
        self.assertAlmostEqual(expectedHeight, sut.scaledImage.height)  # type: ignore


if __name__ == "__main__":
    unittest.main()
