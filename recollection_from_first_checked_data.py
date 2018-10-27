# coding: utf-8

import os
import shutil
from utils import FilesScanner
from contants import PATHOLOGY_TYPE_CLASSES

def collect(image_root_path, collect_files_save_path):
    images = FilesScanner(path, ['.jpg']).get_files()

    for image in images:
        basename = os.path.basename(image)
        cell_type = os.path.basename(os.path.dirname(image))

        if '_' in cell_type:
            cell_type = cell_type.split('_')[0]

        if '-' in cell_type:
            cell_type = cell_type.split('-')[0]

        if cell_type in PATHOLOGY_TYPE_CLASSES:
            pass
        else:
            raise Exception("%s NOT CLASSIFIED" % image)


if __name__ == '__main__':
    image_root_path = ""
    collect_files_save_path = ""

    collect(image_root_path, collect_files_save_path)



