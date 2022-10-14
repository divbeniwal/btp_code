import rasterio as rs
import numpy as np

from pathlib import Path
from sar_img import SARImage
from typing import List, Union, Dict

from rich.console import Console
from rich.theme import Theme
from rich.traceback import install

install()
LogTheme = Theme({
    "info": "blue",
    "warning": "magenta",
    "danger": "bold red",
    "success": "green"
})
console = Console(theme=LogTheme)


class Chandrayaan_2:
    startup: bool
    dir: str
    dir_path: Path

    files_path_list: List[Path]
    date_map: Dict[str, Path]
    date_mat_map: Dict[str, Union[None, SARImage]]

    def __init__(self, dir: str) -> None:
        self.startup = True
        self.dir = dir
        self.dir_path = Path(dir)
        self.make_date_map()

        # TODO: extract calibration from the config and xml files....
        self.CALIBRATION = 10000

    def make_date_map(self) -> None:
        self.files_path_list = [
            child for child in self.dir_path.iterdir()
            if child.is_dir()
        ]
        self.date_map = {
            self.get_date_from_path(dir): dir
            for dir in self.files_path_list
        }
        if self.startup:
            self.startup = False
            self.date_mat_map = {
                date: None
                for date in self.date_map.keys()
            }
        else:
            for date in self.date_map.keys():
                if date not in self.date_mat_map:
                    self.date_mat_map[date] = None

    def get_sar_img(self, date: str) -> SARImage | None:
        array_list = self.get_array_list(date)
        sar_img = SARImage(*array_list, calibrated=False)

        console.log("calibrating scattering coefficients ... ", style="info")
        sar_img.calibrate(calibration=self.CALIBRATION)
        console.log("done", style="success")

        console.log("Computing T Matrix ... ", style="info")
        tmat = sar_img.computeT()
        console.print("shape of T matrix: ", type(tmat), tmat.shape)
        console.log("done", style="success")
        self.date_mat_map[date] = sar_img

        return sar_img

    def get_array_list(self, date: str) -> List[np.ndarray]:
        dir_path = self.get_calibrateed_data_files(date)
        paths = sorted(dir_path.glob("*sli*.tif"))
        array_list = list()
        for path in paths:
            with rs.open(path.__str__()) as src:
                array_list.append(src.read())
        return array_list

    #    def get_HH(self, date: str):
    #        dir_path = self.get_calibrateed_data_files(date)
    #        files_paths = sorted(dir_path.glob("*sli*.tif"))
    #        hh_path = files_paths[0]
    #        hh = cv.imread(hh_path.as_uri(), cv.IMREAD_UNCHANGED)
    #        print(hh.size)
    #

    def update_paths(self) -> None:
        self.make_date_map()

    def get_dirs(self) -> Dict[str, Union[Path, List[Path]]]:
        dir = {
            'BASE': self.dir_path,
            'DATA_FILES': self.files_path_list
        }
        return dir

    def get_path_by_date(self, date: str) -> Path:
        self.update_paths()
        if date in self.date_map:
            return self.date_map[date]
        else:
            raise KeyError(
                f"date: {date} is not in date_map, you don't have the files or you need to update Chandrayaan_2 class data.")

    def get_calibrateed_data_files(self, date: str) -> Path:
        files_path = self.get_path_by_date(date)
        return files_path / "data" / "calibrated" / date

    def get_date_from_path(self, dir_path: Path) -> str:
        date: str = dir_path.name.split("_")[3].split("t")[0]
        return date

    def get_dates(self) -> List[str]:
        self.update_paths()
        return list(self.date_map.keys())

    def get_paths_for_all_dates(self) -> List[Path]:
        self.update_paths()
        res = [
            self.get_calibrateed_data_files(date)
            for date in self.date_map.keys()
        ]
        return res
