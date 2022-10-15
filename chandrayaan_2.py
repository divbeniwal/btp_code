import rasterio as rs

import numpy.typing as npt

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


# TODO: make SAR child class of SARImage
class SAR:
    path: Path
    local_path: Path
    calibrated_data_path: Path
    sarImage: SARImage
    date: str
    
    def __init__(self, path: Path, local_path: Path) -> None:
        self.path = path
        self.local_path = local_path
        self.date = self.path.name.split("_")[3].split("t")[0]
        self.calibrated_data_path = self.path / "data" / "calibrated" / self.date

        # TODO: add if found in local
        coeffs = self.get_scattering_coeff()
        self.sarImage = SARImage(*coeffs, calibrated=False)


    def get_scattering_coeff(self) -> List[npt.NDArray]:
        coeffs_path = sorted(self.calibrated_data_path.glob("*sli*.tif"))
        coeffs: List = list()
        for path in coeffs_path:
            with rs.open(path.__str__()) as src:
                coeffs.append(src.read())
        return coeffs


class Chandrayaan2:
    path: Path
    local_path: Path
    date_map: Dict[str, SAR]

    def __init__(self, path: str, local_path: str) -> None:
        self.path = Path(path)
        self.local_path = Path(local_path)
        self.dateSARMap()


    def dateSARMap(self) -> None:
        sar_data_paths = [child for child in self.path.iterdir() if child.is_dir()]
        SARList = [
                # TODO: change local path
                SAR(Path(path), self.local_path)
                for path in sar_data_paths
                ]
        self.date_map = {
                SAR.date : SAR
                for SAR in SARList
                }


    def get_dirs(self) -> Dict[str, Union[Path, List[Path]]]:
        date_map = {
                'BASE': self.path,
                'DATE_MAP': {
                    date: sarimg_data.path
                    for date, sarimg_data in self.date_map.items()
                    }
                }
        return date_map

