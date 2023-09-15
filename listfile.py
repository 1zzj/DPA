import os
import random
file_list = [file for file in os.listdir(r"H:\DataSet\DPA\data\Ds\image") if file.endswith(".tif")]

split_index = int(0.8 * len(file_list))

random.shuffle(file_list)

train_data = file_list[:split_index]
val_data = file_list[split_index:]

# 将数据写入文件
train_file = open(r"H:\DataSet\DPA\data\Ds\list\train.txt", "w")
val_file = open(r"H:\DataSet\DPA\data\Ds\list\val.txt", "w")

for item in train_data:
    train_file.write(str(item) + "\n")

for item in val_data:
    val_file.write(str(item) + "\n")

# 关闭文件
train_file.close()
val_file.close()