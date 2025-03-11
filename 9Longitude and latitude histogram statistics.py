from osgeo import gdal, osr
import numpy as np
import pandas as pd
from pyproj import Transformer

# 打开 TIFF 文件
leixings = ['BIRD', 'MAMMALS', 'REPTILES', 'PLANTS']
for leixing in leixings:
    dataset = gdal.Open(f"E:/Datasatlast/LossResults/SSP2_RCP45/SSP2_RCP45_2050_{leixing}.tif")
    cols = dataset.RasterXSize  # 图像宽度
    rows = dataset.RasterYSize  # 图像高度

    # 获取地理变换信息
    transform = dataset.GetGeoTransform()

    # 读取栅格数据为数组
    r = dataset.ReadAsArray(0, 0, cols, rows)

    # 获取 Nodata 值
    nodata_value = dataset.GetRasterBand(1).GetNoDataValue()
    # 将 Nodata 值替换为 NaN
    r = np.where(r == nodata_value, np.nan, r)

    # 按 y 轴（即每列）计算平均值，忽略 NaN
    mean_values = np.nanmean(r, axis=0)

    # 设置转换器，将 EPSG:6933 转换为 EPSG:4326
    transformer = Transformer.from_crs("EPSG:6933", "EPSG:4326", always_xy=True)

    # 计算每一行中心点的投影 Y 坐标并转换为纬度
    y_coords = transform[3] + np.arange(rows) * transform[5]
    latitudes = [transformer.transform(0, y)[1] for y in y_coords]

    # 计算每一列中心点的投影 X 坐标并转换为经度
    x_coords = transform[0] + np.arange(cols) * transform[1]
    longitudes = [transformer.transform(x, 0)[0] for x in x_coords]

    # 将纬度和均值存入 DataFrame 并导出为 CSV 文件
    # dataframe = pd.DataFrame({'latitude': latitudes, 'value': mean_values})
    dataframe = pd.DataFrame({'longitudes': longitudes, 'value': mean_values})
    dataframe.to_csv(f"直方图/{leixing}_2050longitude.csv", index=False)