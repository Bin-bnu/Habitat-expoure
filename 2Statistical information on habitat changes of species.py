import os
import rasterio
import numpy as np
import pandas as pd


output_csv = 'E:/Datasatlast/LossStatistic/按整个变化大图统计面积.csv'
# 初始化一个空的列表来存储结果
results = []
# 定义文件夹路径
for leixing in ['SSP1_RCP26','SSP2_RCP45','SSP3_RCP70','SSP5_RCP85']:
    input_folder = 'E:/Datasatlast/LossResults/'+str(leixing)
    # 遍历文件夹中的所有 TIFF 文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.tif') and 'PLANT' not in filename:
            file_path = os.path.join(input_folder, filename)
            # 读取栅格数据
            with rasterio.open(file_path) as src:
                # 读取栅格数据到 numpy 数组
                array = src.read(1)
                # 获取 Nodata 值
                # nodata = src.nodata
                raster1_meta = src.meta

                # 获取 NoData 值
                nodata = raster1_meta['nodata']
                print(nodata)
                # 计算有效数据（排除 Nodata 区域）
                # if nodata is not None:
                valid_data = array[array != nodata]
                # else:
                #     valid_data = array
                # 计算统计值
                total_valid_pixels = valid_data.size
                greater_than_zero = np.sum(valid_data > 0.9)/1000
                equal_to_zero = np.sum((valid_data > -0.9) & (valid_data < 0.9))/10000

                less_than_zero = np.sum(valid_data < -0.9)/1000

                # 计算大于0和小于0的像元值总和
                # 将 valid_data 转换为整数
                valid_data_int = np.floor(valid_data).astype(int)
                sum_greater_than_zero = np.sum(valid_data_int[valid_data_int >= 0.9])/10000
                sum_less_than_zero = np.sum(valid_data_int[valid_data_int < -0.9])/10000

                # # 计算百分比
                # if total_valid_pixels > 0:
                #     percent_greater_than_zero = (greater_than_zero / total_valid_pixels) * 100
                #     percent_equal_to_zero = (equal_to_zero / total_valid_pixels) * 100
                #     percent_less_than_zero = (less_than_zero / total_valid_pixels) * 100
                # else:
                #     percent_greater_than_zero = percent_equal_to_zero = percent_less_than_zero = 0

                # 将结果添加到列表
                results.append([filename, equal_to_zero,
                                sum_greater_than_zero, sum_less_than_zero])

# 将结果转换为 DataFrame
df = pd.DataFrame(results, columns=['Filename',  'EqualToZero',
                                    'SumGreaterThanZero', 'SumLessThanZero'])

# 保存结果到 CSV 文件
df.to_csv(output_csv, index=False)