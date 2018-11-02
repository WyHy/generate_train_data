import os
import csv

CLASSES = ["IDENTIFIER", "HSIL", "ASCH", "LSIL", "ASCUS", "SCC", "EC", "AGC", "FUNGI", "TRI", "CC", "ACTINO", "VIRUS", "MC", "SC", "RC", "GEC", ]


def count(path):
    lst = []
    files = os.listdir(path)

    total = len(files)
    for index, file in enumerate(files):
        basename, _ = os.path.splitext(os.path.basename(file))
        print("%s / %s %s" % (index + 1, total, basename))

        obj = {"IDENTIFIER": basename}

        parent = os.path.join(path, file)
        classifications = os.listdir(parent)
        for clas in classifications:
            children_path = os.path.join(parent, clas)
            obj[clas] = len(os.listdir(children_path))

        lst.append(obj)

    return lst


if __name__ == '__main__':
    path = "/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181102_ZHENGZHOU/CELLS"
    output_path = "/home/cnn/Development/DATA/CELL_CLASSIFIED_JOB_20181102_ZHENGZHOU/cells_count_by_pathology_20181102.txt"

    lst = count(path)
    with open(output_path, 'w', newline='') as o:
        writer = csv.DictWriter(o, CLASSES)
        writer.writerows(lst)


