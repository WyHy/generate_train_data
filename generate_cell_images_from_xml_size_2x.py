# coding: utf-8

"""
    基于已生成的大图对应的 xml 文件，从大图中读取并保存已审阅细胞图像
    按照 大图名称_x_y_w_h_s 信息进行命名，如
    2018-06-20_18_59_33_x8656_y46722_w91_h181_s15.jpg

    生成细胞图像供算法人员进行细胞筛选
"""

import os
import xml
from concurrent.futures import ProcessPoolExecutor, as_completed

import cv2
import numpy as np
import openslide

from constants import CELL_IMAGES_SAVE_PATH, CHECKED_CELL_XML_SAVE_PATH, TIFF_OPEN_FAIL_RECORDS, \
    DATA_RESOURCE_ROOT_PATH, METADATA_FILE_PATH, SELECTED_CELL_XML_SAVE_PATH
from tslide.tslide import TSlide
from utils import FilesScanner, generate_name_path_dict

if not os.path.exists(CELL_IMAGES_SAVE_PATH):
    os.makedirs(CELL_IMAGES_SAVE_PATH, exist_ok=True)


def generate_image_from_xml(xml_path, cell_save_path, tiff_dict):
    """
    从 xml 文件解析大图标注点坐标,生成细胞文件
    :param xml_path: xml 文件路径
    :param cell_save_path: 细胞文件生成目录
    :return:
    """

    DOMTree = xml.dom.minidom.parse(xml_path)
    collection = DOMTree.documentElement

    parent = collection.getElementsByTagName("Annotations")[0]
    # 原始大图路径
    tiff_file_name = parent.getAttribute("Name")
    # tiff_file_path = os.path.join(TIFF_IMAGE_RESOURCE_PATH, parent.getAttribute("FullName").replace(" ", '-'))
    xml_name, _ = os.path.splitext(os.path.basename(xml_path))
    if xml_name not in tiff_dict:
        print(xml_name, 'NOT FOUND!')
        exit()

    tiff_file_path = tiff_dict[xml_name]

    annotations = collection.getElementsByTagName("Annotation")

    # 打开失败的 TIFF 图像列表
    open_fail_records = []
    # 打开 TIFF 文件
    try:
        try:
            slide = openslide.OpenSlide(tiff_file_path)
        except:
            slide = TSlide(tiff_file_path)
    except:
        open_fail_records.append((len(annotations), tiff_file_path))
        print("TIFF OPEN FAILED => %s" % tiff_file_path)
        return tiff_file_path

    mpp = big_image_obj.properties['openslide.mpp-x']

    near_20x = abs(float(mpp) - 0.5)
    near_40x = abs(float(mpp) - 0.25)

    if near_20x < near_40x:
        mpp = 20
    if near_40x < near_20x:
        mpp = 40


    # class_count = dict(zip(PATHOLOGY_TYPE_CLASSES, [0] % len(PATHOLOGY_TYPE_CLASSES)))
    for index, annotation in enumerate(annotations):
        cell = annotation.getElementsByTagName("Cell")[0]
        x = int(cell.getAttribute("X"))
        y = int(cell.getAttribute("Y"))
        w = int(cell.getAttribute("W"))
        h = int(cell.getAttribute("H"))

        # expand to size * 2
        x_ = x - w / 2
        y_ = y - h / 2
        w_ = 2 * w
        h_ = 2 * h

        class_type = cell.getAttribute("Type")

        save_path = os.path.join(cell_save_path, class_type)
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)

        image_name = "%s_x%s_y%s_w%s_h%s.bmp" % (xml_name, x_, y_, w_, h_)
        try:
            patch = slide.read_region((x_, y_), 0, (w_, h_)).convert("RGB")
            
            if mpp == 40:
                image = np.asarray(image)
                image = cv2.pyrDown(image)
                image = Image.fromarray(image)

            patch.save(os.path.join(save_path, image_name)) 
            #patch = cv2.cvtColor(np.asarray(patch), cv2.COLOR_RGBA2BGR)
            #cv2.imwrite(os.path.join(save_path, image_name), patch, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        except Exception as e:
            print(e)
            print(x_, y_, w_, h_)
            print(slide.dimensions)
            continue

    return None


if __name__ == '__main__':
    # xmls_path = TRAIN_DATA_SAVE_PATH
    # 获取 xml 文件路径列表
    xmls = FilesScanner(CHECKED_CELL_XML_SAVE_PATH, ['.xml']).get_files()
    # xmls = FilesScanner(SELECTED_CELL_XML_SAVE_PATH, ['.xml']).get_files()

    size = len(xmls)

    executor = ProcessPoolExecutor(max_workers=10)
    tasks = []

    tif_path = '/home/cnn/Development/DATA/TRAIN_DATA/TIFFS'
    os.makedirs(METADATA_FILE_PATH, exist_ok=True)
    tif_images_collections_path = os.path.join(METADATA_FILE_PATH, 'TIFF_IMAGES_PATH_DICT.txt')
    tiff_dict = generate_name_path_dict(tif_path, ['.tif', '.kfb'], tif_images_collections_path)
    # tiff_dict = generate_name_path_dict('', ['.tif', '.kfb'])

    for index, file in enumerate(xmls):
        tasks.append(executor.submit(generate_image_from_xml, file, CELL_IMAGES_SAVE_PATH, tiff_dict))

        # print("%s / %s %s" % (index + 1, size, os.path.basename(file)))
        # generate_image_from_xml(file, CELL_IMAGES_SAVE_PATH)

    job_count = len(tasks)
    tiff_read_fail_records = []
    for future in as_completed(tasks):
        result = future.result()  # get the returning result from calling fuction
        if result:
            tiff_read_fail_records.append(result)

        job_count -= 1
        print("LAST JOB NUM %s" % job_count)

    write_to = os.path.join(DATA_RESOURCE_ROOT_PATH, TIFF_OPEN_FAIL_RECORDS)
    with open(write_to, "w") as o:
        for record in tiff_read_fail_records:
            o.write("%s\n" % record)

    print("THERE %s TIFF FILE READ FILE, PLEASE CHECK!" % write_to)
