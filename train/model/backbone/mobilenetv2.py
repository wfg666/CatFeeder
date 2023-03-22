# 
#  Created by hwx on 2021/12/15
# 

import warnings
from typing import Callable, Any, Optional, List

import torch
from torch import Tensor
from torch import nn

def conv_bn(inp, oup, stride, padding=1):
    return nn.Sequential(
        nn.Conv2d(inp, oup, 3, stride, padding, bias=False),
        nn.BatchNorm2d(oup),
        nn.ReLU6(inplace=True)
    )


def conv_1x1_bn(inp, oup):
    return nn.Sequential(
        nn.Conv2d(inp, oup, 1, 1, 0, bias=False),
        nn.BatchNorm2d(oup),
        nn.ReLU6(inplace=True)
    )

class InvertedResidual(nn.Module):
    def __init__(self, inp, oup, stride, expand_ratio, dilation=1):
        super(InvertedResidual, self).__init__()
        self.stride = stride

        self.use_res_connect = self.stride == 1 and inp == oup

        padding = 2 - stride
        if dilation > 1:
            padding = dilation

        if(expand_ratio!=1):
            self.conv = nn.Sequential(
                # pw
                nn.Conv2d(in_channels=inp, out_channels=inp * expand_ratio, kernel_size=1, stride=1, padding=0, bias=False),
                nn.BatchNorm2d(inp * expand_ratio),
                nn.ReLU6(inplace=True),
                # dw
                nn.Conv2d(in_channels=inp * expand_ratio, out_channels=inp * expand_ratio, kernel_size=3,
                          stride=stride, padding=padding, dilation=dilation,
                          groups=inp * expand_ratio, bias=False),
                nn.BatchNorm2d(inp * expand_ratio),
                nn.ReLU6(inplace=True),
                # pw-linear
                nn.Conv2d(in_channels=inp*expand_ratio, out_channels=oup, kernel_size=1,  stride=1, padding=0, bias=False),
                nn.BatchNorm2d(oup),
            )
        else:
            self.conv = nn.Sequential(
                # pw
                nn.Conv2d(in_channels=inp * expand_ratio, out_channels=inp * expand_ratio, kernel_size=3,
                          stride=stride, padding=padding, dilation=dilation,
                          groups=inp * expand_ratio, bias=False),
                nn.BatchNorm2d(inp * expand_ratio),
                nn.ReLU6(inplace=True),
                # pw-linear
                nn.Conv2d(in_channels=inp*expand_ratio, out_channels=oup, kernel_size=1,  stride=1, padding=0, bias=False),
                nn.BatchNorm2d(oup),
            )

    def forward(self, x):
        if self.use_res_connect:
            return x + self.conv(x)
        else:
            return self.conv(x)

class MobileNetV2(nn.Module):
    def __init__(self, width_mult = 1.0, inverted_residual_setting = None, block = None, norm_layer = None, dropout = 0.2, used_layers=[4, 5, 6, 7]):
        """
        MobileNet V2 main class

        Args:
            width_mult (float): Width multiplier - adjusts number of channels in each layer by this amount
            inverted_residual_setting: Network structure
            round_nearest (int): Round the number of channels in each layer to be a multiple of this number
            Set to 1 to turn off rounding
            block: Module specifying inverted residual building block for mobilenet
            norm_layer: Module specifying the normalization layer to use
            dropout (float): The droupout probability

        """
        super().__init__()
        # _log_api_usage_once("models", self.__class__.__name__)


        if block is None:
            block = InvertedResidual

        if norm_layer is None:
            norm_layer = nn.BatchNorm2d

        input_channel = 32
        last_channel = 1280

        if inverted_residual_setting is None:
            inverted_residual_setting = [
                # t, c, n, s
                [1, 16, 1, 1],
                [6, 24, 2, 2],
                [6, 32, 3, 2],
                [6, 64, 4, 2],
                [6, 96, 3, 1],
                [6, 160, 3, 2],
                [6, 320, 1, 1],
            ]

        # only check the first element, assuming user knows t,c,n,s are required
        if len(inverted_residual_setting) == 0 or len(inverted_residual_setting[0]) != 4:
            raise ValueError(
                f"inverted_residual_setting should be non-empty or a 4-element list, got {inverted_residual_setting}"
            )

        self.used_layers = used_layers
        self.channel_num = [inverted_residual_setting[i-1][1] for i in used_layers]

        # building first layer
        self.add_module('layer0', conv_bn(3, input_channel, stride=2, padding=1))
        # building inverted residual blocks
        for idx, (t, c, n, s) in enumerate(inverted_residual_setting):
            output_channel = int(c * width_mult)

            layers = []

            for i in range(n):
                stride = s if i == 0 else 1
                layers.append(block(input_channel, output_channel, stride, expand_ratio=t))
                input_channel = output_channel

            self.add_module('layer%d' % (idx+1), nn.Sequential(*layers))
        # building last several layers
        # features.append(
        #     ConvNormActivation(
        #         input_channel, self.last_channel, kernel_size=1, norm_layer=norm_layer, activation_layer=nn.ReLU6
        #     )
        # )
        # make it nn.Sequential
        # self.features = nn.Sequential(*features)

        # weight initialization
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.zeros_(m.bias)

    def _forward_impl(self, x):
        outputs = []
        for idx in range(8):
            name = "layer%d" % idx
            x = getattr(self, name)(x)
            outputs.append(x)
        # p0, p1, p2, p3, p4 = [outputs[i] for i in [1, 2, 3, 5, 7]]
        out = [outputs[i] for i in self.used_layers]
        if len(out) == 1:
            return out[0]
        return out

    def forward(self, x: Tensor):
        return self._forward_impl(x)

def load_from_torch_model(pretrained_dict):
    new_pretrained_dict = {}

    dst_setting = [[3], [5], [8, 8], [8, 8, 8], [8, 8, 8, 8], [8, 8, 8], [8, 8, 8], [8]]

    length = 0
    for idx, layer_info in enumerate(dst_setting):
        if idx == 0:
            new_pretrained_dict['backbone.layer{}.0.weight'.format(idx)] = pretrained_dict['features.0.0.weight']
            new_pretrained_dict['backbone.layer{}.1.weight'.format(idx)] = pretrained_dict['features.0.1.weight']
            new_pretrained_dict['backbone.layer{}.1.bias'.format(idx)]   = pretrained_dict['features.0.1.bias']
            new_pretrained_dict['backbone.layer{}.1.running_mean'.format(idx)] = pretrained_dict['features.0.1.running_mean']
            new_pretrained_dict['backbone.layer{}.1.running_var'.format(idx)] = pretrained_dict['features.0.1.running_var']
            new_pretrained_dict['backbone.layer{}.1.num_batches_tracked'.format(idx)] = pretrained_dict['features.0.1.num_batches_tracked']
            length+=1
        elif idx == 1:
            for i in range(layer_info[0]):
                if i == 0 or i == 3:
                    if i == 0:
                        key = '0.0'
                    elif i == 3:
                        key = '1'
                    new_pretrained_dict['backbone.layer{}.0.conv.{}.weight'.format(idx, i)] = pretrained_dict['features.{}.conv.{}.weight'.format(idx, key)]
                elif i == 1 or i == 4:
                    if i == 1:
                        key = '0.1'
                    elif i == 4:
                        key = '2'
                    new_pretrained_dict['backbone.layer{}.0.conv.{}.weight'.format(idx, i)] = pretrained_dict['features.{}.conv.{}.weight'.format(length, key)]
                    new_pretrained_dict['backbone.layer{}.0.conv.{}.bias'.format(idx, i)]   = pretrained_dict['features.{}.conv.{}.bias'.format(length, key)]
                    new_pretrained_dict['backbone.layer{}.0.conv.{}.running_mean'.format(idx, i)] = pretrained_dict['features.{}.conv.{}.running_mean'.format(length, key)]
                    new_pretrained_dict['backbone.layer{}.0.conv.{}.running_var'.format(idx, i)] = pretrained_dict['features.{}.conv.{}.running_var'.format(length, key)]
                    new_pretrained_dict['backbone.layer{}.0.conv.{}.num_batches_tracked'.format(idx, i)] = pretrained_dict['features.{}.conv.{}.num_batches_tracked'.format(length, key)]
            length+=1
        else:
            for idx2, n in enumerate(layer_info):
                for i in range(n):
                    if i == 0 or i == 3 or i == 6:
                        if i == 0:
                            key = '0.0'
                        elif i == 3:
                            key = '1.0'
                        elif i == 6:
                            key = '2'
                        new_pretrained_dict['backbone.layer{}.{}.conv.{}.weight'.format(idx, idx2, i)] = pretrained_dict['features.{}.conv.{}.weight'.format(length, key)]
                    elif i == 1 or i == 4 or i == 7:
                        if i == 1:
                            key = '0.1'
                        elif i == 4:
                            key = '1.1'
                        elif i == 7:
                            key = '3'
                        new_pretrained_dict['backbone.layer{}.{}.conv.{}.weight'.format(idx, idx2, i)] = pretrained_dict['features.{}.conv.{}.weight'.format(length, key)]
                        new_pretrained_dict['backbone.layer{}.{}.conv.{}.bias'.format(idx, idx2, i)]   = pretrained_dict['features.{}.conv.{}.bias'.format(length, key)]
                        new_pretrained_dict['backbone.layer{}.{}.conv.{}.running_mean'.format(idx, idx2, i)] = pretrained_dict['features.{}.conv.{}.running_mean'.format(length, key)]
                        new_pretrained_dict['backbone.layer{}.{}.conv.{}.running_var'.format(idx, idx2, i)] = pretrained_dict['features.{}.conv.{}.running_var'.format(length, key)]
                        new_pretrained_dict['backbone.layer{}.{}.conv.{}.num_batches_tracked'.format(idx, idx2, i)] = pretrained_dict['features.{}.conv.{}.num_batches_tracked'.format(length, key)]
                length+=1
    return new_pretrained_dict


def mobilenet_v2(pretrained_model=None, convert_torch_model=False, used_layers=[4,5,6,7]):
    device = torch.cuda.current_device()
    """
    Constructs a MobileNetV2 architecture from
    `"MobileNetV2: Inverted Residuals and Linear Bottlenecks" <https://arxiv.org/abs/1801.04381>`_.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    model = MobileNetV2(used_layers=used_layers)
    # print(model)

    if pretrained_model:
        print("load pretrained mode from {}".format(pretrained_model))
        pretrained_dict = torch.load(pretrained_model, map_location=lambda storage, loc: storage.cuda(device))
        if convert_torch_model:
            pretrained_dict = load_from_torch_model(pretrained_dict)
        model.load_state_dict(pretrained_dict, strict=True)
        # print(pretrained_dict.keys())
        if convert_torch_model:
            torch.save(pretrained_dict, 'model.pth')
    return model




if __name__ == '__main__':
    # pretrained_model = "../../pretrain/mobilenetv2.pth"
    pretrained_model = "pretrain/mobilenet_v2-b0353104.pth"
    # pretrained_model = None
    net = mobilenet_v2(pretrained_model, True)
    print(net)
    # print(net.channel_num)
    # print(net)