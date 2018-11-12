import os
import csv
import openslide
from tslide.tslide import TSlide
from utils import FilesScanner


def read_clas_xmls(csv_path):
    with open(csv_path) as f:
        lines = csv.reader(f)

        points_lst = []

        next(lines, None)
        for line in lines:
            name, label01, accu01, label02, accu02, xmin, ymin, w, h = line
            accu02, xmin, ymin, w, h = float(accu02), float(xmin), float(ymin), float(w), float(h)
            x0, y0 = [int(item) for item in name.split('_')]

            x, y = xmin + x0, ymin + y0
            points_lst.append({
                "label": label02,
                "accuracy": accu02,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
            })

    return points_lst


def cut_cells(tiff_path, points_lst, output_dir, N=1):
    basename, _ = os.path.splitext(os.path.basename(tiff_path))

    try:
        slide = openslide.OpenSlide(tiff_path)
    except:
        slide = TSlide(tiff_path)

    for point in points_lst:
        cell_save_dir = os.path.join(output_dir, basename, point['label'])
        os.makedirs(cell_save_dir, exist_ok=True)

        x, y, w, h = point['x'], point['y'], point['w'], point['h']
        image_name = "1-p{:.10f}_{}_x{}_y{}_w{}_h{}_{}X.jpg".format(1 - point['accuracy'], basename, x, y, w, h, N)
        cell_save_path = os.path.join(cell_save_dir, image_name)

        slide.read_region((int(x + (1 - N) * w / 2), int(y + (1 - N) * h / 2)), 0, (int(N * w), int(N * h))).convert("RGB").save(cell_save_path)


def collect_cells_by_accuracy(path, accuracy, output):
    cell_images = FilesScanner(path, ['.jpg'])




if __name__ == '__main__':
    path = ""
    csvs = os.listdir()



