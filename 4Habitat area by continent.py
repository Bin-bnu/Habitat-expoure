# import os
# import rasterio
# import numpy as np
# import pandas as pd
# import geopandas as gpd
# from rasterio.mask import mask
#
# # 定义文件路径和类型
# types = ['baseline', 'SSP1_RCP26', 'SSP2_RCP45', 'SSP3_RCP70', 'SSP5_RCP85']
# leixings = ['AMPHIBIANS', 'BIRD', 'MAMMALS', 'REPTILES', 'PLANTS']
# shapefile_path = 'E:/SSP2452050/shp/continent.shp'
# output_csv = 'statistic/continent_speciesarea.csv'
#
# # 读取shapefile
# continents_gdf = gpd.read_file(shapefile_path)
# results = []
# for leixing in leixings:
#     for type1 in types:
#         folder_path = 'E:/TianyuanData/Clipresults/' + str(type1)
#         if not os.path.exists(folder_path):
#             print(f"Folder {folder_path} does not exist.")
#             continue
#
#         tif_files = [f for f in os.listdir(folder_path) if f.endswith('.tif') and str(leixing) in f]
#         for tif_file in tif_files:
#             file_path = os.path.join(folder_path, tif_file)
#             print(f"Processing {file_path}")
#
#             # try:
#             # 打开 TIFF 文件
#             with rasterio.open(file_path) as src:
#                 nodata = src.nodata
#                 data = src.read(1)
#                 if nodata is not None:
#                     masked_data = np.ma.masked_equal(data, nodata)
#                 else:
#                     masked_data = np.ma.masked_invalid(data)
#                 # 遍历 shapefile 中的每个几何形状
#                 for _, row in continents_gdf.iterrows():
#                     geometry = row['geometry']
#
#                     # 对 TIFF 数据进行掩膜
#                     out_image, out_transform = mask(src, [geometry], crop=True)
#                     if nodata is not None:
#                         masked_out_image = np.ma.masked_equal(out_image, nodata)
#                     else:
#                         masked_out_image = np.ma.masked_invalid(out_image)
#
#                     # 计算大于0的栅格像元值的总和
#                     non_zero_sum = np.sum(masked_out_image[masked_out_image > 0])
#
#                     # 存储结果
#                     results.append({
#                         # 'Type': type1,
#                         'TIFF File': tif_file,
#                         'Geometry ID': row['continents'],  # 假设 shapefile 中有 id 列
#                         'Sum of Non-Zero Values': non_zero_sum
#                     })
#                     print({
#                         # 'Type': type1,
#                         'TIFF File': tif_file,
#                         'Geometry ID': row['continents'],  # 假
#                         'Sum of Non-Zero Values': non_zero_sum
#                     })
#
# # 将结果保存到 CSV 文件
# df_results = pd.DataFrame(results)
# df_results.to_csv(output_csv, index=False)
# print(f"Results saved to {output_csv}")
import os
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from rasterio.mask import mask
from multiprocessing import Pool, cpu_count

# 定义文件路径和类型
types = ['baseline', 'SSP1_RCP26', 'SSP2_RCP45', 'SSP3_RCP70', 'SSP5_RCP85']
# types = ['baseline','SSP2_RCP45']
leixings = ['AMPHIBIANS', 'BIRD', 'MAMMALS', 'REPTILES', 'PLANTS']
years = ['2030','2050','2070','2100']
shapefile_path = 'E:/SSP2452050/shp/continent.shp'
output_csv = 'statistic/按大洲统计栖息地面积-按像元数baseline.csv'

# 读取shapefile
continents_gdf = gpd.read_file(shapefile_path)


def process_tif_file(args):
    tif_file, folder_path, leixing, continents_gdf = args
    file_path = os.path.join(folder_path, tif_file)
    results = {}

    print(f"Processing {file_path}")

    try:
        # 打开 TIFF 文件
        with rasterio.open(file_path) as src:
            nodata = src.nodata
            data = src.read(1)
            if nodata is not None:
                data = np.ma.masked_equal(data, nodata)
            else:
                data = np.ma.masked_invalid(data)

            # 初始化结果字典
            results['TIFF File'] = tif_file

            # 遍历 shapefile 中的每个几何形状
            for _, row in continents_gdf.iterrows():
                geometry = row['geometry']
                continent_id = row['continents']  # 假设 shapefile 中有 id 列

                # 对 TIFF 数据进行掩膜
                out_image, out_transform = mask(src, [geometry], crop=True)
                if nodata is not None:
                    masked_out_image = np.ma.masked_equal(out_image, nodata)
                else:
                    masked_out_image = np.ma.masked_invalid(out_image)

                # 计算大于0的栅格像元值的总和
                non_zero_sum = np.sum(masked_out_image[masked_out_image > 0])/10000
                # 计算大于0的像元数
                # non_zero_count = np.sum(masked_out_image > 0)

                # 存储结果
                results[continent_id] = non_zero_sum
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    print(results)
    return results


def main():
    results = []
    for leixing in leixings:
        for type1 in types:
            if type1 == 'baseline':
                year = '2020'
                # 栖息地
                folder_path = 'E:/Datasatlast/lastresults/combine/' + str(type1) + '/' + str(year)
                if not os.path.exists(folder_path):
                    print(f"Folder {folder_path} does not exist.")
                    continue

                tif_files = [f for f in os.listdir(folder_path) if f.endswith('.tif') and str(leixing) in f]

                # 创建进程池并处理 TIFF 文件
                with Pool(cpu_count()) as pool:
                    arguments = [(tif_file, folder_path, leixing, continents_gdf) for tif_file in tif_files]
                    results_list = pool.map(process_tif_file, arguments)
                    results.extend(results_list)
            else:
                for year in years:
                    # 栖息地
                    folder_path = 'E:/Datasatlast/lastresults/combine/' + str(type1)+'/'+str(year)
                    if not os.path.exists(folder_path):
                        print(f"Folder {folder_path} does not exist.")
                        continue

                    tif_files = [f for f in os.listdir(folder_path) if f.endswith('.tif') and str(leixing) in f]

                    # 创建进程池并处理 TIFF 文件
                    with Pool(cpu_count()) as pool:
                        arguments = [(tif_file, folder_path, leixing, continents_gdf) for tif_file in tif_files]
                        results_list = pool.map(process_tif_file, arguments)
                        results.extend(results_list)

    # 将结果转换为 DataFrame
    df_results = pd.DataFrame(results)

    # 确保所有列的顺序一致，按大洲列填充缺失值
    columns = ['TIFF File'] + list(continents_gdf['continents'].unique())
    df_results = df_results.reindex(columns=columns, fill_value=0)

    # 将结果保存到 CSV 文件
    df_results.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")


if __name__ == '__main__':
    main()

