# coding: utf-8

"""
   基于已审核的细胞图像文件名生成对应大图的 xml， xml 包含信息为对应大图里的已审核细胞位置
   细胞图像包含其来源大图名称，如
    # 1-p0.0000_markedAs_ASCH_2017-10-27-16_12_50_x9659_y28027_w616_h331.jpg
    # 1-p0.0000_markedAs_CC_2018-03-27-23_18_27_x5675_y23431_w230_h207_4x.jpg
    # 1-p0.0000_markedAs_ACTINO_2018-06-20_18_37_06_x34602_y10123_w145_h172_2x.jpg
    # 1-p0.0000_2017-11-24-13_16_54_x6626_y35845_w150_h79_4x.jpg
    # 1-p0.0001_2017-10-09-17_12_28_x19230_y29594_w370_h910_.jpg
    # m1_2018-04-04-17_50_08_x11194_y33583_w163_h112.jpg
    # m1_2018-06-20_18_37_06_x10880_y42947_w113_h122.jpg

"""

import json
import os
import re
from copy import deepcopy
from concurrent.futures import ProcessPoolExecutor, as_completed

from constants import PATHOLOGY_TYPE_CLASSES, METADATA_FILE_PATH, AGC_CLASSES, CHECKED_CELL_XML_SAVE_PATH, ACCEPTED_OVERLAPPED_RATIO, TIFF_IMAGE_RESOURCE_PATH
from utils import FilesScanner, generate_checked_level_xml, cal_IOU, get_location_from_filename, generate_name_path_dict

if not os.path.exists(METADATA_FILE_PATH):
    os.makedirs(METADATA_FILE_PATH, exist_ok=True)

if not os.path.exists(CHECKED_CELL_XML_SAVE_PATH):
    os.makedirs(CHECKED_CELL_XML_SAVE_PATH, exist_ok=True)


def get_cell_image(path, ctype, parent_pathes):
    """
    获取细胞文件路径
    :param path: 细胞图像路径
    :param ctype: 标注类别 MANUAL or AUTO
    :param parent_pathes: 大图名称及对应路径字典
    :return:
    """

    # 检查本地有无细胞图像文件路径信息文件
    # 如果存在，则直接读取
    # 如果没有，通过 FileScanner 工具类获取并写入本地文件

    # image_path_info_dict_path = ctype + '_IMAGES_PATH_DICT.txt'
    # check_name = os.path.join(METADATA_FILE_PATH, image_path_info_dict_path)

    # if os.path.exists(check_name):
    #     with open(os.path.join(METADATA_FILE_PATH, image_path_info_dict_path)) as f:
    #         files = [item.replace('\n', '') for item in f.readlines()]
    # else:
    files = FilesScanner(path, ['.jpg']).get_files()
        # with open(os.path.join(METADATA_FILE_PATH, image_path_info_dict_path), 'w') as o:
        #     o.writelines([item + '\n' for item in files])

    # 根据细胞图像文件名生成细胞坐标信息
    cells_dict = {}

    for item in files:
        if item.endswith('.jpg'):
            # 细胞图文件名
            basename = os.path.basename(item).replace(' ', '-')

            parent = os.path.dirname(item)
            # 细胞所属类别
            clas_type = os.path.basename(parent)

            parent = os.path.dirname(parent)
            # 细胞所属大图名称
            pattern = re.compile(r'1\-p0\.\d+_(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_?(\dx)?.jpg')
            items = re.findall(pattern, basename)
            if items:
                parent_name, x, y, w, h, _ = items[0]
            else:
                raise Exception(items)
                exit()

            # parent_name = os.path.basename(parent).replace(' ', '-')

            parent = os.path.dirname(parent)
            # 大图所属类别
            parent_type = os.path.basename(parent)

            # 大图原始路径
            try:
                parent_path = parent_pathes[parent_name]
            except Exception as e:
                print("CANNOT FIND RELATIVE TIFF PATH INFO, %s\n%s" % (str(e), item))
                exit()

            # 解析坐标信息
            point = get_location_from_filename(basename)
            assert point, "THIS JPG NAME IS NOT ACCEPTED => %s" % basename

            _, x, y, w, h, _ = point
            x, y, w, h = int(x), int(y), int(w), int(h)

            if '2+' in clas_type:
                x = x - w / 2
                y = y - h / 2
                w = 2 * w
                h = 2 * h

            if '_' in clas_type:
                clas_type = clas_type.split('_')[0]

            if '-' in clas_type:
                clas_type = clas_type.split('-')[0]

            # 修正 AGC 细胞类别
            if clas_type in AGC_CLASSES:
                clas_type = 'AGC'

            if clas_type not in PATHOLOGY_TYPE_CLASSES:
                raise Exception(item + " CELL_TYPE NOT FOUND")

            # # 解析与修正大图分类
            # if '_' in parent_type:
            #     parent_type = parent_type.split('_')[-1]
            #
            # if '-' in parent_type:
            #     parent_type = parent_type.split('-')[-1]

            if parent_type in AGC_CLASSES:
                parent_type = 'AGC'

            # if parent_type not in PATHOLOGY_TYPE_CLASSES:
                # raise Exception(item + " PARENT_TYPE NOT FOUND")


            # 细胞位置及类别信息
            info = {
                'name': basename,
                'cell_type': clas_type,
                'cell_path': item,
                'parent': parent_name,
                'parent_full_name': os.path.basename(parent_path),
                'parent_type': parent_type,
                'x': x,
                'y': y,
                'w': w,
                'h': h,
            }

            if parent_name in cells_dict:
                cells_dict[parent_name].append(info)
            else:
                cells_dict[parent_name] = [info]

    # 将解析细胞数据按归属大图名称写入文件
    for key, lines in cells_dict.items():
        # 生成输出路径
        save_path = os.path.join(METADATA_FILE_PATH, ctype + '_IMAGES_PATH_DICT')
        os.makedirs(save_path, exist_ok=True)
        with open(os.path.join(save_path, key + '.txt'), 'w') as f:
            for line in lines:
                f.write(json.dumps(line) + '\n')

    return cells_dict


def generate_xml_file(points_collection, tif_images):
    # 统计当前数据生成进度
    count = 0

    # 待处理文件总数
    size = len(points_collection)

    # 遍历拷贝大图文件及生成xml文件
    for key, value in points_collection.items():
        parent_name = value[0]['parent']
        parent_file_name = value[0]['parent_full_name']

        print("\nProcessing %s / %s %s" % (count + 1, size, parent_file_name))

        # TIFF 文件本地存储路径
        save_path = os.path.join(TIFF_IMAGE_RESOURCE_PATH, parent_file_name)

        # 当本地文件不存在时从远程服务器下载该文件
        key, _ = os.path.splitext(os.path.basename(parent_file_name))
        key = key.replace(' ', '-')

        if key not in tif_images:
            raise Exception("%s IS NOT FOUND IN LOCAL RESOURCE PATH" % parent_file_name)
            # pass
            # shutil.copy(parent_path, save_path)
        else:
            pass

        # 生成大图对应 细胞标注点 xml 文件
        xml_file_name = os.path.join(CHECKED_CELL_XML_SAVE_PATH, parent_name + '.xml')
        print('GENERATE XML %s' % xml_file_name)
        if len(value) > 0:
            generate_checked_level_xml(xml_file_name, value)

        count += 1


if __name__ == '__main__':
    # 大图存储位置
    tif_path = [
        '/home/cnn/Development/DATA/TRAIN_DATA/TIFFS',
    ]

    # 自动标注细胞图像存储位置
    auto_path = [
        '/home/cnn/Development/DATA/THIRD_TRAIN_DATA_1',
    ]

    # 1. 检查大图 名称与路径对应关系 txt 文件是否存在， 生成生成大图文件名与路径 dict
    tif_images_collections_path = os.path.join(METADATA_FILE_PATH, 'TIFF_IMAGES_PATH_DICT.txt')

    if not os.path.exists(tif_images_collections_path):
        print('GENERATE TIFF IMAGES FILES PATH COLLECTIONS FILE...')
        tif_images = generate_name_path_dict(tif_path, ['.tif', '.kfb'], tif_images_collections_path)
    else:
        print('LOAD TIFF IMAGES FILES PATH COLLECTIONS...')

        tif_images = {}
        with open(tif_images_collections_path) as f:
            lines = f.readlines()
            for line in lines:
                name, path = line.replace('\n', '').split('\t')
                if name in tif_images:
                    print('ERROR')
                else:
                    tif_images[name] = path

    if not tif_images:
        print("NO TIFF FILES FOUND!")
        exit()
    else:
        print("GOT %s TIFF FILES" % len(tif_images))

    # 2. 生成大图与细胞位置信息文件路径字典
    # 自动标注细胞信息
    print('LOAD AUTO IMAGES INFO COLLECTIONS...')
    count = 0
    points_collection = {}

    total = len(auto_path)
    for index, path in enumerate(auto_path):
        print("LOAD %s / %s ..." % (index + 1, total))
        dict_ = get_cell_image(path, 'AUTO', tif_images)
        for key, value in dict_.items():
            count += len(value)
            if key in points_collection:
                print("FOUND REPEAT KEY %s" % key)
            else:
                points_collection[key] = value

    print(count)

    # 3. 拷贝文件，生成 xml 文件
    generate_xml_file(points_collection, tif_images)
