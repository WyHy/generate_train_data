# coding: utf-8

"""
基于模型处理生成的 csv 文件，对比原始的大图 xml 信息，按一下类别对细胞进行归类
在已知原始 xml 信息的条件下，分别提取

1. 新模型漏标的细胞
2. 模型标注分类与原始审核分类 类别不一致的细胞
3. 新识别的细胞
"""
import os

from utils import read_from_labelme_xml, cal_IOU, FilesScanner


def generate_csv_path_dict(csv_files_path):
    """
    模型生成的 csv 文件<名称：路径> dict
    :param csv_files_path:  csv 文件路径
    :return:  dict
    """

    files = FilesScanner(csv_files_path, ['_clas.csv']).get_files()

    dict_ = {}
    for file in files:
        basename = os.path.basename(file).replace("_clas.csv", "")
        dict_[basename] = file

    return dict_


def generate_xml_path_dict(xml_path_lst):
    """
    生成 xml 文件 <名称： 路径> dict
    :param xml_path_lst:  xml 文件路径
    :return:  dict
    """

    files = FilesScanner(xml_path_lst, ['.xml']).get_files()

    dict_ = {}
    for file in files:
        basename = os.path.basename(file).replace(".xml", "")
        dict_[basename] = file

    return dict_


def cell_classification(xml_path_lst, csv_path_lst):
    """
    基于
    :param xml_path_lst:  xml 文件路径列表
    :param csv_path_lst:  csv 文件路径列表
    :return:
    """

    # 模型漏标的细胞集合
    dict_miss = {}

    # 模型诊断类别与原始手工标注类别不一致的细胞集合
    dict_modify = {}

    # 新识别出的细胞集合
    dict_new = {}

    xml_dict = generate_xml_path_dict(xml_path_lst)
    csv_dict = generate_csv_path_dict(csv_path_lst)

    print("LENGTH OF XML: %s" % len(xml_dict))
    print("LENGTH OF CSV: %s" % len(csv_dict))
    count = 0
    for key, lst01 in xml_dict.items():
        if key in csv_dict:
            pass
        else:
            count += 1

    print("LENGTH OF CSV: %s" % count)

    # label_lst = []
    # for path in xml_path_lst:
    #     label_lst.extend(read_from_labelme_xml(path))
    #
    # new_lst = []
    # for point in label_lst:
    #     type01, x01, y01, w01, h01 = point
    #     for item in new_lst:
    #         type02, x02, y02, w02, h02 = item
    #         ratio = cal_IOU((x02, y02, w02, h02), (x01, y01, w01, h01))
    #         if ratio > 0.8 and type01 == type02:
    #             break
    #     else:
    #         new_lst.append(point)
    #
    # return new_lst


if __name__ == '__main__':

    # 大图 xml 文件存放路径
    xml_path_lst = '/home/tsimage/Development/DATA/XMLS_SELECTED'

    # 大图 csv 文件存放路径
    csv_path_lst = '/home/tsimage/Development/DATA/meta_01'

    cell_classification(xml_path_lst, csv_path_lst)
