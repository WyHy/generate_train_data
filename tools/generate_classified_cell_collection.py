# coding: utf-8

"""
基于模型处理生成的 csv 文件，对比原始的大图 xml 信息，按一下类别对细胞进行归类
在已知原始 xml 信息的条件下，分别提取

1. 新模型漏标的细胞
2. 模型标注分类与原始审核分类 类别不一致的细胞
3. 新识别的细胞
"""
import os
import sys
import csv
import re
import openslide
import xml
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.append('..')

from tslide.tslide import TSlide
from utils import read_from_labelme_xml, cal_IOU, FilesScanner, get_tiff_dict

pattern = re.compile(r'^(.*?)_(\d+)_(\d+)$')

tiff_dict = get_tiff_dict()

TEST_IMAGE_SAVE_PATH = '/home/tsimage/Development/DATA/for_duplicate_removal_test'

def generate_csv_path_dict(csv_files_path):
    """
    模型生成的 csv 文件<名称：路径> dict
    :param csv_files_path:  csv 文件路径
    :return:  dict
    """

    files = FilesScanner(csv_files_path, ['.csv']).get_files()

    dict_ = {}
    for file in files:
        basename = os.path.basename(file)
        if basename.endswith('_clas.csv'):
            basename = basename.replace("_clas.csv", "")
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


def remove_repeat_cells(key, csv_file_path):
    if key not in tiff_dict:
        raise Exception("XCEPTION PREPROCESS %s NOT FOUND" % key)

    tiff_path = tiff_dict[key]

    try:
        try:
            slide = openslide.OpenSlide(tiff_path)
        except:
            slide = TSlide(tiff_path)
    except:
        raise Exception('TIFF FILE OPEN FAILED => %s' % tiff_path)


    save_path = os.path.join(TEST_IMAGE_SAVE_PATH, key)

    with open(csv_file_path) as f:
        lines = csv.reader(f)

        dict_ = {}
        unique_cells_collection = []

        next(lines, None)

        count = 0
        for line in lines:
            name, label01, accu01, label02, accu02, xmin, ymin, xmax, ymax = line
            xmin, ymin, xmax, ymax = float(xmin), float(ymin), float(xmax), float(ymax)
            x, y, w, h = xmin, ymin, int(xmax - xmin + 0.5), int(ymax - ymin + 0.5)

            tiff_name, start_x, start_y = re.findall(pattern, name)[0]
            start_x, start_y = int(start_x), int(start_y)

            x, y = int(start_x + x), int(start_y + y)

            origin_save_path = os.path.join(save_path, "origin", label02)
            removal_save_path = os.path.join(save_path, "removal", label02)


            if not os.path.exists(origin_save_path):
                os.makedirs(origin_save_path)

            if not os.path.exists(removal_save_path):
                os.makedirs(removal_save_path)

            patch = slide.read_region((x, y), 0, (w, h)).convert("RGB")
            image_name = "%s_x%s_y%s_w%s_h%s.jpg" % (key, x, y, w, h)

            patch.save(os.path.join(origin_save_path, image_name))
            for item in unique_cells_collection:
                label, x_, y_, w_, h_ = item

                ratio = cal_IOU((x, y, w, h), (x_, y_, w_, h_))

                if ratio > 0.7 and label == label02:
                    break
            else:
                unique_cells_collection.append((label02, x, y, w, h))
                patch.save(os.path.join(removal_save_path, image_name))

            count += 1

        print("ORIGIN POINTS COLLECTION LENGTH: %s" % count)
        print("AFTER DUPLICATE REMOVAL COLLECTION LENGTH: %s" % len(unique_cells_collection))

        return unique_cells_collection


def read_data_from_xml(xml_file_path):
    DOMTree = xml.dom.minidom.parse(xml_file_path)
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")

    labelled_cells_collection = []
    for index, annotation in enumerate(annotations):
        cell = annotation.getElementsByTagName("Cell")[0]
        x = int(cell.getAttribute("X"))
        y = int(cell.getAttribute("Y"))
        w = int(cell.getAttribute("W"))
        h = int(cell.getAttribute("H"))  
        label = cell.getAttribute("Type")

        labelled_cells_collection.append((label, x, y, w, h))

    return labelled_cells_collection


def write_to_txt(name, lst):
    with open(name, 'w') as o:
        o.writelines(['%s\n' % ','.join([str(ele) for ele in item]) for item in lst])


def cell_classification(xml_path_lst, csv_path_lst):
    """
    基于
    :param xml_path_lst:  xml 文件路径列表
    :param csv_path_lst:  csv 文件路径列表
    :return:
    """

    print("GET XML AND CSV <NAME: PATH> DICT...")
    xml_dict = generate_xml_path_dict(xml_path_lst)
    csv_dict = generate_csv_path_dict(csv_path_lst)

    # GET NEW MODEL OUTPUT POINTS COLLECTION
    csv_points_dict = {}

    removal_xml_save_path = '/home/tsimage/Development/DATA/removal_xmls'

    keys = list(csv_dict.keys())
    total = len(keys)

    print("GET CSV LABELLED POINTS COLLECTION ...")
    # read csv
    for index, key in enumerate(keys):
        print("GET CSV DATA %s / %s %s..." % (index+1, total, key))
        removal_xml_data_path = os.path.join(removal_xml_save_path, key + ".txt")

        lst = []
        if os.path.exists(removal_xml_data_path):
            with open(removal_xml_data_path) as f:
                lines = f.readlines()
                for line in lines:
                    label, x, y, w, h = line.replace("\n", "").split(',')
                    lst.append((label, int(x), int(y), int(w), int(h)))
        else:
            lst = remove_repeat_cells(key, csv_dict[key])
            write_to_txt(removal_xml_data_path, lst)

        csv_points_dict[key] = lst


    xml_points_dict = {}
    keys = list(xml_dict.keys())
    total = len(keys)

    print("GET XML LABELLED POINTS COLLECTION ...")
    # read xml
    for index, key in enumerate(keys):
        print("GET XML DATA %s / %s %s..." % (index+1, total, key))
        lst = read_data_from_xml(xml_dict[key])
        xml_points_dict[key] = lst


    print('CELL COMPARE AND CLASSIFICATION ...')
    # compare and classification
    keys = list(csv_points_dict.keys())
    total = len(keys)

    # 模型诊断类别与原始手工标注类别不一致的细胞集合
    dict_modify = {}

    # 新识别出的细胞集合
    dict_new = {}

    # 新识别出的细胞集合
    dict_same = {}

    for index, key in enumerate(keys):
        print("CLASSIFICATION %s / %s %s..." % (index+1, total, key))

        same_lst = []
        new_lst = []
        modify_lst = []

        csv_lst = csv_points_dict[key]
        xml_lst = xml_points_dict[key]

        for csv_item in csv_lst:
            label01, x01, y01, w01, h01 = csv_item

            for xml_item in xml_lst:
                label02, x02, y02, w02, h02 = xml_item

                ratio = cal_IOU((x02, y02, w02, h02), (x01, y01, w01, h01))
                if ratio > 0.8:
                    if label01 == label02:
                        same_lst.append(csv_item)
                    else:
                        modify_lst.append((label02, label01, x01, y01, w01, h01))

                    break
            else:
                new_lst.append(csv_item)

        dict_same[key] = same_lst
        dict_new[key] = new_lst
        dict_modify[key] = modify_lst

    # 模型漏标的细胞集合
    dict_miss = {}

    keys = list(xml_points_dict.keys())
    total = len(keys)
    for index, key in enumerate(keys):
        if key not in csv_dict:
            continue

        miss_lst = []

        csv_lst = csv_points_dict[key]
        xml_lst = xml_points_dict[key]

        for xml_item in xml_lst:
            label01, x01, y01, w01, h01 = xml_item

            for csv_item in csv_lst:
                label02, x02, y02, w02, h02 = csv_item

                if cal_IOU((x02, y02, w02, h02), (x01, y01, w01, h01)) > 0.8:
                    break
            else:
                miss_lst.append(xml_item)

        dict_miss[key] = miss_lst


    data_after_classification_save_path = '/home/tsimage/Development/DATA/data_after_removal'
    for index, key in enumerate(keys):
        save_path = os.path.join(data_after_classification_save_path, key)

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        if key in dict_same:
            write_to_txt(os.path.join(save_path, 'same.txt'), dict_same[key])

        if key in dict_new:
            write_to_txt(os.path.join(save_path, 'new.txt'), dict_new[key])

        if key in dict_modify:
            write_to_txt(os.path.join(save_path, 'modify.txt'), dict_modify[key])

        if key in dict_miss:
            write_to_txt(os.path.join(save_path, 'miss.txt'), dict_miss[key])


    # print("WRITE SAME CELL COLLECTION TO TXT ...")

    # # same cell
    # save_path = os.path.join(data_after_classification_save_path, 'same')
    # if not os.path.exists(save_path):
    #     os.makedirs(save_path)

    # for key, lst in dict_same.items():
    #     write_to_txt(os.path.join(save_path, key + '.txt'))

    # print("WRITE NEW CELL COLLECTION TO TXT ...")

    # # new cell
    # save_path = os.path.join(data_after_classification_save_path, 'new')
    # if not os.path.exists(save_path):
    #     os.makedirs(save_path)

    # for key, lst in dict_new.items():
    #     write_to_txt(os.path.join(save_path, key + '.txt'))

    # print("WRITE MODIFY CELL COLLECTION TO TXT ...")
    
    # # modify cell
    # save_path = os.path.join(data_after_classification_save_path, 'modify')
    # if not os.path.exists(save_path):
    #     os.makedirs(save_path)

    # for key, lst in dict_modify.items():
    #     write_to_txt(os.path.join(save_path, key + '.txt'))


    # # 模型漏标的细胞集合
    # dict_miss = {}

    # keys = list(xml_points_dict.keys())
    # total = len(keys)
    # for index, key in enumerate(keys):
    #     if key not in csv_dict:
    #         continue

    #     miss_lst = []

    #     csv_lst = csv_points_dict[key]
    #     xml_lst = xml_points_dict[key]

    #     for xml_item in xml_lst:
    #         label01, x01, y01, w01, h01 = xml_item

    #         for csv_item in csv_lst:
    #             label02, x02, y02, w02, h02 = csv_item

    #             if cal_IOU((x02, y02, w02, h02), (x01, y01, w01, h01)) > 0.8:
    #                 break
    #         else:
    #             miss_lst.append(xml_item)

    #     dict_miss[key] = miss_lst

    # print("WRITE MISS CELL COLLECTION TO TXT ...")

    # # miss cell
    # save_path = os.path.join(data_after_classification_save_path, 'miss')
    # if not os.path.exists(save_path):
    #     os.makedirs(save_path)

    # for key, lst in dict_miss.items():
    #     write_to_txt(os.path.join(save_path, key + '.txt'))


def generate_classified_cell_images(key, classified_data_save_path):
    tiff_path = tiff_dict[key]

    try:
        try:
            slide = openslide.OpenSlide(tiff_path)
        except:
            slide = TSlide(tiff_path)
    except:
        raise Exception('TIFF FILE OPEN FAILED => %s' % tiff_path)

    txt_data_path = os.path.join(classified_data_save_path, key)
    
    txts = os.listdir(txt_data_path)
    try:
        for txt in txts:
            if txt.endswith('.txt'):
                basename, _ = os.path.splitext(os.path.basename(txt))
                with open(os.path.join(txt_data_path, txt)) as f:
                    lines = f.readlines()

                    image_save_path = os.path.join(txt_data_path, basename)
                    for line in lines:
                        items = line.replace('\n', '').split(',')
                        if len(items) == 6:
                            label, label_, x, y, w, h = items
                            image_name = "%s_%s_x%s_y%s_w%s_h%s.jpg" % (key, label_, x, y, w, h)
                        else:
                            label, x, y, w, h = items
                            image_name = "%s_x%s_y%s_w%s_h%s.jpg" % (key, x, y, w, h)

                        save_path = os.path.join(image_save_path, label)
                        if not os.path.exists(save_path):
                            os.makedirs(save_path)

                        x, y, w, h = int(x), int(y), int(w), int(h)
                        patch = slide.read_region((x, y), 0, (w, h)).convert("RGB")
                        
                        patch.save(os.path.join(save_path, image_name))
    except:
        return 1, key

    return 0


if __name__ == '__main__':

    # # 大图 xml 文件存放路径
    # xml_path_lst = '/home/tsimage/Development/DATA/XMLS_SELECTED'

    # # 大图 csv 文件存放路径
    # csv_path_lst = '/home/tsimage/Development/DATA/meta_test'

    # cell_classification(xml_path_lst, csv_path_lst)


    classified_data_save_path = '/home/tsimage/Development/DATA/data_after_removal'
    names = os.listdir(classified_data_save_path)

    total = len(names)

    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []

    for name in names:
        # generate_classified_cell_images(name, classified_data_save_path)
        tasks.append(executor.submit(generate_classified_cell_images, name, classified_data_save_path))

    job_count = len(tasks)
    tiff_read_fail_records = []
    for future in as_completed(tasks):
        result = future.result()  # get the returning result from calling fuction
        if result == 0:
            pass
        else:
            tiff_read_fail_records.append(result[1])

        job_count -= 1
        print("LAST JOB NUM %s" % job_count)

    print("\n".join(tiff_read_fail_records))


    # classified_data_save_path = '/home/tsimage/Development/DATA/data_after_removal'
    # files = os.listdir(classified_data_save_path)

    # need_remove = []
    # for file in files:
    #     path = os.path.join(classified_data_save_path, file)
    #     items = os.listdir(path)

    #     if len(items) == 0:
    #         need_remove.append(path)

    # print('NEED REMOVE DIRS NUM: %' % len(need_remove))
    # for item in need_remove:
    #     os.removedirs(item)