import torch
import math
import numpy as np
import torch.nn.functional as F


def pseudolabel(target, epoch, args):
    """
    target : model输出的结果trout:[batch_size,num_class,H,W]
    trlb : [batch_size,1,H,W] 信息熵最小的ratio有类别(1,24),其余为0(unlabeled)
    """
    #----------------------------------------------------------------------------------------------------

    # 计算信息熵
    # 计算每个class对应概率图probability
    prob = F.softmax(target, dim=1)
    # 根据所有class的probability 计算信息熵/lg(numclass)
    entp = torch.mul(prob, torch.log2(prob + 1e-30)) # torch.mul逐元素乘法
    entp = torch.div(torch.sum(entp, dim=1), - math.log2(args.numclass)) # torch.div逐元素除法

    # ----------------------------------------------------------------------------------------------------

    # 生成遮罩
    # 使用伪标签元素的比例
    ratio = ((epoch + 1) / args.epochs) * args.factor  # 默认 factor:0.5 , epochs:120
    # 使用伪标签的元素的数量
    num = math.floor(entp.numel() * ratio) # .numel()返回元素总数
    # 去除信息熵最小的元素后的其他元素的索引
    idx = np.argpartition(entp.detach().cpu().numpy().reshape(-1), num)[num:]
    # .reshape(-1)展平为一维数组
    # np.argpartition: 返回索引，第 num 个元素的左侧是最小的 num 个元素，而右侧是剩余的元素，但并不按照顺序排列。

    # ----------------------------------------------------------------------------------------------------

    # 生成伪标签，numclass维度中最大的值对应的索引，作为该元素的分类结果，trlb伪标签
    trlb = torch.max(target, dim=1)[1].reshape(-1)  # torch.max(,1)[1] 返回numclass上最大值的索引

    # ----------------------------------------------------------------------------------------------------

    # 遮罩,信息熵不是最小的分类为unlabeled类
    trlb[idx] = 0
    trlb = trlb.reshape(entp.size())

    return trlb

