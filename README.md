# generate_train_data
tools for generate train data for MACHINE LEARNING

# Steps
#### 1. 生成大图对应审核细胞相关 xml 文件

`python generate_tiff_xml.py`

#### 2. 根据 xml 文件读取并保存细胞图像供算法人员筛选

`python generate_cell_images_from_xml.py`

#### 3. 根据算法人员筛选后的细胞文件生成大图对应筛选细胞相关 xml 文件

`python regenerate_tiff_xml.py`

#### 4. 基于 xml 文件统计按类别统计细胞个数

`python count_cell_by_class_from_xml.py`
