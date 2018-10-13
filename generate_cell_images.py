# coding: utf-8
import os
import xml
import openslide
from concurrent.futures import ProcessPoolExecutor, as_completed

from constants import CELL_IMAGES_SAVE_PATH, TRAIN_DATA_SAVE_PATH, TIFF_IMAGE_RESOURCE_PATH, TIFF_OPEN_FAIL_RECORDS, \
    DATA_RESOURCE_ROOT_PATH
from tslide.tslide import TSlide

from utils import copy_remote_file_to_local, FilesScanner

if not os.path.exists(CELL_IMAGES_SAVE_PATH):
    os.makedirs(CELL_IMAGES_SAVE_PATH, exist_ok=True)


def generate_image_from_xml(xml_path, cell_save_path):
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
    tiff_file_path = os.path.join(TIFF_IMAGE_RESOURCE_PATH, parent.getAttribute("FullName"))

    annotations = collection.getElementsByTagName("Annotation")

    # 
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

    # class_count = dict(zip(PATHOLOGY_TYPE_CLASSES, [0] % len(PATHOLOGY_TYPE_CLASSES)))
    for index, annotation in enumerate(annotations):
        cell = annotation.getElementsByTagName("Cell")[0]
        x = int(cell.getAttribute("X"))
        y = int(cell.getAttribute("Y"))
        w = int(cell.getAttribute("W"))
        h = int(cell.getAttribute("H"))

        center_x = x + int(w / 2)
        center_y = y + int(h / 2)

        line_length = max(w, h)

        x_ = center_x - int(line_length / 2)
        y_ = center_y - int(line_length / 2)
        w_, h_ = line_length, line_length

        class_type = cell.getAttribute("Type")

        save_path = os.path.join(cell_save_path, class_type)
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)

        image_name = "%s_x%s_y%s_w%s_h%s_s%s.jpg" % (tiff_file_name, x, y, w, h, index)
        slide.read_region((x_, y_), 0, (w_, h_)).convert("RGB").save(os.path.join(save_path, image_name))

    return None


if __name__ == '__main__':
    # xmls_path = TRAIN_DATA_SAVE_PATH
    # 获取 xml 文件路径列表
    xmls = FilesScanner(TRAIN_DATA_SAVE_PATH, ['.xml']).get_files()

    size = len(xmls)

    executor = ProcessPoolExecutor(max_workers=20)
    tasks = []
    for index, file in enumerate(xmls):
        tasks.append(executor.submit(generate_image_from_xml, file, CELL_IMAGES_SAVE_PATH))

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

    print("THERE %s TIFF FILE READ FILE, PLEASE CHECK => %s" % write_to)
