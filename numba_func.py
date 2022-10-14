import numpy as np
from numba import jit
from numba import cuda



jit(nopython=True, parallel=True, fastmath=True, nogil=True)
def computeT_cpu(HH, HV, VH, VV) -> tuple:
    T11 = 0.5 * np.square(np.abs(HH + VV))
    T12 = 0.5 * (HH + VV) * np.conjugate(HH - VV)
    T13 = (HH + VV) * np.conjugate(HV)
    T21 = 0.5 * (HH - VV) * np.conjugate(HH + VV)
    T22 = 0.5 * (np.square(np.abs(HH - VV)))
    T23 = (HH - VV) * np.conjugate(HV)
    T31 = np.conjugate(HH + VV) * HV
    T32 = np.conjugate(HH - VV) * HV
    T33 = 2 * np.square(np.abs(HV))
    return (T11, T12, T13, T21, T22, T23, T31, T32, T33)


@cuda.jit
def computeT_gpu(HH, HV, VH, VV) -> tuple:
    T11 = 0.5 * np.square(np.abs(HH + VV))
    T12 = 0.5 * (HH + VV) * np.conjugate(HH - VV)
    T13 = (HH + VV) * np.conjugate(HV)
    T21 = 0.5 * (HH - VV) * np.conjugate(HH + VV)
    T22 = 0.5 * (np.square(np.abs(HH - VV)))
    T23 = (HH - VV) * np.conjugate(HV)
    T31 = np.conjugate(HH + VV) * HV
    T32 = np.conjugate(HH - VV) * HV
    T33 = 2 * np.square(np.abs(HV))
    return (T11, T12, T13, T21, T22, T23, T31, T32, T33)


@jit(nopython=True, nogit=True, parallel=True, fastmath=True)
def computeC_cpu(HH, HV, VH, VV) -> tuple:
    C11 = np.square(np.abs(HH))
    C12 = np.sqrt(2) * HH * np.conj(HV)
    C13 = HH * np.conj(VV)
    C21 = np.sqrt(2) * np.conj(HH) * HV
    C22 = 2 * np.square(np.abs(HV))
    C23 = np.sqrt(2) * HV * np.conj(VV)
    C31 = VV * np.conj(HH)
    C32 = np.sqrt(2) * VV * np.conj(HV)
    C33 = np.square(np.abs(VV))
    return (C11, C12, C13, C21, C22, C23, C31, C32, C33)


@cuda.jit
def computeC_gpu(HH, HV, VH, VV) -> tuple:
    C11 = np.square(np.abs(HH))
    C12 = np.sqrt(2) * HH * np.conj(HV)
    C13 = HH * np.conj(VV)
    C21 = np.sqrt(2) * np.conj(HH) * HV
    C22 = 2 * np.square(np.abs(HV))
    C23 = np.sqrt(2) * HV * np.conj(VV)
    C31 = VV * np.conj(HH)
    C32 = np.sqrt(2) * VV * np.conj(HV)
    C33 = np.square(np.abs(VV))
    return (C11, C12, C13, C21, C22, C23, C31, C32, C33)
