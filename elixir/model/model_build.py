# 
#  Created by hwx on 2021/12/15
# 

import torch
from torch import nn

# from model.backbone.mobilenetv2 import *
# from model.backbone.alexnet import AlexNet
from model.backbone.alexnet import AlexNet
from model.backbone.resnet import ResNet, BasicBlock
from collections import OrderedDict


class class_model(nn.Module):
    def __init__(self, backbone, classifier, class_num, loss=None, is_training=True):
        super(class_model, self).__init__()
        self.backbone = backbone
        self.classifier = classifier
        self.is_training = is_training
        self.loss = loss
        self.class_num = class_num
        return;


    def forward(self, data, label=None):
        if self.is_training:
            feature = self.backbone(data[0])
        else:
            feature = self.backbone(data)
        pred = self.classifier(feature)

        if not self.is_training:
            return pred
        else:
            l = self.loss(pred, data[1])
            return l


def class_loss(pred_obj, label_obj, training_mask=None, select_label=None):
    return torch.nn.functional.nll_loss(torch.nn.functional.log_softmax(pred_obj, dim=1), label_obj)


def build(args=None, is_training=False):
    if args is None or args.backbone == 'alexnet':
        backbone = AlexNet(args.class_num)
        classifier = nn.Sequential(
            nn.Dropout(),
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, args.class_num),
        )
    elif args.backbone == 'resnet18':
        backbone = ResNet(BasicBlock, [2, 2, 2, 2], args.class_num)
        classifier = nn.Sequential(
            OrderedDict([
                ('fc', nn.Linear(512 * BasicBlock.expansion, args.class_num))
            ])
        )
    
    m = class_model(backbone, classifier, args.class_num, class_loss, is_training);

    if args.pretrained_model:
        pretrained_dict = torch.load(args.pretrained_model)
        m.backbone.load_state_dict(pretrained_dict, strict=False)

    m.to(args.device)
    return m

if __name__ == '__main__':
    # backbone = mobilenet_v2(used_layers=[1, 2, 3, 4, 5]);
    # m = seg_model(backbone, 4, seg_loss.seg_loss)
    # for p in m.parameters():
    #     print(p.shape)

    backbone = AlexNet(3);
    m = class_model(backbone, 3, class_loss)
    for p in m.parameters():
        print(p.shape)
    print(m)