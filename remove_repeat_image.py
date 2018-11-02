import os
import re
import shutil
import sys

from utils import FilesScanner, cal_IOU

REPEAT_FILE_SAVE_PATH = '/home/data_samba/DATA/4TRAIN_DATA/20181026/BASE_PURE_DATA/PURE_CELL_DATA_20181029/REPEAT_CELL_IMAGE_COLLECTION'


def do_repeat_remove(path):
    files = FilesScanner(path).get_files()

    pattern = re.compile(r'(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_s(\d+).jpg')

    dict_ = {}
    for file in files:
        basename = os.path.basename(file)
        cell_type = os.path.basename(os.path.dirname(file))

        items = re.findall(pattern, basename)[0]
        key = "_".join(items[:-1])

        if key not in dict_:
            dict_[key] = items[1:-1]
        else:
            save_path = os.path.join(REPEAT_FILE_SAVE_PATH, cell_type)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # shutil.move(file, save_path)
            shutil.copy(dict_[key], save_path)

    return dict_


def do_similar_remove(path):
    files = FilesScanner(path).get_files()

    pattern = re.compile(r'(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_s(\d+).jpg')

    dict_ = {}
    total = len(files)
    for index, file in enumerate(files):
        print("%s / %s ..." % (index + 1, total))
        basename = os.path.basename(file)
        cell_type = os.path.basename(os.path.dirname(file))

        items = re.findall(pattern, basename)[0]
        big_name, x, y, w, h, _ = items

        x, y, w, h = int(x), int(y), int(w), int(h)
        if big_name in dict_:
            lst = dict_[big_name]
            for item in lst:
                x_, y_, w_, h = item[:-1]
                if cal_IOU((x, y, w, h), (x_, y_, w_, h)) > 0.6:
                    save_path = os.path.join(REPEAT_FILE_SAVE_PATH, cell_type)
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)

                    shutil.move(file, save_path)
                    # shutil.copy(item[-1], save_path)
                    # shutil.copy(file, save_path)
            else:
                dict_[big_name].append((x, y, w, h, file))
        else:
            dict_[big_name] = [(x, y, w, h, file)]

    return dict_


if __name__ == '__main__':

    # path = "/home/data_samba/DATA/4TRAIN_DATA/20181026/BASE_PURE_DATA/PURE_CELL_DATA_20181029/PURE_CELL_DATA_COLLECTION"
    # # path = "/home/data_samba/DATA/4TRAIN_DATA/20181026/BASE_PURE_DATA/PURE_CELL_DATA_20181029/MERGED"
    # dict_ = do_repeat_remove(path)
    label = sys.argv[1]
    path = "/home/data_samba/DATA/4TRAIN_DATA/20181026/BASE_PURE_DATA/PURE_CELL_DATA_20181029/REGENERATE_PURE_CELL_COLLECTION/%s" % label

    dict_ = do_similar_remove(path)

    count = 0
    for key, lst in dict_.items():
        count += len(lst)

    print("UNIQUE CELL IMAGE COUNT: %s" % count)
