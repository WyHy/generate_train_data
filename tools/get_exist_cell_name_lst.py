import os
import re
import shutil


def get_path_postfix(filename):
    """
    获取文件名和文件后缀
    :param filename: 待处理文件路径
    :return: (文件名， 文件后缀) 如：a.txt --> return ('a', '.txt')
    """
    basename = os.path.basename(filename)
    return os.path.splitext(basename)


class FilesScanner(object):
    """
    获取文件列表工具类
    """

    def __init__(self, files_path, postfix=None):
        """

        :param files_path: 待扫描文件路径
        :param postfix: 所需文件后缀，['.tif', '.kfb'], 默认为空，即获取该路径下所有文件
        """
        self.files_path = files_path

        if postfix:
            assert isinstance(postfix, list), 'argument [postfix] should be list'

        files = []
        if os.path.isfile(files_path):
            if postfix:
                _, ctype = get_path_postfix(files_path)
                if ctype in postfix:
                    files.append(files_path)
            else:
                files.append(files_path)

        if os.path.isdir(files_path):
            for root, dirs, filenames in os.walk(files_path):
                for filename in filenames:
                    if postfix:
                        _, ctype = get_path_postfix(filename)
                        if ctype in postfix:
                            files.append(os.path.join(root, filename))
                    else:
                        files.append(os.path.join(root, filename))
        # 替换为绝对路径
        files = [os.path.abspath(item) for item in files]

        self.files = files

    def get_files(self):
        return self.files


def get_tiff_name_lst():
    dst_path = "/home/data_samba/DATA/4TRAIN_DATA/20181026/DATA_IN_PREPARE/BIG_PIC"


if __name__ == '__main__':
    # a = ["HSIL", "ASCH", "LSIL", "ASCUS", "SCC", "EC", "AGC", "FUNGI", "TRI", "CC", "ACTINO", "VIRUS", "MC", "SC", "RC", "GEC", ]
    # print(" ".join([item + "_CENTER" for item in a]))

    pathes = [
        # '/home/data_samba/DATA/4TRAIN_DATA/20181026/DATA_IN_PREPARE/CHECKED_BY_ZHU',
        '/home/data_samba/DATA/4TRAIN_DATA/20181026/DATA_IN_PREPARE/ROUND_01_TRAIN_DATA/HSIL',
    ]

    # TC18053765_x46070_y20472_w26_h28_s110.jpg
    pattern = re.compile(r'(.*?)_x(\d+)_y(\d+)_w(\d+)_h(\d+)_s(\d+).jpg')
    # dst_path = "/home/data_samba/DATA/4TRAIN_DATA/20181026/DATA_IN_PREPARE/BIG_PIC"

    big_tiff_name = []
    for path in pathes:
        names = FilesScanner(path, ['.jpg']).get_files()
        for name in names:
            basename = os.path.basename(name)
            cell_type = os.path.basename(os.path.dirname(name))

            big_name, x, y, w, h, _ = re.findall(pattern, basename)[0]

            if big_name not in big_tiff_name:
                big_tiff_name.append(big_name)

            if int(w) > 608 or int(h) > 608:
                # save_path = os.path.join(path, cell_type + "_2-")
                save_path = "/home/data_samba/DATA/4TRAIN_DATA/20181026/DATA_IN_PREPARE/ROUND_01_TRAIN_DATA/HSIL_2-"
                if not os.path.exists(save_path):
                    os.makedirs(save_path)

                shutil.move(name, save_path)

    # for path in pathes:
    #     names = FilesScanner(path, ['.jpg']).get_files()
    #     for name in names:
    #         basename = os.path.basename(name)
    #         parent = os.path.dirname(name)
    #         cell_type = os.path.basename(parent)
    #
    #         if '_2-' in cell_type:
    #             pass
    #         else:
    #             big_name, x, y, w, h, _ = re.findall(pattern, basename)[0]
    #
    #             if big_name in big_tiff_name:
    #                 big_tiff_name.append(big_name)
    #
    #                 save_path = os.path.join(path, cell_type + "_2-")
    #                 if not os.path.exists(save_path):
    #                     os.makedirs(save_path)
    #
    #                 shutil.move(name, save_path)






