import os
import re
import shutil
import sys

sys.path.append("..")

from utils import FilesScanner

# 1-p0.1718_TC18050036_x34939_y52118_w107_h105_2x.jpg
# 1-p0.5982_TC18053765_x46070_y20472_w26_h28_.jpg
pattern = re.compile(r'1-p0.\d{4}_(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_?(\dx)?.jpg')

src_path = "/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181022/CELLS/TIFFS_CHECKED"
dst_path = "/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181022/CELLS/ABNORMAL_IMAGE_COLLECTIONS"

images = FilesScanner(src_path).get_files()

for path in images:
    basename = os.path.basename(path)
    items = re.findall(pattern, basename)

    if items:
        print(items)
    else:
        print(basename)

    continue
    big_name, x, y, w, h, _ = items[0]

    if int(w) > 500 or int(h) > 500:
        shutil.copy(path, dst_path)
