# coding: utf-8
import os

import openslide

from tslide import TSlide
from utils import FilesScanner

tiff_resource_path = ''
tiffs = FilesScanner(tiff_resource_path, ['.kfb', '.tif']).get_files()

files = {}
for item in tiffs:
    basename = os.path.basename(item)
    if item in files:
        files[item].append(item)
    else:
        files[item] = [item]

for key, lst in files.items():
    if len(lst) > 1:
        print(lst)

# for tiff in tiffs:
#     try:
#         try:
#             slide = openslide.OpenSlide(tiff)
#         except:
#             slide = TSlide(tiff)
#     except:
#         print("TIFF OPEN FAILED => \n%s" % tiff)
