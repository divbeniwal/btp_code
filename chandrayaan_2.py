import json
import rasterio as rs

import numpy as np
import numpy.typing as npt

from pathlib import Path
from sar_img import SARImage
from typing import List, Union, Dict
from dataclasses import dataclass, field


@dataclass
class SAR(SARImage):
    path:                   Path = field(init=True)
    local_path:             Path = field(init=True)
    force_load:             bool = field(init=True, default=False)
    calibrated_data_path:   Path = field(init=False)
    date:                   str = field(init=False)
    local_save_paths:       Dict[str, Path] = field(init=False, default_factory=dict, repr=False)
    configs:                Dict[str, bool | str] = field(init=False, default_factory=dict, repr=False)

    # from SARImage
    HH:         npt.NDArray = field(init=False, repr=False)
    HV:         npt.NDArray = field(init=False, repr=False)
    VH:         npt.NDArray = field(init=False, repr=False)
    VV:         npt.NDArray = field(init=False, repr=False)
    T:          npt.NDArray | None = field(default=None, kw_only=True, repr=False)
    C:          npt.NDArray | None = field(default=None, kw_only=True, repr=False)
    calibrated: bool = field(default=False, kw_only=True, repr=True)
    device:     str = field(default="cpu", kw_only=True, repr=True)

    # TODO: auto make local numpy files

    def __post_init__(self) -> None:
        self.date = self.path.name.split("_")[3].split("t")[0]
        self.calibrated_data_path = self.path / "data" / "calibrated" / self.date
        self.local_save_paths = {
                'scattering_coeffs' : self.local_path / "scattering_coeffs.npy",
                't_matrix'          : self.local_path / "t_matrix.npy",
                'c_matrix'          : self.local_path / "c_matrix.npy",
                'config'            : self.local_path / "config.json"
                }

        # check for config_file and extract self.configs
        self.__get_configs__()

        # loading sar image coeffs and matrices
        if self.force_load or not self.check_local_files():
            self.HH, self.HV, self.VH, self.VV = self.get_scattering_coeff()
            super().__post_init__()
        else:
            self.calibrated = True


    def check_local_files(self) -> bool:
        """
        Checks if numpy arrays are saved in the local files folder
        If they are then it loads those arrays and returns True
        otherwise False
        """
        if not self.configs['save']:
            return False

        # get coeffs
        if self.local_save_paths['scattering_coeffs'].is_file():
            with open(self.local_save_paths['scattering_coeffs'], 'rb') as coeffs_file:
                self.HH = np.load(coeffs_file)
                self.HV = np.load(coeffs_file)
                self.VH = np.load(coeffs_file)
                self.VV = np.load(coeffs_file)
        else:
            raise FileNotFoundError(f"numpy save file: {self.local_save_paths['scattering_coeffs'].__str__()} not found")

        # get matrices
        if self.configs.get('t_matrix', False) and self.local_save_paths['t_matrix'].is_file():
            with open(self.local_save_paths['t_matrix'], 'rb') as t_file:
                self.T = np.load(t_file)
        if self.configs.get('c_matrix', False) and self.local_save_paths['c_matrix'].is_file():
            with open(self.local_save_paths['c_matrix'], 'rb') as c_file:
                self.C = np.load(c_file)
        return True

    
    def get_scattering_coeff(self) -> List[npt.NDArray]:
        """
        Loads the scattering coefficients from the GeoTif files
        """
        coeffs_path = sorted(self.calibrated_data_path.glob("*sli*.tif"))
        coeffs: List = list()
        for path in coeffs_path:
            with rs.open(path.__str__()) as src:
                coeffs.append(src.read())
        return coeffs


    def save(self, path: Path | None = None) -> None:
        """
        Save the sacttering coefficients along with T and C matrices 
        if the data is calibrated.
        """
        if not self.calibrated:
            raise Exception("coeffs are not calibrated, please calibrat them first or change self.calibrated to True")
        if not path:
            coeffs_path, t_path, c_path, config_path = self.local_save_paths.values()
            local_path: Path = config_path.parent
        else:
            local_path: Path = path
            coeffs_path, t_path, c_path, config_path = [
                    path / "scattering_coeffs",
                    path / "t_matrix",
                    path / "c_path",
                    path / "config.json"
                    ]

        if not local_path.is_dir():
            local_path.mkdir(parents=True)


        with open(coeffs_path, 'wb') as coeffs_file:
            for array in (self.HH, self.HV, self.VH, self.VV):
                np.save(coeffs_file, array)
        if self.T:
            with open(t_path, 'wb') as t_file:
                    np.save(t_file, self.T)
                    self.configs['t_matrix'] = True
        if self.C:
            with open(c_path, 'wb') as c_file:
                np.save(c_file, self.C)
                self.configs['c_matrix'] = True
        
        self.configs['save'] = True
        with config_path.open('w') as config_file:
            json.dump(self.configs, config_file, indent=4)



    def __get_configs__(self) -> None:
        config_path = self.local_save_paths['config']
        if not config_path.is_file():
            if not config_path.parent.is_dir():
                config_path.parent.mkdir(parents=True)
            if not config_path.is_file():
                config_path.touch()
            with config_path.open('w') as config_file:
                self.configs = {
                        'save': False
                        }
                json.dump(self.configs, config_file, indent=4)
        else:
            with config_path.open('r') as config_file:
                self.configs = json.load(config_file)





class Chandrayaan2:
    path: Path
    local_path: Path
    date_map: Dict[str, SAR]

    def __init__(self, path: Path, local_path: Path) -> None:
        self.path = path
        self.local_path = local_path
        self.dateSARMap()


    def dateSARMap(self) -> None:
        sar_data_paths = [child for child in self.path.iterdir() if child.is_dir()]
        sar_data_dates = [path.name.split("_")[3].split("t")[0] for path in sar_data_paths]
        sar_list = [
                # TODO: change local path
                SAR(Path(path), self.local_path / date)
                for path, date in zip(sar_data_paths, sar_data_dates)
                ]
        self.date_map = {
                SAR.date : SAR
                for SAR in sar_list
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

