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
from copy import deepcopy

from constants import METADATA_FILE_PATH, AGC_CLASSES, CHECKED_CELL_XML_SAVE_PATH, ACCEPTED_OVERLAPPED_RATIO
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

    image_path_info_dict_path = ctype + '_IMAGES_PATH_DICT.txt'
    check_name = os.path.join(METADATA_FILE_PATH, image_path_info_dict_path)

    if os.path.exists(check_name):
        with open(os.path.join(METADATA_FILE_PATH, image_path_info_dict_path)) as f:
            files = [item.replace('\n', '') for item in f.readlines()]
    else:
        files = FilesScanner(path, ['.jpg']).get_files()
        with open(os.path.join(METADATA_FILE_PATH, image_path_info_dict_path), 'w') as o:
            o.writelines([item + '\n' for item in files])

    # 根据细胞图像文件名生成细胞坐标信息
    cells_dict = {}

    for item in files:
        if item.endswith('.jpg'):
            # 细胞图文件名
            basename = os.path.basename(item)

            parent = os.path.dirname(item)
            # 细胞所属类别
            clas_type = os.path.basename(parent)

            parent = os.path.dirname(parent)
            # 细胞所属大图名称
            parent_name = os.path.basename(parent)

            parent = os.path.dirname(parent)
            # 大图所属类别
            parent_type = os.path.basename(parent)

            # 大图原始路径
            try:
                parent_path = parent_pathes[parent_name]
            except Exception as e:
                print("CANNOT FIND RELATIVE TIFF PATH INFO, %s" % str(e))
                exit()

            # 解析坐标信息
            point = get_location_from_filename(basename)
            assert point, "THIS JPG NAME IS NOT ACCEPTED => %s" % basename

            _, x, y, w, h, _ = point

            # 修正 AGC 细胞类别
            if clas_type in AGC_CLASSES:
                clas_type = 'AGC'

            # 解析与修正大图分类
            if '_' in parent_type:
                parent_type = parent_type.split('_')[-1]

            if parent_type in AGC_CLASSES:
                parent_type = 'AGC'

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


def generate_xml_file(points_collection):
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
        save_path = os.path.join(CHECKED_CELL_XML_SAVE_PATH, parent_file_name)

        # 当本地文件不存在时从远程服务器下载该文件
        if not os.path.exists(save_path):
            pass
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
        '/run/user/1000/gvfs/smb-share:server=192.168.2.221,share=data_samba/DATA/checked_cells/manual_labelled_checked/label_kfb_tif/label_data',
        '/run/user/1000/gvfs/smb-share:server=192.168.2.221,share=data_samba/DATA/checked_cells/manual_labelled_checked/label_kfb_tif/stage2_labelimg',
        '/run/user/1000/gvfs/smb-share:server=192.168.2.221,share=data_samba/DATA/checked_cells/manual_labelled_checked/label_kfb_tif/stage2_online',
    ]

    # 自动标注细胞图像存储位置
    auto_path = '/run/user/1000/gvfs/smb-share:server=192.168.2.221,share=data_samba/DATA/checked_cells/auto_cellCutting_checked/Drzhuchecked'

    # 手工标注细胞图像存储位置
    manual_path = '/run/user/1000/gvfs/smb-share:server=192.168.2.221,share=data_samba/DATA/checked_cells/manual_labelled_checked/renamed_manual_checked_cells'

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

    # 2. 生成大图与细胞位置信息文件路径字典
    # 人工标注细胞信息
    print('LOAD MANUAL IMAGES INFO COLLECTIONS...')
    manual_images = get_cell_image(manual_path, 'MANUAL', tif_images)

    # 自动标注细胞信息
    print('LOAD AUTO IMAGES INFO COLLECTIONS...')
    auto_images = get_cell_image(auto_path, 'AUTO', tif_images)

    # 用于判断同一大图是否在手工标注和自动标注文件夹中同时存在
    # rets[0]-不存在标注信息；rets[1]-存在 手工/自动 一种标注信息；rets[2]-存在 手工+自动 两种标注信息
    rets = [0, 0, 0]
    # 相似细胞个数统计
    similar_count = 0

    # 所有大图的文件名列表
    tif_names = list(tif_images.keys())

    # 3. 大图与图内细胞信息字典
    print('DROP CELL WHICH IN AUTO AND MANUAL AND OVERLAP RATION OVER 0.5 ...')
    points_collection = {}
    for name in tif_names:
        # 获取自动标注细胞信息文件路径
        auto = auto_images.get(name, None)
        # 获取手工标注细胞信息文件路径
        manual = manual_images.get(name, None)

        # 表示大图在手工标注和自动标注均不存在
        n = 0

        # 表示大图在自动标注中存在
        n += 1 if auto else 0

        # 表示大图在手工标注中存在
        n += 1 if manual else 0

        # 计数
        rets[n] += 1

        # 当两种标注数据同时存在时，进行去重处理
        # 以手工标注信息为准，对自动标注信息在手工标注信息中进行遍历
        # 若存在重合度 ratio > 0.5 的标注信息，直接丢弃；否则加入细胞信息列表
        if n == 2:
            # 以手工标注信息为基准
            # TO-DO 过滤 重叠率 > 0.5 图像
            available_points = deepcopy(manual)

            # 对自动标注信息进行遍历，存在手工标注信息中存在 重合度 > 0.5 的细胞信息，直接丢弃
            for item_ in auto:
                x_, y_, w_, h_ = item_['x'], item_['y'], item_['w'], item_['h']

                for item in manual:
                    x, y, w, h = item['x'], item['y'], item['w'], item['h']
                    ratio = cal_IOU((x, y, w, h), (x_, y_, w_, h_))

                    if ratio > ACCEPTED_OVERLAPPED_RATIO:
                        similar_count += 1
                        break
                else:
                    available_points.append(item_)

            points_collection[name] = available_points

        elif n == 1:
            if auto:
                points_collection[name] = auto

            if manual:
                points_collection[name] = manual

    print('\n大图文件总数:\t%s' % len(tif_names))
    print('未匹配到标注信息的大图数量:\t%s' % rets[0])
    print('匹配到一种标注信息的大图数量:\t%s' % rets[1])
    print('匹配到两种标注信息的大图数量:\t%s' % rets[2])
    print('重合度 大于0.5 的细胞数量:\t%s' % similar_count)
    print('已标注大图数量:\t%s\n' % len(points_collection))

    # 4. 拷贝文件，生成 xml 文件
    generate_xml_file(points_collection)
