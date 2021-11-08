import unittest
import src.model as model
import src.training_sub_image_extraction as sut


class CreateOutputFilePathTests(unittest.TestCase):
    def test_file_name_when_true(self):
        # Setup
        x = 23
        y = 966
        region = model.TaggedRegion(x, y, 10, 10, True)
        dest_folder = "/data/output"

        image_info = model.ImageInfo(False, "/data/input/foo/bar/test.png", [])

        # Act
        result = sut.createOutputFilePath(dest_folder, image_info, region)

        # Test
        expected = f"{dest_folder}/true/test_0023x0966.png"
        result = result.replace(
            "\\", "/"
        )  # So we can test consistently on any platform
        self.assertEqual(result, expected)


    def test_file_name_when_false(self):
        # Setup
        x = 23
        y = 966
        region = model.TaggedRegion(x, y, 10, 10, False)
        dest_folder = "/data/output"

        image_info = model.ImageInfo(False, "/data/input/foo/bar/test.png", [])

        # Act
        result = sut.createOutputFilePath(dest_folder, image_info, region)

        # Test
        expected = f"{dest_folder}/false/test_0023x0966.png"
        result = result.replace(
            "\\", "/"
        )  # So we can test consistently on any platform
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
