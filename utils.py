# coding: utf-8

import os
import re
import shutil
import random
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET

from constants import TYPE_to_COLOR_DICT, PATHOLOGY_TYPE_CLASSES, TIFF_IMAGE_RESOURCE_PATH, \
    REMOTE_PATH_FLAG, LABELME_DEFAULT_IMAGE_SIZE, LABELME_DEFAULT_XML_OUTPUT_PATH


def get_path_postfix(filename):
    """
    获取文件名和文件后缀
    :param filename: 待处理文件路径
    :return: (文件名， 文件后缀) 如：a.txt --> return ('a', '.txt')
    """
    basename = os.path.basename(filename)
    return os.path.splitext(basename)


class FilesScanner(object):
    """
    获取文件列表工具类
    """

    def __init__(self, files_path, postfix=None):
        """

        :param files_path: 待扫描文件路径
        :param postfix: 所需文件后缀，['.tif', '.kfb'], 默认为空，即获取该路径下所有文件
        """
        self.files_path = files_path

        if postfix:
            assert isinstance(postfix, list), 'argument [postfix] should be list'

        files = []
        if os.path.isfile(files_path):
            if postfix:
                _, ctype = get_path_postfix(files_path)
                if ctype in postfix:
                    files.append(files_path)
            else:
                files.append(files_path)

        if os.path.isdir(files_path):
            for root, dirs, filenames in os.walk(files_path):
                for filename in filenames:
                    if postfix:
                        _, ctype = get_path_postfix(filename)
                        if ctype in postfix:
                            files.append(os.path.join(root, filename))
                    else:
                        files.append(os.path.join(root, filename))
        # 替换为绝对路径
        files = [os.path.abspath(item) for item in files]

        self.files = files

    def get_files(self):
        return self.files


def generate_checked_level_xml(filename, point_lst):
    """
    生成大图对应审核细胞位置 xml 文件
    :param filename: 待生成 xml 文件存放路径【包含文件名】
    :param point_lst: 待写入细胞位置列表，包含 x, y, w, h
    :return: None
    """
    root = ET.Element("ASAP_Annotations")
    annotations = ET.SubElement(root, "Annotations")

    point = point_lst[0]
    parent_type = point['parent_type']

    annotations.attrib = {
        "Name": point['parent'],
        "FullName": point['parent_full_name'],
        "Type": parent_type if parent_type in PATHOLOGY_TYPE_CLASSES else "UNRECOGNIZED",
    }

    cell_count = 0
    for i, point in enumerate(point_lst):
        cell_type = point['cell_type']
        if '_' in cell_type:
            cell_type = cell_type.split('_')[0]
            
        assert cell_type in TYPE_to_COLOR_DICT, "THE CELL_TYPE [%s] IS NOT EXIST!" % cell_type

        annotation = ET.SubElement(annotations, "Annotation")
        annotation.attrib = {
            "Color": TYPE_to_COLOR_DICT[cell_type],
            "Name": "Annotation %s" % i,
            "PartOfGroup": "None",
            "Type": "Polygon"
        }

        x, y, w, h = int(point['x']), int(point['y']), int(point['w']), int(point['h'])
        cell = ET.SubElement(annotation, "Cell")

        coordinates = ET.SubElement(annotation, "Coordinates")
        cell.attrib = {
            "Name": point['name'],
            "Type": point['cell_type'],
            "Path": point['cell_path'],
            "X": "%s" % x,
            "Y": "%s" % y,
            "W": "%s" % w,
            "H": "%s" % h,
        }

        coords = [
            (0, x, y),
            (1, x + w, y),
            (2, x + w, y + h),
            (3, x, y + h),
        ]

        for coord in coords:
            coordinate = ET.SubElement(coordinates, "Coordinate")
            coordinate.attrib = {"Order": "%s" % coord[0], "X": "%s" % coord[1], "Y": "%s" % coord[2]}

        cell_count += 1

    # 存在细胞时写入文件
    if cell_count > 0:
        ET.SubElement(root, "AnnotationGroups")
        raw_string = ET.tostring(root, "utf-8")
        reparsed = parseString(raw_string)

        with open(filename, "w") as file:
            file.write(reparsed.toprettyxml(indent="\t"))


def generate_selected_level_xml(filename, point_lst):
    """
    生成大图对应筛选细胞位置 xml 文件
    :param filename: 待生成 xml 文件存放路径【包含文件名】
    :param point_lst: 待写入细胞位置列表，包含 cell_type, , y, w, h
    :return: None
    """
    root = ET.Element("ASAP_Annotations")
    annotations = ET.SubElement(root, "Annotations")

    cell_count = 0
    for i, point in enumerate(point_lst):
        cell_type = point['cell_type']
        # assert cell_type in TYPE_to_COLOR_DICT, "THE CELL_TYPE [%s] IS NOT EXIST!" % cell_type
        cell_type_ = cell_type

        # if '_' in cell_type_:
        #     cell_type_ = cell_type_.split("_")[0]

        if "2+" in cell_type_:
            exit()


        annotation = ET.SubElement(annotations, "Annotation")
        annotation.attrib = {
            "Color": TYPE_to_COLOR_DICT[cell_type_] if cell_type != cell_type_ else TYPE_to_COLOR_DICT[cell_type],
            "Name": "Annotation %s" % i,
            "PartOfGroup": "None",
            "Type": "Polygon"
        }

        x, y, w, h = int(point['x']), int(point['y']), int(point['w']), int(point['h'])
        cell = ET.SubElement(annotation, "Cell")

        coordinates = ET.SubElement(annotation, "Coordinates")
        cell.attrib = {
            "Type": point['cell_type'],
            "X": "%s" % x,
            "Y": "%s" % y,
            "W": "%s" % w,
            "H": "%s" % h,
        }

        coords = [
            (0, x, y),
            (1, x + w, y),
            (2, x + w, y + h),
            (3, x, y + h),
        ]

        for coord in coords:
            coordinate = ET.SubElement(coordinates, "Coordinate")
            coordinate.attrib = {"Order": "%s" % coord[0], "X": "%s" % coord[1], "Y": "%s" % coord[2]}

        cell_count += 1

    # 存在细胞时写入文件
    if cell_count > 0:
        ET.SubElement(root, "AnnotationGroups")
        raw_string = ET.tostring(root, "utf-8")
        reparsed = parseString(raw_string)

        with open(filename, "w") as file:
            file.write(reparsed.toprettyxml(indent="\t"))


def cal_IOU(ret01, ret02):
    """
    计算矩阵重叠率
    :param ret01: 矩阵01 （x1, y1, w1, h1）
    :param ret02: 矩阵01 （x2, y2, w2, h2）
    :return: 矩阵重叠率 ratio
    """

    x1, y1, w1, h1 = ret01
    x1, y1, w1, h1 = int(x1), int(y1), int(w1), int(h1)

    x2, y2, w2, h2 = ret02
    x2, y2, w2, h2 = int(x2), int(y2), int(w2), int(h2)

    endx = max(x1 + w1, x2 + w2)
    startx = min(x1, x2)
    w = w1 + w2 - (endx - startx)

    endy = max(y1 + h1, y2 + h2)
    starty = min(y1, y2)
    h = h1 + h2 - (endy - starty)

    if w <= 0 or h <= 0:
        ratio = 0
    else:
        area = w * h
        area01 = w1 * h1
        area02 = w2 * h2
        ratio = area / (area01 + area02 - area)

    return ratio


def get_location_from_filename(filename_string):
    """
    通过正则表达式从文件名中解析细胞在大图位置
    :param filename_string: 细胞图像文件名
    :return: (image_name, x, y, w, h)
    """
    name = filename_string.replace(' - 副本', '').replace(' ', '').encode('utf-8').decode('utf-8')

    # 1-p0.0000_markedAs_ASCH_2017-10-27-16_12_50_x9659_y28027_w616_h331.jpg
    # 1-p0.0000_markedAs_CC_2018-03-27-23_18_27_x5675_y23431_w230_h207_4x.jpg
    # 1-p0.0000_markedAs_ACTINO_2018-06-20_18_37_06_x34602_y10123_w145_h172_2x.jpg
    pattern00 = re.compile(r'.*?_markedAs_.*?_(\d+\-\d+\-\d+[\-_]\d+_\d+_\d+)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_?(\dx)?.jpg')

    # 1-p0.0000_2017-11-24-13_16_54_x6626_y35845_w150_h79_4x.jpg
    # 1-p0.0001_2017-10-09-17_12_28_x19230_y29594_w370_h910_.jpg
    # m1_2018-04-04-17_50_08_x11194_y33583_w163_h112.jpg
    # m1_2018-06-20_18_37_06_x10880_y42947_w113_h122.jpg
    pattern01 = re.compile(r'.*?_(\d+\-\d+\-\d+[\-_]\d+_\d+_\d+)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_?(\dx)?.jpg')

    # 1-p0.0000_TC17033982_x21065_y14444_w56_h49_.jpg
    # 1-p0.0987_TC17013562_x28691_y23628_w64_h61_.jpg
    # 1-p0.0033_TC18018765_x28205_y36889_w41_h52_2x.jpg
    pattern02 = re.compile(r'.*?_([A-Z]+\d+)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_?(\dx)?.jpg')


    # # 1-p0.6042_BD1607254-子宫内膜C_2018-10-09 16_42_03_x23043_y40485_w162_h218_2x.jpg
    pattern03 = re.compile(r'1-p\d\.\d+_(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_?(\dx)?.jpg')

    # 2017-10-19-09_21_43_x42903_y48412_w126_h192_s20.jpg
    pattern04 = re.compile(r'(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_s(\dx).jpg')

    if '_markedAs' in name:
        point = re.findall(pattern00, name)
    else:
        point = re.findall(pattern01, name)

    if not point:
        point = re.findall(pattern02, name)

    if not point:
        point = re.findall(pattern03, name)

    if not point:
        point = re.findall(pattern04, name)

    if point:
        return point[0]
    else:
        return None


# TO-DO
# 添加同名不同格式文件可辨识性
def generate_name_path_dict(path, postfix=None, output_file_path=None):
    """
    获取大图文件路径 key: value = 文件名：文件路径
    :param path: 待检索文件路径列表
    :param output_file_path: 将生成字典结果写入本地的文件路径，含文件名称
    :param postfix: 回收文件类型 ['.tif', '.kfb']
    :return: {filename: file_abs_path}
    """

    assert isinstance(path, (str, list)), 'argument [path] should be path or path list'

    files_collection = []

    if isinstance(path, list):
        for item in path:
            files_collection.extend(FilesScanner(item, postfix).get_files())
    else:
        files_collection = FilesScanner(path, postfix).get_files()


    dict_ = {}
    for file in files_collection:
        key, _ = os.path.splitext(os.path.basename(file))
        key = key.replace(" ", "-")

        if key in dict_:
            value = dict_[key]
            if value.endswith('.kfb'):
                pass
            else:
                dict_[key] = file
        else:
            dict_[key] = file

    # 如果存在输出路径则写入本地文件
    if output_file_path:
        with open(os.path.join(output_file_path), 'w') as f:
            for key, path in dict_.items():
                f.write('%s\t%s\n' % (key, path))

    return dict_


def get_tiff_dict():
    tif_path = '/home/tsimage/Development/DATA/tiff'
    return generate_name_path_dict(tif_path, ['.tif', '.kfb'])


def is_remote_path(file_path):
    """
    检测文件路径是否为远程路径
    :param file_path: 文件路径
    :return: True / False
    """

    return REMOTE_PATH_FLAG in file_path


def copy_remote_file_to_local(remote_file_path, local_file_path=TIFF_IMAGE_RESOURCE_PATH):
    """
    检测是否为远程路径，若是则拷贝文件至本地临时目录
    :param remote_file_path: 远程文件目录
    :param local_file_path: 本地文件目录
    :return: 实际文件目录
    """

    if not os.path.exists(local_file_path):
        os.makedirs(local_file_path, exist_ok=True)

    if is_remote_path(remote_file_path):
        basename = os.path.basename(remote_file_path)
        local_file_path = os.path.join(local_file_path, basename)

        print("COPY FILE ...\nFROM %s\nTO %s" % (remote_file_path, local_file_path))
        shutil.copy(remote_file_path, local_file_path)

        return local_file_path
    else:
        return remote_file_path


def remove_redundant_element(src_dir_path, dst_dir_path, limit):
    """
    移除多余细胞图像
    :param src_dir_path: 待处理细胞文件夹
    :param dst_dir_path:  被移除出来的细胞文件存放目录
    :param limit: 保持数量，即需要保留的细胞数量
    :return:
    """
    files = os.listdir(src_dir_path)

    random.shuffle(files)
    for file in files[limit:]:
        shutil.move(os.path.join(src_dir_path, file), dst_dir_path)


def read_from_labelme_xml(xml_files_path):
    """
    读入 xml 文件标注点信息， 来自 Labelme 的标注文件
    :param xml_files_path:
    :return:
    """
    tree = parse(xml_files_path)
    collection = tree.documentElement

    # 标注点数组
    lst = []

    objects = collection.getElementsByTagName("object")
    for index, obj in enumerate(objects):
        name = obj.getElementsByTagName('name')[0].childNodes[0].data
        box = obj.getElementsByTagName('bndbox')[0]
        xmin = box.getElementsByTagName('xmin')[0].childNodes[0].data
        ymin = box.getElementsByTagName('ymin')[0].childNodes[0].data
        xmax = box.getElementsByTagName('xmax')[0].childNodes[0].data
        ymax = box.getElementsByTagName('ymax')[0].childNodes[0].data

        xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
        lst.append((name, xmin, ymin, xmax - xmin, ymax - ymin))
        # lst.append({
        #     "type": name,
        #     "x": xmin,
        #     "y": ymin,
        #     "w": xmax - xmin,
        #     "h": ymax - ymin,
        # })

    return lst


def write_to_labelme_xml(points_dict, xml_save_path=LABELME_DEFAULT_XML_OUTPUT_PATH, image_size=LABELME_DEFAULT_IMAGE_SIZE):
    """
    将标注点信息写入 xml 文件， 用于 Labelme 审核
    :param points_dict:
    :param xml_save_path: xml 文件写入路径
    :param image_size: 待写入的 Image 文件尺寸
    :return:
    """

    count = 0
    total = len(points_dict)

    for key, lst in points_dict.items():
        count += 1
        print("GENERATE %s / %s %s ..." % (count, total, key + '.xml'))
        root = ET.Element("annotation")
        ET.SubElement(root, "folder").text = "folder"
        ET.SubElement(root, "filename").text = key + ".jpg"
        ET.SubElement(root, "path").text = "path"

        source = ET.SubElement(root, "source")
        ET.SubElement(source, "database").text = "Unknown"

        size = ET.SubElement(root, "size")
        ET.SubElement(size, "width").text = str(image_size)
        ET.SubElement(size, "height").text = str(image_size)
        ET.SubElement(size, "depth").text = "3"

        ET.SubElement(root, "segmented").text = "0"

        for point in lst:
            object = ET.SubElement(root, "object")
            ET.SubElement(object, "name").text = point['name']
            ET.SubElement(object, "pose").text = "Unspecified"
            ET.SubElement(object, "truncated").text = "0"
            ET.SubElement(object, "difficult").text = "0"
            bndbox = ET.SubElement(object, "bndbox")
            ET.SubElement(bndbox, "xmin").text = str(int(point['xmin']))
            ET.SubElement(bndbox, "ymin").text = str(int(point['ymin']))
            ET.SubElement(bndbox, "xmax").text = str(int(point['xmax']))
            ET.SubElement(bndbox, "ymax").text = str(int(point['ymax']))

        raw_string = ET.tostring(root, "utf-8")
        reparsed = parseString(raw_string)

        if not os.path.exists(xml_save_path):
            os.makedirs(xml_save_path)

        with open(os.path.join(xml_save_path, key + ".xml"), "w") as o:
            o.write(reparsed.toprettyxml(indent="\t"))


if __name__ == '__main__':
    filename = '1-p0.0000_markedAs_ACTINO_2018-06-20_18_37_06_x34602_y10123_w145_h172_2x.jpg'
    print(get_location_from_filename(filename))
