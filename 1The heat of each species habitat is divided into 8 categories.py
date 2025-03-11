import rasterio
import numpy as np

def process_raster(raster, threshold, nodata_value):
    """对非 NoData 区域进行分类"""
    mask = raster != nodata_value  # 生成一个掩膜，仅处理非 NoData 区域
    classification = np.zeros_like(raster, dtype=np.uint8)
    classification[mask] = (raster[mask] > threshold).astype(np.uint8)
    return classification

# # 所有物种
# raster_paths = ["CDD_loss_modified.tif", "tmax95th_loss.tif", "hd_loss_modified.tif"]
# thresholds = [133.78, 1.07, 9.28]  # 设置三个阈值
# # 打开第一个栅格文件，读取其元数据
# with rasterio.open(raster_paths[0]) as src1:
#     raster1 = src1.read(1)
#     profile = src1.profile
#     nodata_value = src1.nodata
#
# # 打开其他两个栅格文件
# with rasterio.open(raster_paths[1]) as src2:
#     raster2 = src2.read(1)
#
# with rasterio.open(raster_paths[2]) as src3:
#     raster3 = src3.read(1)
#
# # 对每个栅格进行分类，仅处理非 NoData 区域
# class1 = process_raster(raster1, thresholds[0], nodata_value)
# class2 = process_raster(raster2, thresholds[1], nodata_value)
# class3 = process_raster(raster3, thresholds[2], nodata_value)
#
# # 组合三个分类结果，得到 8 类（1-8）
# combined_classes = class1 * 4 + class2 * 2 + class3 + 1
# # 检查合并后的分类是否在 1 到 8 之间
# valid_mask = (combined_classes >= 1) & (combined_classes <= 8)
# if not np.all(valid_mask | (combined_classes == nodata_value)):
#     # 如果有值不在 1 到 8 之间，输出警告并修正
#     print("警告: 发现值不在 1-8 范围内，将这些值重设为 NoData")
#     combined_classes[~valid_mask] = nodata_value
# # 保留原始 NoData 值的区域
# combined_classes[raster1 == nodata_value] = nodata_value
#
# # 更新元数据并创建一个新的 TIFF 文件，保存分类结果
# output_path = f"classified/classified_all.tif"
# profile.update(dtype=rasterio.int16, count=1, nodata=nodata_value)
#
# with rasterio.open(output_path, 'w', **profile) as dst:
#     dst.write(combined_classes, 1)
#
# print("分类完成并保存为", output_path)

for data in ['BIRD', 'MAMMALS', 'REPTILES', 'PLANTS']:
    # 鸟
    if data == 'BIRD':
        raster_paths = ["A分物种/CDD_Bird.tif", "A分物种/tmax95th_Bird.tif", "A分物种/hd_Bird.tif"]
        thresholds = [125.94, 1.05, 5.78]  # 设置三个阈值
    # buru
    if data == 'MAMMALS':
        raster_paths = ["A分物种/CDD_Mammals.tif", "A分物种/tmax95th_Mammals.tif", "A分物种/hd_Mammals.tif"]
        thresholds = [126.36, 1.05, 6.62]  # 设置三个阈值
    # paxing
    if data == 'REPTILES':
        raster_paths = ["A分物种/CDD_Reptiles.tif", "A分物种/tmax95th_Reptiles.tif", "A分物种/hd_Reptiles.tif"]
        thresholds = [180.75, 0.845, 8.14]  # 设置三个阈值
    if data == 'PLANTS':
        raster_paths = ["A分物种/CDD_Plants.tif", "A分物种/tmax95th_Plants.tif", "A分物种/hd_Plants.tif"]
        thresholds = [118.28, 0.97, 4.28]  # 设置三个阈值

    # 打开第一个栅格文件，读取其元数据
    with rasterio.open(raster_paths[0]) as src1:
        raster1 = src1.read(1)
        profile = src1.profile
        nodata_value = src1.nodata

    # 打开其他两个栅格文件
    with rasterio.open(raster_paths[1]) as src2:
        raster2 = src2.read(1)

    with rasterio.open(raster_paths[2]) as src3:
        raster3 = src3.read(1)

    # 对每个栅格进行分类，仅处理非 NoData 区域
    class1 = process_raster(raster1, thresholds[0], nodata_value)
    class2 = process_raster(raster2, thresholds[1], nodata_value)
    class3 = process_raster(raster3, thresholds[2], nodata_value)

    # 组合三个分类结果，得到 8 类（1-8）
    combined_classes = class1 * 4 + class2 * 2 + class3 + 1
    # 检查合并后的分类是否在 1 到 8 之间
    valid_mask = (combined_classes >= 1) & (combined_classes <= 8)
    if not np.all(valid_mask | (combined_classes == nodata_value)):
        # 如果有值不在 1 到 8 之间，输出警告并修正
        print("警告: 发现值不在 1-8 范围内，将这些值重设为 NoData")
        combined_classes[~valid_mask] = nodata_value
    # 保留原始 NoData 值的区域
    combined_classes[raster1 == nodata_value] = nodata_value
    combined_classes = combined_classes.astype(np.int16)
    # 更新元数据并创建一个新的 TIFF 文件，保存分类结果
    output_path = f"classified/classified_{data}.tif"
    profile.update(dtype=rasterio.int16, count=1, nodata=nodata_value)

    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(combined_classes, 1)

    print("分类完成并保存为", output_path)