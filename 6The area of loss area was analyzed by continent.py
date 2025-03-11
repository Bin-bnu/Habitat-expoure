import geopandas as gpd
import rasterio
import rasterio.mask
import numpy as np
import pandas as pd
from shapely.geometry import mapping

# 读取大洲边界shapefile
shapefile_path = "E:/SSP2452050/shp/continent.shp"
gdf = gpd.read_file(shapefile_path)

# 读取TIFF文件路径列表
tif_files = ["E:/Datasatlast/LossResults/SSP2_RCP45/SSP2_RCP45_2050_AMPHIBIANS.tif",
             "E:/Datasatlast/LossResults/SSP2_RCP45/SSP2_RCP45_2050_BIRD.tif",
             "E:/Datasatlast/LossResults/SSP2_RCP45/SSP2_RCP45_2050_MAMMALS.tif",
             'E:/Datasatlast/LossResults/SSP2_RCP45/SSP2_RCP45_2050_PLANTS.tif',
             'E:/Datasatlast/LossResults/SSP2_RCP45/SSP2_RCP45_2050_REPTILES.tif'
             ]

# 存储统计结果的列表
results = []

# 遍历每个TIFF文件
for tif_file in tif_files:
    # 读取TIFF栅格
    with rasterio.open(tif_file) as src:
        # 遍历每个大洲边界的要素
        for idx, feature in gdf.iterrows():
            # 获取要素的几何信息
            geometry = [mapping(feature['geometry'])]

            # 使用掩膜裁剪栅格
            out_image, out_transform = rasterio.mask.mask(src, geometry, crop=True)
            out_image = out_image[0]  # 获取第一个波段

            # 计算非Nodata区域的大于0、小于0、等于0的像元个数
            non_nodata_mask = out_image != src.nodata
            # 增加
            count_greater_0 = np.sum((out_image >= 1) & non_nodata_mask)
            # 损失
            count_less_0 = np.sum((out_image < -0.9) & non_nodata_mask)
            # 不变
            count_equal_0 = np.sum((out_image > -0.9) & (out_image < 0.9) & non_nodata_mask)

            # 将结果存储到字典中
            result = {
                "Feature_ID": idx,
                "Continent_Name": feature['continents'],  # 假设边界文件中有name字段
                "TIFF_File": tif_file,
                "Greater_Than_0": count_greater_0/10000,
                "Less_Than_0": count_less_0/10000,
                "Equal_To_0": count_equal_0/10000
            }
            print(result)
            results.append(result)

# 将结果转换为DataFrame
df = pd.DataFrame(results)

# 保存到CSV文件
output_csv_path = "statistic/按大洲统计变化区域的面积.csv"
df.to_csv(output_csv_path, index=False)

print(f"统计结果已保存到 {output_csv_path}")
