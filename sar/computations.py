import numpy as np
import numpy.typing as npt
from numba import jit

__cupy_import__ = False


@jit(nopython=True, parallel=True, fastmath=True, nogil=True)
def computeT_from_coeffs_cpu(coeffs: npt.NDArray[np.complex64], t: npt.NDArray[np.complex64]) -> None:
    hh = coeffs[0, 0, :, :]
    hv = coeffs[0, 1, :, :]
    vh = coeffs[1, 0, :, :]
    vv = coeffs[1, 1, :, :]

    t[0, 0, :, :] = 0.5 * np.square(np.abs(hh + vv))
    t[0, 1, :, :] = 0.5 * (hh + vv) * np.conj(hh - vv)
    t[0, 2, :, :] = (hh + vv) * np.conj(hv)
    t[1, 0, :, :] = 0.5 * (hh - vv) * np.conj(hh + vv)
    t[1, 1, :, :] = 0.5 * np.square(np.abs(hh - vv))
    t[1, 2, :, :] = (hh + vv) * np.conj(hv)
    t[2, 0, :, :] = np.conj(hh + vv) * hv
    t[2, 1, :, :] = np.conj(hh - vv) * hv
    t[2, 2, :, :] = 2 * np.square(np.abs(hv))



def computeT_from_coeffs_gpu(coeffs: npt.NDArray[np.complex64], t:npt.NDArray[np.complex64]) -> npt.NDArray[np.complex64]:
    # TODO: coeffs and T gpu ram object
    if not __cupy_import__:
        raise ImportError(f"Issue importing cupy for gpu computations")
    # TODO: complete this
    return t


@jit(nopython=True, parallel=True, fastmath=True, nogil=True)
def computeC_from_coeffs_cpu(coeffs: npt.NDArray[np.complex64], c: npt.NDArray[np.complex64]) -> npt.NDArray[np.complex64]:
    hh = coeffs[0, 0, :, :]
    hv = coeffs[0, 1, :, :]
    # vh = coeffs[1, 0, :, :]
    vv = coeffs[1, 1, :, :]

    # TODO: complete this functions
    c[0, 0, :, :] = 0.5 * np.square(np.abs(hh + vv))
    c[0, 1, :, :] = 0.5 * (hh + vv) * np.conj(hh - vv)
    c[0, 2, :, :] = (hh + vv) * np.conj(hv)
    c[1, 0, :, :] = 0.5 * (hh - vv) * np.conj(hh + vv)
    c[1, 1, :, :] = 0.5 * np.square(np.abs(hh - vv))
    c[1, 2, :, :] = (hh + vv) * np.conj(hv)
    c[2, 0, :, :] = np.conj(hh + vv) * hv
    c[2, 1, :, :] = np.conj(hh - vv) * hv
    c[2, 2, :, :] = 2 * np.square(np.abs(hv))

    return c


def computeC_from_coeffs_gpu(coeffs: npt.NDArray[np.complex64], c:npt.NDArray[np.complex64]) -> npt.NDArray[np.complex64]:
    # TODO: coeffs and C ram object
    if not __cupy_import__:
        raise ImportError(f"Issue importing cupy for gpu computations")
    # TODO: complete this
    return c
