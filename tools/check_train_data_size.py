import os
import shutil

from PIL import Image
import sys

sys.path.append('..')

from utils import FilesScanner

OUT_PUT_PATH = "/home/data-server/Documents/wangy/DATA/size_check"


def find_size_over_608(path):
    images = FilesScanner(path, ['.jpg']).get_files()

    total = len(images)
    for index, image in enumerate(images):
        basename = os.path.basename(image)
        ctype = os.path.basename(os.path.dirname(image))

        print("%s / %s %s" % (index + 1, total, basename))
        img = Image.open(image)
        w, h = img.size

        if w > 608 or h > 608:
            save_path = os.path.join(OUT_PUT_PATH, ctype)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            shutil.copy(image, save_path)


if __name__ == '__main__':
    path = '/home/data_samba/DATA/4TRAIN_DATA/20181026/DATA_FOR_TRAIN/CELLS'
    find_size_over_608(path)
