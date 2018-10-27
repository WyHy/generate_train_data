import os
import re
import shutil
import sys

sys.path.append("..")

from utils import FilesScanner


def find_abnormal():
    # 1-p0.1718_TC18050036_x34939_y52118_w107_h105_2x.jpg
    # 1-p0.5982_TC18053765_x46070_y20472_w26_h28_.jpg
    pattern = re.compile(r'1-p0.\d{4}_(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_?(\dx)?.jpg')

    src_path = "/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181022/CELLS/TIFFS_CHECKED"
    dst_path = "/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181022/CELLS/ABNORMAL_IMAGE_COLLECTIONS"

    images = FilesScanner(src_path, ['.jpg']).get_files()

    for path in images:
        basename = os.path.basename(path)
        items = re.findall(pattern, basename)

        if items:
            # print(items)
            pass
        else:
            print(basename)

        big_name, x, y, w, h, _ = items[0]

        if int(w) > 500 or int(h) > 500:
            shutil.copyfile(path, os.path.join(dst_path, "%s_%s_%s_%s_%s.jpg" % (big_name, x, y, w, h)))


def get_abnormal_tiff_list():
    src_path = '/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181022/CELLS/ABNORMAL_IMAGE_COLLECTIONS'

    files = FilesScanner(src_path, ['.jpg']).get_files()

    lst = []
    for item in files:
        basename = os.path.basename(item)
        key = basename.split('_')[0]

        if key in lst:
            pass
        else:
            lst.append(key)

    with open("4x_tiff_lst.txt", 'w') as o:
        o.write("\n".join(lst))


def get_tiff_location():
    pathes = [
        '/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181022/CELLS/TIFFS',
        '/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181024/CELLS/TIFFS_READY_TO_CHECK',
        '/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181025_1/CELLS/20181025',
        '/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181026/CELLS/20181025_1',
    ]

    dict_ = {}
    for path in pathes:
        tiffs = os.listdir(path)
        for tiff in tiffs:
            tiff = tiff.replace(" ", "-")
            if tiff in dict_:
                raise Exception(tiff, dict_[tiff])
            else:
                dict_[tiff] = os.path.join(path, tiff)

    with open("/home/cnn/Development/code/generate_train_data/tools/4x_tiff_lst.txt") as f:
        lines = f.readlines()
        names = [line.replace("\n", "") for line in lines]

    count = 0

    lst = []
    for name in names:
        if name in dict_:
            lst.append(dict_[name])
            count += 1

    print("SHOW AGAIN NUM: %s" % count)

    return lst


if __name__ == '__main__':
    # get_abnormal_tiff_list()

    lst = get_tiff_location()

    dst = "/home/cnn/Development/DATA/RECHECK_DATA_IN_20181026"

    with open("names_lst.txt") as f:
        lines = f.readlines()
        already_exist_images = ["_".join(line.replace("\n", '').split("_")[:-1]) for line in lines]

    print(already_exist_images[:100])

    pattern = re.compile(r'1-p0.\d{4}_(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_?(\dx)?.jpg')

    for item in lst:
        images = FilesScanner(item, ['.jpg']).get_files()
        for name in images:
            basename = os.path.basename(name)
            big_name, x, y, w, h, _ = re.findall(pattern, basename)[0]
            basename = "%s_x%s_y%s_w%s_h%s" % (big_name, x, y, w, h)

            cell_type = os.path.basename(os.path.dirname(name))

            if basename not in already_exist_images:
                print("WA %s is NEW " % basename)
                save_path = os.path.join(dst, 'NO_CHECK', big_name, cell_type)
            else:
                print("EEEE %s is EXIST!" % basename)
                save_path = os.path.join(dst, 'CHECKED', cell_type)

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            shutil.copy(name, save_path)
