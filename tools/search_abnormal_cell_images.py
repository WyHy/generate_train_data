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


if __name__ == '__main__':
    get_abnormal_tiff_list()
