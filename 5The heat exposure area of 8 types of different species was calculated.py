import numpy as np
import rasterio
import pandas as pd
from skimage.transform import resize
for name in ['BIRD', 'MAMMALS', 'REPTILES', 'PLANTS']:
    # 读取第一个栅格文件
    with rasterio.open(f'E:/Datasatlast/lastresults/combine/SSP2_RCP45/2050/SSP2_RCP45_2050_{name}.tif') as src1:
        raster1 = src1.read(1)  # 读取第一个波段
        raster1_meta = src1.meta

    # 获取 NoData 值
    nodata = raster1_meta['nodata']

    # 创建三个类别的掩膜
    mask_positive = (raster1 > 0.9) & (raster1 != nodata)
    mask_zero = (raster1 > -0.9) & (raster1 < 0.9) & (raster1 != nodata)
    mask_negative = (raster1 < 0) & (raster1 != nodata)

    # 读取第二个栅格文件
    with rasterio.open(f'E:/Datasatlast/SSP2452050/classified/classified_{name}.tif') as src2:
        raster2 = src2.read(1)  # 读取第一个波段

    if raster1.shape != raster2.shape:
        raster2 = resize(raster2, raster1.shape, order=0, preserve_range=True, anti_aliasing=False).astype(
            raster2.dtype)

    # 使用掩膜提取第二个栅格中的像元值
    values_positive = raster2[mask_positive]
    values_zero = raster2[mask_zero]
    values_negative = raster2[mask_negative]

    # 计算每个类别中1-8像元值的数量
    def count_values(values):
        count_dict = {i: 0 for i in range(1, 9)}
        unique, counts = np.unique(values, return_counts=True)
        for val, count in zip(unique, counts):
            if val in count_dict:
                count_dict[val] = count
        return count_dict

    count_positive = count_values(values_positive)
    count_zero = count_values(values_zero)
    count_negative = count_values(values_negative)

    # 将结果整理成DataFrame
    data = {
        'Value': list(range(1, 9)),
        'Count_Positive': [count_positive.get(i, 0) for i in range(1, 9)],
        'Count_Zero': [count_zero.get(i, 0) for i in range(1, 9)],
        'Count_Negative': [count_negative.get(i, 0) for i in range(1, 9)]
    }

    df = pd.DataFrame(data)
    df.to_csv(f'不同物种热暴露统计/output_counts_{name}.csv', index=False)

    print("结果已保存到"+ f'不同物种热暴露统计/output_counts_{name}.csv')