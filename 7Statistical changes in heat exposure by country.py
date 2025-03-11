import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
import pandas as pd
import numpy as np
from skimage.transform import resize
# 读取国家行政区划 shapefile
shapefile_path = 'E:/SSP2452050/shp/World.shp'
countries = gpd.read_file(shapefile_path)
leixings = ['BIRD', 'MAMMALS', 'REPTILES', 'PLANTS']
# types = ['CDD', 'tmax95th', 'hd']
types = ['CDD', 'tmax95th', 'hd']
for leixing in leixings:
    for type1 in types:

        # 到2050年单一热暴露（'CDD', 'tmax95th', 'hd'）的变化在国家的统计
        # 读取热暴露变化栅格数据
        if type1 == 'CDD' or type1 == 'tmax95th' or type1 == 'hd':
            cdd_loss_tif_path = f'heat/loss/{type1}_loss.tif'
            data_tif_path = f'E:/Datasatlast/lastresults/combine/SSP2_RCP45/2050/SSP2_RCP45_2050_{leixing}.tif'
            # 单一热暴露变化
            csv_path = f'statistic/country/{type1}_{leixing}_2050.csv'
            if type1 == 'tmax95th':
                column_name = f't95_{leixing[:1]}'
            column_name = f'{type1}_{leixing[:1]}'

        # 两个年份2020和2050整体热暴露的评价在国家的统计
        if type1 == '2020':
            # 读取濒危物种分布栅格数据
            cdd_loss_tif_path = f'heat/output_sum2020.tif'
            # 读取濒危物种分布栅格数据
            data_tif_path = f'E:/TianyuanData/Clipresults/baseline/baseline_2020_{leixing}.tif'
            # 整体热暴露胁迫
            csv_path = f'statistic/country/Allheat_{type1}_{leixing}.csv'
            column_name = f'Heat20_{leixing[:1]}'
        if type1 == '2050':
            # 读取濒危物种分布栅格数据
            cdd_loss_tif_path = f'heat/output_sum2050.tif'
            # 读取濒危物种分布栅格数据
            data_tif_path = f'E:/TianyuanData/Clipresults/SSP2_RCP45/SSP2_RCP45_2050_{leixing}.tif'
            # 整体热暴露胁迫
            csv_path = f'statistic/country/Allheat_{type1}_{leixing}.csv'
            column_name = f'Heat50_{leixing[:1]}'


        # 计算物种分布掩膜
        def get_species_distribution_mask(data_tif_path):
            with rasterio.open(data_tif_path) as src:
                data_array = src.read(1)  # 读取栅格数据
                nodata = src.nodata
                mask = (data_array != nodata) & (data_array > 0)  # 创建非空值且大于0的掩膜
            return mask, src.transform, src.crs

        species_distribution_mask, transform, crs = get_species_distribution_mask(data_tif_path)

        # 获取每个国家范围内濒危物种分布区域的热暴露变化指标平均值
        def calculate_mean_exposure(countries, cdd_loss_tif_path, species_distribution_mask, transform):
            stats = {}
            stdata = []
            with rasterio.open(cdd_loss_tif_path) as cdd_src:
                cdd_data = cdd_src.read(1)
                nodata = cdd_src.nodata
                if species_distribution_mask.shape != cdd_data.shape:
                    print(f'有问题：{type1}_{leixing}_2050.tif')
                    species_distribution_mask = resize(species_distribution_mask, cdd_data.shape, order=0, preserve_range=True, anti_aliasing=False).astype(
                        species_distribution_mask.dtype)
                cdd_data = np.where(species_distribution_mask, cdd_data, np.nan)  # 仅保留物种分布区域的值
                for index, country in countries.iterrows():
                    country_geom = country.geometry
                    zonal_stats_result = zonal_stats(
                        country_geom,
                        cdd_data,
                        affine=transform,
                        stats='mean',
                        nodata=nodata
                    )
                    mean_exposure = zonal_stats_result[0]['mean'] if zonal_stats_result else None
                    print(country['SOC'], mean_exposure)
                    stats[country['SOC']] = mean_exposure
                    stdata.append(mean_exposure)
            return stats, stdata

        # 计算每个国家范围内的热暴露变化指标平均值
        mean_exposure_stats, stdata = calculate_mean_exposure(countries, cdd_loss_tif_path, species_distribution_mask, transform)

        # 将计算结果添加到 GeoDataFrame 的新列中
        print(mean_exposure_stats)
        countries[column_name] = stdata
        # countries[column_name] = countries['NAME'].map(mean_exposure_stats)


        # 将结果保存到 CSV 文件
        def save_results_to_csv(results, csv_path):
            df = pd.DataFrame(list(results.items()), columns=['Country', 'Mean_Exposure'])
            df.to_csv(csv_path, index=False)

        # 设置 CSV 文件保存路径


        # 保存结果到 CSV
        save_results_to_csv(mean_exposure_stats, csv_path)

# 所有循环结束后，保存结果到新的 shapefile
final_shapefile_path = 'shp/country_stats_all1.shp'
countries.to_file(final_shapefile_path, driver='ESRI Shapefile')
print(f"保存成功：{final_shapefile_path}")
