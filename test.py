import unittest
from unittest import TestCase
from pathlib import Path

from dir import Dir


BASE_PATH = Path(__file__).resolve().parent


class DirTest(TestCase):
    dir_dict_changed = {
            'config': BASE_PATH / "config_file.json",
            'local': {
                'base': BASE_PATH / ".local",
                'sar_image': BASE_PATH / ".local" / "sar_image",
                'chandrayaan2': BASE_PATH / ".local" / "isro_local_files",
                },
            'data': {
                'base': BASE_PATH / "data",
                'chandrayaan2': BASE_PATH / "data" / "isro_data",
                },
            }


    def setUp(self) -> None:
        self.DirDefault = Dir({})
        self.DirChanged = Dir(self.dir_dict_changed)


    def test_default(self) -> None:
        dir = self.DirDefault
        self.assertEqual(dir.base, BASE_PATH, "Base Path is incorrect")
        self.assertEqual(dir.config, BASE_PATH / "config.json")
        self.assertEqual(dir.local.chandrayaan2, BASE_PATH / ".local" / "chandrayaan2")
        self.assertEqual(dir.data.chandrayaan2, BASE_PATH / "data" / "chandrayaan2")

    def test_changed(self) -> None:
        dir = self.DirChanged
        self.assertEqual(dir.base, BASE_PATH, "Base Path is incorrect")
        self.assertEqual(dir.config, BASE_PATH / "config_file.json")
        self.assertEqual(dir.local.chandrayaan2, BASE_PATH / ".local" / "isro_local_files")
        self.assertEqual(dir.data.chandrayaan2, BASE_PATH / "data" / "isro_data")

    def test_local_set(self) -> None:
        dir = self.DirChanged
        changed_local_dict = {
                'base': BASE_PATH.parent / ".local",
                }
        dir.local.set(**changed_local_dict)
        self.assertEqual(
                dir.local.base,
                BASE_PATH.parent / ".local",
                f"Local base path not correct after change, dir.local.base: {dir.local.base}, but should be {BASE_PATH.parent / '.local'}"
                )
        self.assertEqual(
                dir.local.sar_image,
                BASE_PATH.parent / ".local" / "sar_image",
                f"Incorrect after only local.base change -> dir.local.sar_image: {dir.local.sar_image} ({BASE_PATH / '.local' / 'sar_image'})"
                )

        complete_change_local_dict = {
                'base': BASE_PATH.parent / "local",
                'chandrayaan2': BASE_PATH / ".chandrayaan2"
                }
        dir.local.set(**complete_change_local_dict)
        self.assertEqual(
                dir.local.base,
                BASE_PATH.parent / "local",
                f"Local base path not correct after change, dir.local.base: {dir.local.base}, but should be {BASE_PATH.parent / '.local'}"
                )
        self.assertEqual(
                dir.local.chandrayaan2,
                BASE_PATH / ".chandrayaan2",
                f"Incorrect after local.set() change -> dir.local.chandrayaan2: {dir.local.chandrayaan2} ({BASE_PATH / '.chandrayaan2'})"
                )

        # refresh dir
        self.DirChanged = Dir(self.dir_dict_changed)



if __name__ == '__main__':
    unittest.main()
