# coding: utf-8
import os
import xml

from constants import PATHOLOGY_TYPE_CLASSES, CELL_COUNT_FILE_NAME, CHECKED_CELL_XML_SAVE_PATH, \
    DATA_RESOURCE_ROOT_PATH
from utils import FilesScanner


def count_from_xml(xmls_path, save_path=DATA_RESOURCE_ROOT_PATH):
    """
    从 xml 文件解析大图标注点坐标类别，按类别统计细胞数量
    :param xmls_path: xml 文件路径
    :param save_path: 细胞文件生成目录
    :return:
    """

    # 创建生成目录
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # xml 文件路径列表
    xmls = FilesScanner(xmls_path, ['.xml']).get_files()
    # xml 文件数量
    size = len(xmls)

    class_count = dict(zip(PATHOLOGY_TYPE_CLASSES, [0] * len(PATHOLOGY_TYPE_CLASSES)))
    count_file_save_path = os.path.join(save_path, CELL_COUNT_FILE_NAME)

    # 细胞总数统计
    total = 0

    # 如果计数文件存在则直接读取并返回
    if os.path.exists(count_file_save_path):
        with open(count_file_save_path) as f:
            lines = f.readlines()

            for line in lines:
                key, value = line.replace("\n", '').split('\t')
                print("%s\t%s" % (key, value))

                class_count[key] = int(value)
                total += class_count[key]

            return class_count

    for index, path in enumerate(xmls):
        print("%s / %s %s" % (index + 1, size, os.path.basename(path)))

        DOMTree = xml.dom.minidom.parse(path)
        collection = DOMTree.documentElement

        annotations = collection.getElementsByTagName("Annotation")
        for index, annotation in enumerate(annotations):
            cell = annotation.getElementsByTagName("Cell")[0]
            class_type = cell.getAttribute("Type")

            class_count[class_type] += 1

    with open(count_file_save_path, 'w') as o:
        for item in PATHOLOGY_TYPE_CLASSES:
            count = class_count[item]
            total += count
            o.write("%s\t%s\n" % (item, count))
            print("%s\t%s" % (item, count))

        o.write("total cell\t%s\n" % total)
        o.write("total xml\t%s\n" % size)
        print("total cell\t%s" % total)
        print("total xml\t%s" % size)

    print("COUNT RESULTS IS WRITED TO %s" % count_file_save_path)

    return class_count


if __name__ == '__main__':
    # 获取 xml 文件路径列表
    count_from_xml(CHECKED_CELL_XML_SAVE_PATH)
