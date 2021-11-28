"""
Unit tests for the data access layer
"""
import os
import unittest
import tempfile

from .testData import getTestDataFolder, getTestDataFilePath
import tagger_ui.data_access_layer as sut

import src.model as model
import tagger_ui.ui_model as uiModel


class TestingAnnotatedImagesDeSerialization(unittest.TestCase):
    def assertRegionsEqual(
        self, region1: model.Region2d | None, region2: model.Region2d | None
    ) -> bool:
        if region1 is None and region2 is None:
            return True
        if region1 is None or region2 is None:
            return False

        self.assertEqual(region1.x, region2.x)
        self.assertEqual(region1.y, region2.y)
        self.assertEqual(region1.w, region2.w)
        self.assertEqual(region1.h, region2.h)
        return True

    def assertScaledRegionsEqual(
        self, region1: uiModel.ScaledRegion2d, region2: uiModel.ScaledRegion2d
    ) -> bool:
        return self.assertRegionsEqual(region1.imageRegion, region2.imageRegion)

    def assertAnnotatedImagesEqual(
        self, ai1: uiModel.AnnotatedImage, ai2: uiModel.AnnotatedImage
    ) -> None:
        """Helper function that tests that the given image info object is converted correctly
        into the given annotated image result

        Args:
            info (model.ImageInfo): The input image info to test against
            result (uiModel.AnnotatedImage): The resulting converted annotated image to test
        """
        assert ai2 is not None
        self.assertEqual(ai1.filePath, ai2.filePath)
        self.assertEqual(ai1.isTagged, ai2.isTagged)
        self.assertEqual(len(ai1.regions), len(ai2.regions))

        for i in range(len(ai1.regions)):
            region1 = ai1.regions[i]
            region2 = ai2.regions[i]
            self.assertScaledRegionsEqual(region1, region2)

    def assertImageInfoEqualsAnnotatedImage(
        self, input: model.ImageInfo, output: uiModel.AnnotatedImage
    ) -> None:
        """Helper function that tests that the given image info object is converted correctly
        into the given annotated image result

        Args:
            info (model.ImageInfo): The input image info to test against
            result (uiModel.AnnotatedImage): The resulting converted annotated image to test
        """
        assert output is not None
        self.assertEqual(input.filePath, output.filePath)
        self.assertEqual(input.tagged, output.isTagged)
        self.assertEqual(len(input.regions), len(output.regions))

        for i in range(len(input.regions)):
            expectedRegion = input.regions[i]
            convertedRegion = output.regions[i]
            actualImageRegion = convertedRegion.imageRegion
            assert actualImageRegion is not None
            self.assertRegionsEqual(expectedRegion, actualImageRegion)


class TestConvertImageInfoToViewModel(TestingAnnotatedImagesDeSerialization):
    """Unit tests for the converting between ImageInfo and AnnotatedImage"""

    def test_converts_ImageInfo_into_AnnotatedImage(self):
        # Setup
        expectedPath = "/data/foo/bar/unit-testing/image1234.jpg"
        regions = [
            model.Region2d(1, 2, 3, 4),
            model.Region2d(10, 11, 12, 13),
        ]
        imageInfo = model.ImageInfo(True, expectedPath, regions)

        # Act
        result = sut.convertImageInfoToAnnotatedImage(imageInfo)

        # Test
        self.assertImageInfoEqualsAnnotatedImage(imageInfo, result)

    def test_converts_AnnotatedImage_into_ImageInfo(self):
        # Setup
        expectedPath = "/data/foo/bar/unit-testing/image1234.jpg"

        annotatedImage = uiModel.AnnotatedImage(expectedPath)
        annotatedImage.addRegion(
            uiModel.ScaledRegion2d(imageRegion=model.Region2d(1, 2, 3, 4))
        )
        annotatedImage.addRegion(
            uiModel.ScaledRegion2d(imageRegion=model.Region2d(10, 11, 12, 13))
        )

        # Act
        result = sut.convertAnnotatedImageToImageInfo(annotatedImage)

        # Test
        self.assertImageInfoEqualsAnnotatedImage(result, annotatedImage)


class TestConvertImagesCollectionToAnnoatedImageManager(
    TestingAnnotatedImagesDeSerialization
):
    """Unit tests for the convertImagesCollectionToViewModel() function"""

    def test_converts_ImagesCollection_into_AnnotatedImageManager(self):
        # Setup
        expectedPath1 = getTestDataFilePath("cat-01.jpg")
        expectedPath2 = getTestDataFilePath("cat-02.jpg")
        expectedPath3 = getTestDataFilePath("cat-03.jpg")

        imageInfo1 = model.ImageInfo(
            True,
            expectedPath1,
            [
                model.Region2d(1, 2, 3, 4),
                model.Region2d(10, 11, 12, 13),
            ],
        )
        imageInfo2 = model.ImageInfo(
            True,
            expectedPath2,
            [
                model.Region2d(23, 57, 20, 50),
                model.Region2d(20, 21, 120, 30),
                model.Region2d(200, 150, 60, 40),
            ],
        )
        imageInfo3 = model.ImageInfo(True, expectedPath3, [])
        images = [imageInfo1, imageInfo2, imageInfo3]

        expectedMaxViewed = 2
        expectedCurrentlyViewed = 1
        collection = model.ImagesCollection(
            expectedMaxViewed, expectedCurrentlyViewed, images
        )

        # Act
        result = sut.convertImagesCollectionToAnnotatedImagesManager(collection)

        # Test
        assert result is not None
        self.assertEqual(expectedMaxViewed, result.maxViewed)
        for i in range(len(images)):
            imageInfo = images[i]
            annotatedImage = result.images[i]
            self.assertImageInfoEqualsAnnotatedImage(imageInfo, annotatedImage)

    def test_converts_AnnotatedImageManager_into_ImagesCollection(self):
        # Setup
        expectedPath1 = getTestDataFilePath("cat-01.jpg")
        annotatedImage1 = uiModel.AnnotatedImage(expectedPath1)
        annotatedImage1.addRegion(
            uiModel.ScaledRegion2d(imageRegion=model.Region2d(1, 2, 3, 4))
        )

        expectedPath2 = getTestDataFilePath("cat-02.jpg")
        annotatedImage2 = uiModel.AnnotatedImage(expectedPath2)
        annotatedImage2.addRegion(
            uiModel.ScaledRegion2d(imageRegion=model.Region2d(10, 11, 12, 13))
        )
        annotatedImages = [annotatedImage1, annotatedImage2]

        expectedMaxViewed = 1
        manager = uiModel.AnnotatedImagesManager(annotatedImages)
        manager.maxViewed = expectedMaxViewed

        # Act
        result = sut.convertAnnotatedImagesManagerToImagesCollection(manager)

        # Test
        assert result is not None
        self.assertEqual(expectedMaxViewed, result.maxViewed)
        for i in range(len(annotatedImages)):
            annotatedImage = annotatedImages[i]
            imageInfo = result.images[i]
            self.assertImageInfoEqualsAnnotatedImage(imageInfo, annotatedImage)


class TestCreateAnnotatedImagesFromDirectory(unittest.TestCase):
    """Unit tests for the createAnnotatedImagesFromDirectory() function"""

    def test_creates_annotation_for_all_three_images_in_order(self):
        testDataDir: str = getTestDataFolder()

        # Act - run the subject under test
        result = sut.createAnnotatedImagesFromDirectory(testDataDir)

        # Test
        self.assertEqual(30, len(result))
        self.assertEqual("cat-01.jpg", result[0].fileName)
        self.assertEqual("cat-02.jpg", result[1].fileName)
        self.assertEqual("cat-03.jpg", result[2].fileName)


class AnnotatedImageSerialization(TestingAnnotatedImagesDeSerialization):
    """Unit tests for the serialization of an AnnotatedImage into a JSON file and then back again"""

    def test_serialize_and_deserialize_returns_same(self):
        """Serialize a Region2d and then deserialize it,
        ensuring the results are what we started with
        """
        # Setup
        expectedPath1 = getTestDataFilePath("cat-01.jpg")
        annotatedImage1 = uiModel.AnnotatedImage(expectedPath1)
        annotatedImage1.addRegion(
            uiModel.ScaledRegion2d(imageRegion=model.Region2d(1, 2, 3, 4))
        )

        expectedPath2 = getTestDataFilePath("cat-02.jpg")
        annotatedImage2 = uiModel.AnnotatedImage(expectedPath2)
        annotatedImage2.addRegion(
            uiModel.ScaledRegion2d(imageRegion=model.Region2d(10, 11, 12, 13))
        )
        annotatedImages = [annotatedImage1, annotatedImage2]

        expectedMaxViewed = 1
        manager = uiModel.AnnotatedImagesManager(annotatedImages)
        manager.maxViewed = expectedMaxViewed

        # Act!
        _, file_name = tempfile.mkstemp(suffix=".json")
        try:
            sut.saveAnnotatedImagesToJsonFile(file_name, manager)
            (result, _) = sut.loadAnnotatedImagesFromJsonFile(file_name)

            # Test
            self.assertEqual(expectedMaxViewed, result.maxViewed)
            self.assertEqual(2, len(result.images))
            for i in range(len(annotatedImages)):
                expectedImage = annotatedImages[i]
                actualImage = result.images[i]
                self.assertAnnotatedImagesEqual(expectedImage, actualImage)

        finally:
            try:
                os.remove(file_name)
            except:
                print("Failed to remove test file:", file_name)


if __name__ == "__main__":
    unittest.main()
