import unittest
import pathlib
import src.model as model
import src.data_serialization_json as sut


class LoadAnimalsJson(unittest.TestCase):
    def test_loads_animals_json(self):
        # Setup
        test_data_file = pathlib.Path(__file__).parent / "_test_animals.json"

        # Act
        result = sut.loadAnimalsJson(str(test_data_file))

        # Test
        self.assertEqual(result.maxViewed, 5508)
        self.assertEqual(len(result.images), 2)

        expected1 = model.ImageInfo(False, "D:\\data\\test\\STC_2020.JPG", [])
        expected2 = model.ImageInfo(
            True,
            "D:\\data\\test\\STC_2021.JPG",
            [model.Region2d(x=0, y=251, w=78, h=222)],
        )

        self.assertEqual(result.images[0], expected1)
        self.assertEqual(result.images[1], expected2)


if __name__ == "__main__":
    unittest.main()
