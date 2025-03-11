import rasterio
import numpy as np
from skimage.transform import resize

# 定义一个函数，用于裁剪 classified_raster.tif
def crop_with_mask(classified_raster, mask_raster, nodata_value):
    """使用 mask_raster 中大于 0 的部分裁剪 classified_raster"""
    mask = mask_raster > 0
    cropped_raster = np.full_like(classified_raster, nodata_value, dtype=rasterio.float32)
    cropped_raster[mask] = classified_raster[mask]
    return cropped_raster

for i in ['heat/loss/CDD_loss_modified.tif','heat/loss/tmax95th_loss.tif','heat/loss/hd_loss_modified.tif']:
    # 读取 classified_raster.tif
    classified_raster_path = i
    print(classified_raster_path.split('/')[-1].split('_')[0])
    # classified_raster_path =
    with rasterio.open(classified_raster_path) as src_classified:
        classified_raster = src_classified.read(1)
        profile = src_classified.profile
        nodata_value = src_classified.nodata

    # 读取四个栅格文件路径
    # mask_raster_paths = ["E:/Datasatlast/lastresults/combine/SSP2_RCP45/2050/SSP2_RCP45_2050_BIRD.tif",
    #                      "E:/Datasatlast/lastresults/combine/SSP2_RCP45/2050/SSP2_RCP45_2050_MAMMALS.tif",
    #                      "E:/Datasatlast/lastresults/combine/SSP2_RCP45/2050/SSP2_RCP45_2050_PLANTS.tif",
    #                      "E:/Datasatlast/lastresults/combine/SSP2_RCP45/2050/SSP2_RCP45_2050_REPTILES.tif"]
    mask_raster_paths = ["E:/Datasatlast/LossResults/SSP2_RCP45/SSP2_RCP45_2050_BIRD.tif",
                         "E:/Datasatlast/LossResults/SSP2_RCP45/SSP2_RCP45_2050_MAMMALS.tif",
                         "E:/Datasatlast/LossResults/SSP2_RCP45/SSP2_RCP45_2050_PLANTS.tif",
                         "E:/Datasatlast/LossResults/SSP2_RCP45/SSP2_RCP45_2050_REPTILES.tif"]

    for i, mask_path in enumerate(mask_raster_paths):
        if 'BIRD' in mask_path:
            NAME = 'Bird'
        if 'MAMMALS' in mask_path:
            NAME = 'Mammals'
        if 'PLANTS' in mask_path:
            NAME = 'Plants'
        if 'REPTILES' in mask_path:
            NAME = 'Reptiles'
        # 打开 mask_raster
        with rasterio.open(mask_path) as src_mask:
            mask_raster = src_mask.read(1)
        if classified_raster.shape != mask_raster.shape:
            mask_raster = resize(mask_raster, classified_raster.shape, order=0, preserve_range=True, anti_aliasing=False).astype(
                mask_raster.dtype)
        mask_raster[mask_raster == 256] = 0
        # 使用 mask_raster 裁剪 classified_raster
        cropped_raster = crop_with_mask(classified_raster, mask_raster, nodata_value)

        # 更新输出文件的元数据并保存裁剪后的结果
        # output_path = f"A分物种/{classified_raster_path.split('/')[-1].split('_')[0]}_{NAME}.tif"

        # 变化区域：
        output_path = f"A分物种/变化区域/{classified_raster_path.split('/')[-1].split('_')[0]}_{NAME}.tif"
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(cropped_raster, 1)

        print(f"裁剪完成并保存为 {output_path}")
