from .sar import SAR

import json
import rasterio as rs
import numpy as np
import numpy.typing as npt

from typing import Dict, List
from pathlib import Path



class SARChandrayaan2(SAR):
    path            : Path
    local_path      : Path
    date            : str
    calibrated_path : Path
    config          : Dict[str, bool]


    # from SAR
    _coeffs     : npt.NDArray | None
    _T          : npt.NDArray | None
    _C          : npt.NDArray | None
    calibrated  : bool = False
    device      : str = "cpu"


    def __init__(self, path: Path, local_path: Path, force_load: bool = False, **kwarg) -> None:
        self.path = path
        self.local_path = local_path

        self.date = self.path.name.split("_")[3].split("t")[0]
        self.calibrated_path = self.path / "data" / "calibrated" / self.date
        
        if self.__check_local__() and not force_load:
            self.load(self.local_path)
        else:
            super().__init__(self.__load_coeffs__(), **kwarg)


    def __check_local__(self) -> bool:
        if self.local_path.is_dir():
            config_path = self.local_path / "config.json"
            if not config_path.is_file():
                raise FileNotFoundError(f"Config File not found at location: {config_path}")
            with config_path.open('r') as config_file:
                self.config = json.load(config_file)
            return True
        else:
            return False

    
    def __load_coeffs__(self) -> npt.NDArray:
        coeffs_path = sorted(self.calibrated_path.glob('*sli*.tif'))
        coeffs = list()
        for path in coeffs_path:
            with rs.open(path.__str__()) as src:
                coeffs.append(src.read())
        hh, hv, vh, vv = [coeff[0] + 1j * coeff[1] for coeff in coeffs]
        return np.array([
            [hh, hv],
            [vh, vv]
            ])


    def save(self) -> None:
        super().save(self.local_path)


class Chandrayaan2:
    path            : Path
    local_path      : Path
    date_map        : Dict[str, SARChandrayaan2]

    def __init__(self, path: Path, local_path: Path) -> None:
        self.path = path
        self.local_path = local_path
        self.dateSARMap()

    def dateSARMap(self) -> None:
        sar_data_paths = [child for child in self.path.iterdir() if child.is_dir()]
        sar_data_dates = [path.name.split("_")[3].split("t")[0] for path in sar_data_paths]
        sar_list = [
                SARChandrayaan2(Path(path), self.local_path / date)
                for path, date in zip(sar_data_paths, sar_data_dates)
                ]
        self.date_map = {
                SAR.date : SAR
                for SAR in sar_list
                }

    def get_dirs(self) -> Dict[str, Path | List[Path]]:
        date_map = {
                'BASE': self.path,
                'DATE_MAP': {
                    date: sarimg_data.path
                    for date, sarimg_data in self.date_map.items()
                    }
                }
        return date_map

