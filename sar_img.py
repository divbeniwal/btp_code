import numba_func
import warnings

import numpy as np
import numpy.typing as npt

from dataclasses import dataclass, field
from typing import List, TypeVar


# TODO:
#   - add save and load features

SARImageType = TypeVar('SARImageType', bound='SARImage')


@dataclass
class SARImage:
    HH: npt.NDArray = field(init=True)
    HV: npt.NDArray = field(init=True)
    VH: npt.NDArray = field(init=True)
    VV: npt.NDArray = field(init=True)
    T: npt.NDArray | None = field(default=None, kw_only=True)
    C: npt.NDArray | None = field(default=None, kw_only=True)
    calibrated: bool = field(default=False, kw_only=True, repr=True)
    device: str = field(default="cpu", kw_only=True, repr=True)


    def __post_init__(self) -> None:
        if self.T or self.C:
            self.calibrated = False
            if not self.T:
                self.computeT(device=self.device)
            elif not self.C:
                self.computeC(device=self.device)
        elif self.calibrated:
            warnings.warn("T and C matrix are not computed but 'calibrated' True was provided", category=Warning)


    def computeC(self, device: str | None = None) -> npt.NDArray:
        if not device:
            device = self.device

        if device == "cpu":
            cout = numba_func.computeC_cpu(self.HH, self.HV, self.VH, self.VV)
        elif device == "gpu":
            cout = numba_func.computeC_gpu(self.HH, self.HV, self.VH, self.VV)
        else:
            raise KeyError(f"device: {device}, should be 'cpu' or 'gpu' ")
        self.C11, self.C12, self.C13, self.C21, self.C22, self.C23, self.C31, self.C32, self.C33 = cout
        self.C = np.array([
            [self.C11, self.C12, self.C13],
            [self.C21, self.C22, self.C23],
            [self.C31, self.C32, self.C33]
            ])
        return self.C


    def computeT(self, device: str | None = None) -> npt.NDArray:
        if not device:
            device = self.device

        if device == "cpu":
            tout = numba_func.computeT_cpu(self.HH, self.HV, self.VH, self.VV)
        elif device == "gpu":
            tout = numba_func.computeT_gpu(self.HH, self.HV, self.VH, self.VV)
        else:
            raise KeyError(f"device: {device}, should be 'cpu' or 'gpu' ")
        self.T11, self.T12, self.T13, self.T21, self.T22, self.T23, self.T31, self.T32, self.T33 = tout
        self.T = np.array([
            [self.T11, self.T12, self.T13],
            [self.T21, self.T22, self.T23],
            [self.T31, self.T32, self.T33]
            ])
        return self.T


    def calibrate(self, calibration: int = 10000) -> None:
        if self.calibrated:
            return 
        cal_coeff_list: List[npt.NDArray] = list()
        uncal_coeffs = np.array([self.HH, self.HV, self.VH, self.VV])
        for coeff in uncal_coeffs:
            coeff_real, coeff_im = coeff / calibration
            coeff_im = 1j * coeff_im 
            if np.can_cast(coeff_real.dtype, coeff_im.dtype):
                cal_coeff = np.add(coeff_real, coeff_im, casting="safe")
            else:
                raise Exception("np.can_cast for coeff_real and coeff_im is not safe")
            cal_coeff_list.append(cal_coeff)
            coeff = coeff.astype(np.complex64)
        self.HH, self.HV, self.VH, self.VV = cal_coeff_list


    def copy(self: SARImageType) -> SARImageType:
        return SARImage(self.HH, self.HV, self.VH, self.VV, 
                calibrated=True, T=self.T, 
                C=self.T, device=self.device)


    def multilook_azimuth(self: SARImageType, nmls: int, method: str = 'mean') -> SARImageType:
        return SARImage(
                self._multilook_indi(self.HH, nmls=nmls, method=method),
                self._multilook_indi(self.HV, nmls=nmls, method=method),
                self._multilook_indi(self.VH, nmls=nmls, method=method),
                self._multilook_indi(self.VV, nmls=nmls, method=method),
                calibrated=self.calibrated,
                device=self.device
                )


    def _multilook_indi(self, data: npt.NDArray, nmls: int, method: str = "mean") -> npt.NDArray:
        method_list = ["mean", "median", "mode"]
        if method not in method_list:
            msg = f"un-supported multilook method: {method}. Available methods: {method_list}"
            raise ValueError(msg)

        nmls = int(nmls)
        if nmls == 1:
            return data
        dtype = data
        shape = np.array(self.HH.shape, dtype=int)
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
            coarse_data = self.HH[int(nmls / 2)::nmls, int(1 // 2)::1]
            if coarse_data.shape != (azimuth_size, shape[1]):
                coarse_data = coarse_data[:azimuth_size, :shape[1]]

        coarse_data = np.array(coarse_data, dtype=dtype)
        return coarse_data

