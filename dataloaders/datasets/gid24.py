from __future__ import print_function, division
import os
import random
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms
from dataloaders import custom_transforms as tr


class GIDData(Dataset):
    """
    GID24 dataset
    """
    NUM_CLASSES = 24+1

    def __init__(self, args, split):
        """
        :param split: train/val
        :param transform: transform to apply
        """
        super().__init__()
        self._base_dir = args.source_dir
        self._image_dir = os.path.join(self._base_dir, 'image')
        self._label_dir = os.path.join(self._base_dir, 'label')
        _splits_dir = os.path.join(self._base_dir, 'list')
        self.split = [split]  # split: train或val

        self.args = args
        # 存文件名
        self.im_ids = []
        # 存图片完整路径
        self.images = []
        # 存标签完整路径
        self.labels = []
        # 在初始化Dataset类时，完成数据路径的随机抽样
        for splt in self.split:
            # txt文件存训练集或验证集的图像名称，train.txt 和 val.txt 内容不同
            with open(os.path.join(os.path.join(_splits_dir, splt + '.txt')), "r") as f:
                lines = f.read().splitlines()
            # 打乱名称顺序&抽取
            if splt == 'train':
                lines = random.sample(lines, len(os.listdir(os.path.join(args.target_dir, args.target))))
            elif split == 'val':
                lines = random.sample(lines, 500)  # random.sample从lines中随机抽500个样本用于批次验证，限制验证集的规模，减少计算

            for ii, line in enumerate(lines):
                # 图像和标签的名称一致
                _image = os.path.join(self._image_dir, line + ".tif")
                _label = os.path.join(self._label_dir, line + ".png")
                assert os.path.isfile(_image)
                assert os.path.isfile(_label)
                self.im_ids.append(line)
                self.images.append(_image)
                self.labels.append(_label)

        assert (len(self.images) == len(self.labels))

        # Display stats
        print('Number of images in {}: {:d}'.format(split, len(self.images)))

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        _img, _target = self._make_img_gt_point_pair(index)
        sample = {'image': _img, 'label': _target}

        for split in self.split:
            if split == "train":
                return self.transform_tr(sample)
            elif split == 'val':
                return self.transform_val(sample)

    def _make_img_gt_point_pair(self, index):
        _img = Image.open(self.images[index]).convert('CMYK')
        _target = Image.open(self.labels[index])

        return _img, _target

    @staticmethod
    def transform_tr(sample):
        composed_transforms = transforms.Compose([
            tr.RandomHorizontalFlip(),
            tr.RandomGaussianBlur(),
            tr.Normalize(mean=(0.506, 0.371, 0.390, 0.363),
                         std=(0.254, 0.244, 0.231, 0.231)),
            tr.ToTensor()])

        return composed_transforms(sample)

    @staticmethod
    def transform_val(sample):
        composed_transforms = transforms.Compose([
            tr.Normalize(mean=(0.506, 0.371, 0.390, 0.363),
                         std=(0.254, 0.244, 0.231, 0.231)),
            tr.ToTensor()])

        return composed_transforms(sample)

    def __str__(self):
        return 'GID24 (split = ' + self.split[0] + ')'





