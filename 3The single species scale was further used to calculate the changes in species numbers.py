import os
import rasterio
import numpy as np
import pandas as pd
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor

def process_single_file(args):
    tif_file, folder_A, folder_B = args

    # 读取2020年栖息地数据
    with rasterio.open(os.path.join(folder_A, tif_file)) as src_2020:
        habitat_2020 = src_2020.read(1)
    # 计算2020年栖息地的像元数
    suitable_pixels_2020 = np.sum(habitat_2020 > 0)

    # 检查B文件夹中是否存在对应的文件
    tif_file_B_path = os.path.join(folder_B, tif_file)
    if os.path.exists(tif_file_B_path):
        # 读取相应年份的栖息地数据
        with rasterio.open(tif_file_B_path) as src_2050:
            habitat_2050 = src_2050.read(1)
        # 计算该年份栖息地的像元数
        suitable_pixels_2050 = np.sum(habitat_2050 > 0)
        # 计算损失的像元数和百分比
        lost_pixels = suitable_pixels_2020 - suitable_pixels_2050
        loss_percentage = (lost_pixels / suitable_pixels_2020) * 100 if suitable_pixels_2020 > 0 else 0
    else:
        # 如果B文件夹中没有对应的文件
        lost_pixels = suitable_pixels_2020
        loss_percentage = 100

    result = {
        'file_name': tif_file,
        'lost_pixels': lost_pixels,
        'loss_percentage': loss_percentage
    }
    print(result)

    return result

def process_files(args):
    year, leixing = args
    print(f"Processing {year} - {leixing}")

    # 文件夹路径
    folder_A = f"E:/Datasatlast/lastresults/baseline/2020/{leixing}"  # 替换为A文件夹的路径
    folder_B = f"E:/Datasatlast/lastresults/SSP2_RCP45/{year}/{leixing}"  # 替换为B文件夹的路径

    # 获取文件列表
    tif_files_A = [f for f in os.listdir(folder_A) if f.endswith('.tif')]
    tif_files_B = [f for f in os.listdir(folder_B) if f in tif_files_A]

    # 使用多线程处理文件
    results = []
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        tasks = [(tif_file, folder_A, folder_B) for tif_file in tif_files_A]
        results = list(executor.map(process_single_file, tasks))

    # 转换为DataFrame并保存为CSV文件
    df = pd.DataFrame(results)
    output_path = f"statistic/单一物种损失统计/habitatloss_{year}_{leixing}.csv"
    df.to_csv(output_path, index=False)
    print(f'保存完毕 {output_path}')

def main():
    leixings = ['AMPHIBIANS', 'BIRD', 'MAMMALS', 'REPTILES', 'PLANTS']
    years = ['2030', '2050', '2070', '2100']

    # 创建进程池
    with Pool(processes=cpu_count()) as pool:
        # 创建任务列表
        tasks = [(year, leixing) for year in years for leixing in leixings]
        # 并行处理
        pool.map(process_files, tasks)

if __name__ == '__main__':
    main()


    import pandas as pd
    for leixing in ['BIRD', 'MAMMALS', 'REPTILES', 'PLANTS']:
        # 读取CSV文件
        df = pd.read_csv(f"statistic/单一物种损失统计/habitatloss_2050_{leixing}.csv")

        # 计算总物种数
        total_species_count = df.shape[0]

        # 统计未发生损失的物种数目
        no_loss_count = df[(df['loss_percentage'] == 0)].shape[0]

        # 统计发生损失的物种数目
        partial_loss_count = df[(df['loss_percentage'] > 0) & (df['loss_percentage'] < 100)].shape[0]

        # 统计全损失的物种数目
        total_loss_count = df[df['loss_percentage'] == 100].shape[0]

        # 统计增加的物种数目
        increase_count = df[(df['loss_percentage'] < 0)].shape[0]

        # 计算每个类别占总物种数的比例
        no_loss_percentage = no_loss_count / total_species_count * 100
        partial_loss_percentage = partial_loss_count / total_species_count * 100
        total_loss_percentage = total_loss_count / total_species_count * 100
        increase_percentage = increase_count / total_species_count * 100

        # 定义变化百分比的级别
        # 定义变化百分比的级别
        bins = [-float('inf'), -30, -15, -5, 0, 0.0000001, 5, 15, 30, float('inf')]
        # labels = ['<-30', '-30--15', '-15--5', '-5-0', '0', '0-5', '5-15', '15-30', '>30']
        labels = ['>30%', '15% - 30%', '5% - 15%', '0 - 5%', '0', '-5% - 0', '-15% - -5%', '-30% - -15%', '<-30%']

        # 将损失百分比划分为七个级别
        df['change_category'] = pd.cut(df['loss_percentage'], bins=bins, labels=labels, right=False)

        # 统计每个级别的物种数量
        change_category_counts = df['change_category'].value_counts().reindex(labels, fill_value=0)

        # 计算每个级别占总物种数的比例
        change_category_percentages = (change_category_counts / total_species_count) * 100

        # 打印结果
        print(leixing)
        print(f"{leixing}未发生损失的物种数目: {no_loss_count} ({no_loss_percentage:.2f}%)")
        print(f"{leixing}发生损失的物种数目: {partial_loss_count} ({partial_loss_percentage:.2f}%)")
        print(f"{leixing}全损失的物种数目: {total_loss_count} ({total_loss_percentage:.2f}%)")
        print(f"{leixing}增加的物种数目: {increase_count} ({increase_percentage:.2f}%)\n")

        # print("按变化百分比分类的物种数目和比例:")
        # for label, count, percentage in zip(labels, change_category_counts, change_category_percentages):
        #     print(f"{label}: {count} ({percentage:.2f}%)")
        #
        # 保存结果到CSV文件
        output_df = pd.DataFrame({
            'Change_Category': labels,
            'Species_Count': change_category_counts.values,
            'Percentage': change_category_percentages.values
        })

        output_df.to_csv(f"statistic/进一步统计/species_loss_{leixing}.csv", index=False)