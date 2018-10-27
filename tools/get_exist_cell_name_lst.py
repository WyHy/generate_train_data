import os


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


if __name__ == '__main__':
    pathes = [
        '/home/data_samba/DATA/4TRAIN_DATA/20181026/DATA_IN_PREPARE/CHECKED_BY_ZHU',
        '/home/data_samba/DATA/4TRAIN_DATA/20181026/DATA_IN_PREPARE/ROUND_01_TRAIN_DATA',
    ]

    with open("names_lst.txt", 'w') as o:
        for path in pathes:
            names = FilesScanner(path, ['.jpg']).get_files()
            for name in names:
                o.write("%s\n" % os.path.basename(name))
