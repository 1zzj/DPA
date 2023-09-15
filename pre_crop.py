import os
from osgeo import gdal
import numpy as np


#  读取tif数据集
def readTif(fileName):
    """
    打开单张图片
    fileName 图片路径
    """
    dataset = gdal.Open(fileName)
    if dataset == None:
        print(fileName + "文件无法打开")
    return dataset


#  保存tif文件函数
def writeTiff(im_data, im_geotrans, im_proj, path):
    """
    将单个numpy数组保存为tif图片
    im_data : numpy数组
    im_geotrans : 仿射变换参数 (图上坐标与平面坐标的映射关系)
    im_proj : 投影信息(平面坐标与大地坐标的映射关系)
    path : 保存路径 .tif
    """
    # 得到输入im_data的数据类型
    if 'uint8' in im_data.dtype.name:  # dtype.name: 数组中元素的数据类型列表
        datatype = gdal.GDT_Byte  # uint8
    elif 'uint16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16 # uint16
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_Int16
    else:
        # datatype = gdal.GDT_Float32
        raise TypeError("不属于uint8或uint16或int16类型")

    # 得到输入im_data尺寸信息
    if len(im_data.shape) == 3:  # 三维数组(channel,H,W)
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:  # 二维数组转为(1,H,W)
        im_data = np.array([im_data])  # 增加一个维度
        im_bands, im_height, im_width = im_data.shape

    # 创建GeoTiff数据驱动程序
    driver = gdal.GetDriverByName("GTiff")

    # 在内存中创建数据集，dataset为指向数据集的指针(并未写入磁盘)
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype) # path: .tif

    # Geotiff的坐标、投影信息
    # if (dataset != None):
    #     dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
    #     dataset.SetProjection(im_proj)  # 写入投影

    # 将数据写入内存中数据集的各个波段
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])  # dataset.GetRasterBand索引从1开始

    # 删除内存中的数据集，并触发保存到磁盘
    del dataset


def TifCrop(TifPath, SavePath ,CropSize, RepetitionRate):
    """
    滑动裁剪一个大图片
    Tifpath: 文件路径
    Savepath: 保存路径
    CropSize 裁剪尺寸
    RepetitionRate 重复率
    """
    dataset_img = readTif(TifPath)
    width = dataset_img.RasterXSize
    height = dataset_img.RasterYSize
    proj = dataset_img.GetProjection()
    geotrans = dataset_img.GetGeoTransform()
    img = dataset_img.ReadAsArray(0, 0, width, height)  # 从(0,0)获取width列height行数据(整幅影像)

    #  获取当前文件夹的文件个数len,并以len+1命名即将裁剪得到的图像
    new_name = len(os.listdir(SavePath)) + 1

    #  整数裁剪，按行列裁剪图片为i*j个, RepetitionRate为重复率0
    for i in range(int((height - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))): # (H-重复的)/(未重复的)
        for j in range(int((width - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))):
            #  如果图像是单波段
            if (len(img.shape) == 2):
                cropped = img[
                          int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                          int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
            #  如果图像是多波段
            else:
                cropped = img[:,  # 第一个维度是波段
                          int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                          int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
            #  写图像
            writeTiff(cropped, geotrans, proj, SavePath + "/%d.tif" % new_name)
            #  文件名 + 1
            new_name = new_name + 1

    #  裁剩下的最后一列
    for i in range(int((height - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))):
        if (len(img.shape) == 2):
            cropped = img[int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                      (width - CropSize): width]
        else:
            cropped = img[:,
                      int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                      (width - CropSize): width]  # 剩下的一列，直接取cropsize个，哪怕有重叠
        #  写图像
        writeTiff(cropped, geotrans, proj, SavePath + "/%d.tif" % new_name)
        new_name = new_name + 1

    #  裁剩下最后一行
    for j in range(int((width - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))):
        if (len(img.shape) == 2):
            cropped = img[(height - CropSize): height,
                      int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
        else:
            cropped = img[:,
                      (height - CropSize): height,   # 剩下的一行，直接取cropsize个，哪怕有重叠
                      int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
        writeTiff(cropped, geotrans, proj, SavePath + "/%d.tif" % new_name)
        #  文件名 + 1
        new_name = new_name + 1

    #  裁剪右下角
    if (len(img.shape) == 2):
        cropped = img[(height - CropSize): height,
                  (width - CropSize): width]
    else:
        cropped = img[:,
                  (height - CropSize): height,
                  (width - CropSize): width]
    writeTiff(cropped, geotrans, proj, SavePath + "/%d.tif" % new_name)
    new_name = new_name + 1

def print_info(path,name):
    """输出文件的维度和类型信息"""
    # 打开图像文件
    dataset = gdal.Open(path+name)

    # 获取图像的宽度和高度
    width = dataset.RasterXSize
    height = dataset.RasterYSize

    # 获取图像的波段数
    num_bands = dataset.RasterCount

    # 读取图像数据
    image_data = dataset.ReadAsArray()

    # 打印图像数据的格式
    print(name,image_data.shape,image_data.dtype)  # 打印图像数据的维度信息



if __name__ == "__main__":
    #-------------------------------------------------------------------------------------------------------------------------------
    # 列表解析式，生成图片和标签名列表
    img_list = [file for file in os.listdir(r"F:\Five_Billion_pixels\Image_16bit_BGRNir") if  file.endswith(".tiff")]
    label_list = [file for file in os.listdir(r"F:\Five_Billion_pixels\Annotation__index") if  file.endswith(".png")]
    Annotation__color = [file for file in os.listdir(r"F:\Five_Billion_pixels\\Annotation__color") if  file.endswith(".tif")]
    Dt = [file for file in os.listdir(r"H:\\DataSet\\AnNingValley\\GF2\\IMG") if  file.endswith(".tiff")]
    # 测试集源图片
    test_list = ['GF2_PMS1__L1A0001064454-MSS1.tif',
'GF2_PMS1__L1A0001118839-MSS1.tif',
'GF2_PMS1__L1A0001344822-MSS1.tif',
'GF2_PMS1__L1A0001348919-MSS1.tif',
'GF2_PMS1__L1A0001366278-MSS1.tif',
'GF2_PMS1__L1A0001366284-MSS1.tif',
'GF2_PMS1__L1A0001395956-MSS1.tif',
'GF2_PMS1__L1A0001432972-MSS1.tif',
'GF2_PMS1__L1A0001670888-MSS1.tif',
'GF2_PMS1__L1A0001680857-MSS1.tif',
'GF2_PMS1__L1A0001680858-MSS1.tif',
'GF2_PMS1__L1A0001757429-MSS1.tif',
'GF2_PMS1__L1A0001765574-MSS1.tif',
'GF2_PMS2__L1A0000607677-MSS2.tif',
'GF2_PMS2__L1A0000607681-MSS2.tif',
'GF2_PMS2__L1A0000718813-MSS2.tif',
'GF2_PMS2__L1A0001038935-MSS2.tif',
'GF2_PMS2__L1A0001038936-MSS2.tif',
'GF2_PMS2__L1A0001119060-MSS2.tif',
'GF2_PMS2__L1A0001367840-MSS2.tif',
'GF2_PMS2__L1A0001378491-MSS2.tif',
'GF2_PMS2__L1A0001378501-MSS2.tif',
'GF2_PMS2__L1A0001396036-MSS2.tif',
'GF2_PMS2__L1A0001396037-MSS2.tif',
'GF2_PMS2__L1A0001416129-MSS2.tif',
'GF2_PMS2__L1A0001471436-MSS2.tif',
'GF2_PMS2__L1A0001517494-MSS2.tif',
'GF2_PMS2__L1A0001591676-MSS2.tif',
'GF2_PMS2__L1A0001787564-MSS2.tif',
'GF2_PMS2__L1A0001821754-MSS2.tif']
    # 测试图片的索引
    index_list = [index for index, element in enumerate(img_list) if element[:-1] in test_list]
    #--------------------------------------------------------------------------------------------------------------------------------
    # 合并图片和标签列表，人工检查
    # print([item for pair in zip(img_list, Annotation__color) for item in pair])
    # # 自动检查图片和标签是否对应
    # for str1, str2 in zip(img_list, Annotation__color):
    #     if str1[:-5] != str2[:-12]:
    #         notmatch = True
    #         print("图片{}和标签不匹配".format(str1))
    #         break
    # --------------------------------------------------------------------------------------------------------------------------------
    # 遍历Annotation__color进行分割
    # for index,file in enumerate(Annotation__color):
    #     print(index)
    #     print_info(r"F:\\Five_Billion_pixels\\Annotation__color\\" , file)
    #     if index in index_list:
    #         print("{}属于测试集".format(file))
    #         TifCrop(r"F:\\Five_Billion_pixels\\Annotation__color\\" + file,
    #                 r"H:\\DataSet\\DPA\\data\\Ds\\test\\Annotation__color", 512, 0)
    #     else:
    #         TifCrop(r"F:\\Five_Billion_pixels\\Annotation__color\\" + file,
    #             r"H:\\DataSet\\DPA\\data\\Ds\\Annotation__color", 512, 0)
    #--------------------------------------------------------------------------------------------------------------------------------
    # 遍历Image_16bit_BGRNir进行分割
    # for index , file in enumerate(img_list):
    #     print(index+'\n')
    #     print_info(r"F:\\Five_Billion_pixels\\Image_16bit_BGRNir\\" , file)
    #     if index in index_list:
    #         print("{}属于测试集".format(file))
    #         TifCrop(r"F:\\Five_Billion_pixels\\Image_16bit_BGRNir\\"+file,
    #         r"H:\\DataSet\\DPA\\data\\Ds\\test\\image", 512, 0)
    #         # continue
    #     else:
    #         TifCrop(r"F:\\Five_Billion_pixels\\Image_16bit_BGRNir\\" + file,
    #                 r"H:\\DataSet\\DPA\\data\\Ds\\image", 512, 0)
    # --------------------------------------------------------------------------------------------------------------------------------
    # 遍历Annotation__index进行分割
    # for index , file in enumerate(label_list):
    #     print_info(r"F:\\Five_Billion_pixels\\Annotation__index\\",file)
    #     if index in index_list:
    #         print("{}属于测试集".format(file))
    #         TifCrop(r"F:\\Five_Billion_pixels\\Annotation__index\\" + file,
    #                 r"H:\\DataSet\\DPA\\data\\Ds\\test\\label", 512, 0)
    #     else:
    #         TifCrop(r"F:\\Five_Billion_pixels\\Annotation__index\\"+file,
    #         r"H:\\DataSet\\DPA\\data\\Ds\\label", 512, 0)
    # --------------------------------------------------------------------------------------------------------------------------------
    # 对目标域图像进行分割
    # for index,file in enumerate(Dt):
    #     print_info(r"H:\\DataSet\\AnNingValley\\GF2\\IMG\\" , file)
    #     TifCrop(r"H:\\DataSet\\AnNingValley\\GF2\\IMG\\" + file,
    #         r"H:\\DataSet\\DPA\\data\\Dt", 512, 0)
