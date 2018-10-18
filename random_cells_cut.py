# Cut cells randomly. -- by mpc
import os
import random

import openslide
from concurrent.futures import ProcessPoolExecutor, as_completed
from tslide.tslide import TSlide

from utils import FilesScanner

KFB_DIR = ""
NORMAL_CELLS_DIR = ""
PATCH_NUM_NEED = 10
PATCH_SIZE = 1216


def worker(tiff_file_path, patch_save_path, patch_num_need=PATCH_NUM_NEED, path_size=(PATCH_SIZE, PATCH_SIZE)):
    """
    随机切图 worker，
    :param tiff_file_path: TIFF 文件路径
    :param patch_save_path:  切图存放路径
    :param patch_num_need:  随机切图数量
    :param path_size:  随机切图尺寸 （1024， 1024）
    :return:
    """

    # 获取 TIFF 文件句柄
    try:
        try:
            slide = openslide.OpenSlide(tiff_file_path)
        except:
            slide = TSlide(tiff_file_path)
    except:
        print("TIFF OPEN FAILED => %s" % tiff_file_path)
        return 1, tiff_file_path

    width, height = slide.dimensions

    # 获取随机坐标列表 x_lst
    x_lst = [int(random.random() * width) for _ in range(patch_num_need)]

    # 获取随机坐标列表 y_lst
    y_lst = [int(random.random() * height) for _ in range(patch_num_need)]

    random_point_lst = list(zip(x_lst, y_lst))

    # 获取大图文件名
    basename, _ = os.path.splitext(os.path.basename(tiff_file_path))
    # 切图大小
    w, h = path_size
    for index, (x, y) in enumerate(random_point_lst):
        save_path = os.path.join(patch_save_path, basename)
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)

        # 保存 PATCH
        image_name = "%s_x%s_y%s_w%s_h%s_s%s.jpg" % (basename, x, y, w, h, index)
        slide.read_region((x, y), 0, (w, h)).convert("RGB").save(os.path.join(save_path, image_name))

    return 0, None


def random_cells_cut_progress(in_dir, out_path, num, size):
    """
    多进程切图方法
    :param in_dir: 输入 TIFF 文件路径
    :param out_path: 输出 PATCH 存放路径
    :param num: 单文件所需切图数量
    :param size: 切图文件大小
    :return:
    """

    kfbs = FilesScanner(in_dir, ['.kfb']).get_files()

    # 设置进程池
    executor = ProcessPoolExecutor(max_workers=20)
    tasks = []
    for index, path in enumerate(kfbs):
        tasks.append(executor.submit(worker, path, out_path, num, (size, size)))

    job_count = len(tasks)

    # 失败任务统计
    fail_task_collection = []
    for future in as_completed(tasks):
        status, _ = future.result()
        if status == 1:
            fail_task_collection.append(_)

        job_count -= 1
        print("LAST JOB NUM %s" % job_count)


if __name__ == '__main__':
    # 输入 TIFF 文件路径
    tiff_file_dir = ''
    # 输出切图存放路径
    patch_save_dir = ''
    
    random_cells_cut_progress(tiff_file_dir, patch_save_dir, PATCH_NUM_NEED, PATCH_SIZE)
