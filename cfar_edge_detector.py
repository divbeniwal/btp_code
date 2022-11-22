# %% 
# imports
import manage
import numpy as np

# %% 
# load sar_img and data
dir = manage.get_dirs()
chd = manage.get_chandrayaan2Obj()
sar_img = chd.date_map['20210312']

sar_img_load_path = dir.local.base / "sar_img_computedT"
sar_img_new_path = dir.local.base / "sar_img_crop_computedT"
sar_img.load(sar_img_load_path)

sar_img = sar_img.crop_new((350, 600, 100, 300))
sar_img.save(sar_img_new_path)

# %% 
# sar_img compute C matrix 

sar_img.computeC()
sar_img.save(sar_img_load_path)

# %% 
# Filter Parameters L: The code is valid for 1 pixel width edge only

spanimg = sar_img.T11 + sar_img.T22 + sar_img.T33

K_f = np.array([7, 3, 1, np.pi / 4])
n = int(K_f[0])
m = int(K_f[1])
N_f = np.pi / K_f[3]
p = 3

winHalfSize = int((K_f[0] - 1) / 2)
filterMask1u = np.zeros((int(K_f[0]), int(K_f[0])))
filterMask1l = np.zeros((int(K_f[0]), int(K_f[0])))
filterMask2u = np.zeros((int(K_f[0]), int(K_f[0])))
filterMask2l = np.zeros((int(K_f[0]), int(K_f[0])))


# %% 
# Filter Mask 1
filterMask1u[:m, :] = np.ones((m, n))
filterMask1l[m + 1:, :] = np.ones((m, n))

filter_temp = np.zeros((n, n), dtype=filterMask1l.dtype)
filter_temp[winHalfSize, :] = 1
filter_temp = filter_temp.T.reshape((1, -1))
filter_weight1 = np.repeat(filter_temp, repeats=p**2, axis=0)

homo_temp = (filterMask1l + filterMask1u).T.reshape((1, -1))
homo_weight1 = np.repeat(homo_temp, repeats=p**2, axis=0) + filter_weight1

# %% 
# Filter Mask 2
filterMask2u[:, :m] = np.ones((n, m))
filterMask2l[:, m + 1:] = np.ones((n, m))

filter_temp = np.zeros((n, n), dtype=filterMask1l.dtype)
filter_temp[:, winHalfSize] = 1
filter_temp = filter_temp.T.reshape((1, -1))
filter_weight2 = np.repeat(filter_temp, repeats=p**2, axis=0)

homo_temp = (filterMask2l + filterMask2u).T.reshape((1, -1))
homo_weight2 = np.repeat(homo_temp, repeats=p**2, axis=0) + filter_weight2
# %%
# Filter Mask 3
var1 = n - int(K_f[2]) + 1
filterMask4 = np.zeros((n, n))
mask = np.zeros((n, n))
for i in range(1, 1 + m):
    filterMask4 += np.eye(n, k=i)
    mask += np.eye(n, k=i)
    filterMask4 += np.eye(n, k=-i)

filterMask3 = np.flipud(filterMask4)

filter_temp = np.flipud(np.eye(n)).T.reshape((1, -1))
filter_weight3 = np.repeat(filter_temp, repeats=p**2, axis=0)

homo_temp = filterMask3.T.reshape((1, -1))
homo_weight3 = np.repeat(homo_temp, repeats=p**2, axis=0) + filter_weight3
# %%
# Filter Mask 4
filter_temp = np.eye(n).T.reshape((1, -1))
filter_weight4 = np.repeat(filter_temp, repeats=p**2, axis=0)

homo_temp = filterMask4.T.reshape((1, -1))
homo_weight4 = np.repeat(homo_temp, repeats=p**2, axis=0) + filter_weight4
# %%
# homo_reg rows and cols

homo_reg_row = np.array([3, 20])
homo_reg_col = np.array([5, 20])

# %% 
# span image crop
spanimg = np.abs(spanimg)
sic = spanimg[homo_reg_row[0]:homo_reg_row[1], homo_reg_col[0]:homo_reg_col[1]]
L_f = sic.mean() / np.square(sic.std())
a = L_f
b = a

L_f, a, b

# %%
rho = 1 - (a**-1 + b**-1 - (a + b)**-1) * (2 * p**2 - 1) / (6 * p)
rho

# %%
qmin = np.zeros(spanimg.shape)
qmax = np.zeros(spanimg.shape)
filter_type = np.zeros(spanimg.shape)
homo_type = np.zeros(spanimg.shape)

w1u = filterMask1u.T.reshape((1, -1))
w1l = filterMask1l.T.reshape((1, -1))

w2u = filterMask2u.T.reshape((1, -1))
w2l = filterMask2l.T.reshape((1, -1))

w3u = mask.T.reshape((1, -1))
w3l = 

w4u = filterMask4.T.reshape((1, -1))