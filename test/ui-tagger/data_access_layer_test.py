"""
Unit tests for the data access layer
"""
import unittest

from .testData import getTestDataFolder, getTestDataFilePath
import tagger_ui.data_access_layer as sut

import src.model as model
import tagger_ui.ui_model as uiModel


class TestingAnnotatedImagesDeSerialization(unittest.TestCase):
    def assertImageInfoToAnnotatedImageConvertedCorrectly(
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
            self.assertEqual(expectedRegion.x, actualImageRegion.x)
            self.assertEqual(expectedRegion.y, actualImageRegion.y)
            self.assertEqual(expectedRegion.w, actualImageRegion.w)
            self.assertEqual(expectedRegion.h, actualImageRegion.h)


class TestConvertImageInfoToViewModel(TestingAnnotatedImagesDeSerialization):
    """Unit tests for the convertImageInfoToViewModel() function"""

    def test_converts_ImageInfo_into_AnnotatedImage(self):
        # Setup
        expectedPath = "/data/foo/bar/unit-testing/image1234.jpg"
        regions = [
            model.Region2d(1, 2, 3, 4),
            model.Region2d(10, 11, 12, 13),
        ]
        imageInfo = model.ImageInfo(True, expectedPath, regions)

        # Act
        result = sut.convertImageInfoToViewModel(imageInfo)

        # Test
        self.assertImageInfoToAnnotatedImageConvertedCorrectly(imageInfo, result)


class TestConvertImagesCollectionToViewModel(TestingAnnotatedImagesDeSerialization):
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
        collection = model.ImagesCollection(expectedMaxViewed, images)

        # Act
        result = sut.convertImagesCollectionToViewModel(collection)

        # Test
        assert result is not None
        self.assertEqual(expectedMaxViewed, result.maxViewed)
        for i in range(len(images)):
            imageInfo = images[i]
            outputAnnotatedImage = result.images[i]
            self.assertImageInfoToAnnotatedImageConvertedCorrectly(
                imageInfo, outputAnnotatedImage
            )


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


# class AnnotatedImageSerialization(unittest.TestCase):
#     """Unit tests for the serialization of an AnnotatedImage into a JSON dict
#     and back again.
#     """

#     def test_serialize_and_deserialize_returns_expected_annotatedImage(self):
#         """Serialize a Region2d and then deserialize it,
#         ensuring the results are what we started with
#         """
#         # Setup
#         expectedRegion0 = model.Region2d(23, 1, 111, 25)
#         expectedRegion1 = model.Region2d(39, 10, 222, 50)
#         expectedRegion2 = model.Region2d(96, 100, 333, 75)
#         expectedFilePath = "/tmp/somewhere/else.jpg"
#         image = uiModel.AnnotatedImage(expectedFilePath)
#         image.addRegion(uiModel.ScaledRegion2d(None, expectedRegion0))
#         image.addRegion(uiModel.ScaledRegion2d(None, expectedRegion1))
#         image.addRegion(uiModel.ScaledRegion2d(None, expectedRegion2))

#         # Act - Serialize and then deserialize
#         serialized = sut.serializeAnnotatedImageToDict(image)
#         result = sut.deSerializeAnnotatedImage(serialized)

#         # Test
#         self.assertEqual(expectedFilePath, result.filePath)
#         self.assertEqual(3, len(result.regions))

#         # Test the first region
#         self.assertEqual(expectedRegion0.x, result.regions[0].imageRegion.x)
#         self.assertEqual(expectedRegion0.y, result.regions[0].imageRegion.y)
#         self.assertEqual(expectedRegion0.w, result.regions[0].imageRegion.w)
#         self.assertEqual(expectedRegion0.h, result.regions[0].imageRegion.h)

#         # Test the second region
#         self.assertEqual(expectedRegion1.x, result.regions[1].imageRegion.x)
#         self.assertEqual(expectedRegion1.y, result.regions[1].imageRegion.y)
#         self.assertEqual(expectedRegion1.w, result.regions[1].imageRegion.w)
#         self.assertEqual(expectedRegion1.h, result.regions[1].imageRegion.h)

#         # Test the third region
#         self.assertEqual(expectedRegion2.x, result.regions[2].imageRegion.x)
#         self.assertEqual(expectedRegion2.y, result.regions[2].imageRegion.y)
#         self.assertEqual(expectedRegion2.w, result.regions[2].imageRegion.w)
#         self.assertEqual(expectedRegion2.h, result.regions[2].imageRegion.h)


if __name__ == "__main__":
    unittest.main()
