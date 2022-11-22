from __future__ import annotations

import json
import numpy as np
import numpy.typing as npt

from typing import List, Dict
from pathlib import Path

from sar import computations


# TODO: Ploting
# TODO: Add logging (only print statements for now or using rich)
# TODO: compute functions
# TODO: add lazy python for T and C matrices

class SAR:
    _coeffs     : npt.NDArray
    _T          : npt.NDArray | None
    _C          : npt.NDArray | None
    calibrated  : bool = False
    device      : str = "cpu"


    def __init__(
            self,
            coeff: npt.NDArray,
            calibrated: bool = False,
            device: str = "cpu",
            T: npt.NDArray | None = None,
            C: npt.NDArray | None = None
            ) -> None:
        
        x, y, *_ = coeff.shape
        if len(coeff.shape) == 4 and x == 2 and y == 2:
            self._coeffs = coeff
        else:
            raise ValueError(f"the shape of coeff should be of the form (2, 2, x, y) [given shape -> {coeff.shape}]")

        self.calibrated = calibrated
        self.device = device
        self._T = T
        self._C = C
    

    def load(self, path: Path) -> None:
        if path.is_dir():
            config_path = path / "config.json"
            if not config_path.is_file():
                raise FileNotFoundError(f"Config File not found at localtions: {config_path}")
            with config_path.open('r') as config_file:
                config = json.load(config_file)

            self._T = None
            self._C = None

            with (path / "coeffs.npy").open('rb') as coeffs_file:
                self._coeffs = np.load(coeffs_file)
            if config['t_mat']:
                with (path / "t_mat.npy").open('rb') as t_file:
                    self._T = np.load(t_file)
            if config['c_mat']:
                with (path / "c_mat.npy").open('rb') as c_file:
                    self._C = np.load(c_file)

        else:
            raise ValueError(f"path: {path} is not a valid directory.")


    @property
    def T(self) -> npt.NDArray:
        if self._T is not None:
            return self._T
        else:
            raise ValueError(f"T matrix is not computed")


    @property
    def C(self) -> npt.NDArray:
        if self._C:
            return self._C
        else:
            raise ValueError(f"C matrix is not computed")


    def copy(self: SAR) -> SAR:
        return SAR(
                self._coeffs,
                calibrated=self.calibrated,
                device=self.device,
                T=self._T,
                C=self._C
                )


    def computeC(self) -> None:
        # TODO: complete this function
        self._C = np.arange(0, 36).reshape([3, 3, 2, 2])


    def computeT(self) -> None:
        if self._T is not None:
            return 
        a, b, x, y = self._coeffs.shape
        self._T = np.empty([3, 3, x, y], dtype=self._coeffs.dtype)
        if self.device == "cpu":
            computations.computeT_from_coeffs_cpu(self._coeffs, self._T)
        elif self.device == "gpu":
            computations.computeT_from_coeffs_gpu(self._coeffs, self._T)
        else:
            raise ValueError(f"Device: {self.device} is not a valid device (should be 'cpu' or 'gpu').")


    def __getattr__(self, attr) -> npt.NDArray:
        # get scattering coefficients elements
        coeffs_dict = {
                "HH": (0, 0),
                "HV": (0, 1),
                "VH": (1, 0),
                "VV": (1, 1)
                }
        if attr in coeffs_dict:
            i, j = coeffs_dict[attr]
            return self._coeffs[i, j, :, :]

        # get matrices elements
        for i in range(1, 4):
            for j in range(1, 4):
                if attr == f"T{i}{j}":
                    if self._T is not None:
                        return self._T[i - 1, j - 1, :, :]
                    else:
                        raise ValueError(f"T matrix is not computed")
                elif attr == f"C{i}{j}":
                    if self._C is not None:
                        return self._C[i - 1, j - 1, :, :]
                    else:
                        raise ValueError(f"C matrix is not computed")
        raise AttributeError(f"Attribute {attr} does not exits")


    def multilook_azimuth(self: SAR, nmls: int, method: str = 'mean') -> SAR:
        coeffs: List[List[npt.NDArray | None]] = [
            [None, None],
            [None, None]
        ]
        for i in range(2):
            for j in range(2):
                coeffs[i][j] = self._multilook_indi(
                        self._coeffs[i, j, :, :], nmls=nmls, method=method)
        return SAR(
                np.array(coeffs),
                calibrated=self.calibrated,
                device=self.device
                )


    def _multilook_indi(self, data: npt.NDArray, nmls: int, method: str = "mean") -> npt.NDArray:
        method_list = ["mean", "median", "mode", "nearest"]
        if method not in method_list:
            msg = f"un-supported multilook method: {method}. Available methods: {method_list}"
            raise ValueError(msg)

        nmls = int(nmls)
        if nmls == 1:
            return data
        dtype = data.dtype
        shape = np.array(data.shape, dtype=int)
        azimuth_size = shape[0] // nmls

        if method in ['mean', 'median']:
            new_shape = np.floor(shape / (nmls, 1)).astype(int) * (nmls, 1)
            crop_data = data[:new_shape[0], :new_shape[1]]

            temp = crop_data.reshape((new_shape[0] // nmls, nmls, new_shape[1], 1))

            if method == 'mean':
                coarse_data = np.nanmean(temp, axis=(1, 3))
            else:
                coarse_data = np.nanmedian(temp, axis=(1, 3))
            
        elif method == 'nearest':
            coarse_data = data[int(nmls / 2)::nmls, int(1 // 2)::1]
            if coarse_data.shape != (azimuth_size, shape[1]):
                coarse_data = coarse_data[:azimuth_size, :shape[1]]

        coarse_data = np.array(coarse_data, dtype=dtype)
        return coarse_data


    def crop_new(self: SAR, margins: List[int]) -> SAR:
        """
        Crops the Image and returns a new SARImage object 
        
        Parameters
        ----------
        margins: Tuple[int]
            margins define the boundries along which the image will be croped.
            Example:
                margins=(r1, r2, c1, c2) is a valid input
                r1, r2 being rows and c1, c2 being columns

        Returns
        -------
        SAR

        """
        if len(margins) == 4:
            r1, r2, c1, c2 = margins
            coeffs = self._coeffs[:, :, r1:r2, c1:c2]
            T = None
            C = None
            if self._T is not None:
                T = self._T[:, :, r1:r2, c1:c2]
            if self._C:
                C = self._C[:, :, r1:r2, c1:c2]
            return SAR(
                    coeffs,
                    calibrated=self.calibrated,
                    device=self.device,
                    T=T,
                    C=C
                    )
        else:
            raise ValueError(f"size of margins should be 4, but got margin: {margins}")

    def save(self, path: Path) -> None:
        """
        Save the scattering coefficients along with T and C matrices if computed,
        for easy loading.
        """
        if not path.is_dir():
            path.mkdir(parents=True)
        config_path = path / "config.json"
        coeffs_path = path / "coeffs.npy"
        t_path = path / "t_mat.npy" 
        c_path = path / "c_mat.npy" 
        config: Dict[str, bool] = {
                'calibrated': self.calibrated,
                'config': True,
                'coeffs': True,
                't_mat': False,
                'c_mat': False
                }

        with coeffs_path.open('wb') as coeffs_file:
            np.save(coeffs_file, self._coeffs)
        if self._T is not None:
            config['t_mat'] = True
            with t_path.open('wb') as t_file:
                np.save(t_file, self._T)
        if self._C:
            config['c_mat'] = True
            with c_path.open('wb') as c_file:
                np.save(c_file, self._C)
        with config_path.open('w') as config_file:
            json.dump(config, config_file, indent=4)


