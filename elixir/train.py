# 
#  Created by hwx on 2021/12/16
# 

import argparse

import os
import os.path as osp
import time

import torch
from torch.utils.data import DataLoader
import datetime

from model import model_build
from dataset import data_reader
from utils import logger

ts = time.strftime("%Y%m%d_%H%M", time.localtime())
os.makedirs('./output/log/', exist_ok=True)
logger = logger.get_logger(filename='./output/log/train_{}.log'.format(ts))


def get_args_parser():
    parser = argparse.ArgumentParser('cat classification', add_help=False)
    parser.add_argument('--class_num', default=3, type=int)
    parser.add_argument('--optimizer', default='Adam', type=str, help='optimizer for training')
    parser.add_argument('--base_lr', default=1e-3, type=float)
    parser.add_argument('--momentum', default=0.9, type=float)
    parser.add_argument('--batch_size', default=64, type=int)
    parser.add_argument('--weight_decay', default=1e-4, type=float)
    parser.add_argument('--epochs', default=500, type=int)
    parser.add_argument('--lr_drop', default=200, type=int)
    parser.add_argument('--num_workers', default=4, type=int)
    parser.add_argument('--start_epoch', default=0, type=int)
    parser.add_argument('--clip_max_norm', default=0.1, type=float, help='gradient clipping max norm')
    parser.add_argument('--backbone', default='resnet18', type=str)
    parser.add_argument('--device', default='cuda', type=str, help='device to use for training')
    parser.add_argument('--resume', default='', type=str, help='resume model path')
    parser.add_argument('--output_dir', default='output', type=str, help='path where to save, empty for no saving')
    parser.add_argument('--gpu_list', default='1', type=str, help='gpu list for using')
    parser.add_argument('--pretrained_model', default='pretrain/resnet18-5c106cde.pth', type=str)
    parser.add_argument('--data_path', default='../data/train', type=str, help='path for training data')
    return parser


def build_data_loader(args):
    logger.info("build train dataset")
    train_dataset = data_reader.data_reader(args.data_path)
    logger.info("build dataset done")

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, num_workers=1, shuffle=True)
    return train_loader


def train_one_epoch(model, data_loader, lr_scheduler, optimizer,
                    device, epoch, max_norm = 0):
    for idx, (samples, targets) in enumerate(data_loader):
        samples = samples.to(device)
        targets = targets.to(device)

        losses = model([samples, targets])

        optimizer.zero_grad()
        losses.backward()
        if max_norm > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
        optimizer.step()
        if idx % 100 == 0:
            info = "Epoch: [{}][{}/{}] loss: {:.4f} lr: {:.6f}".format(
                                epoch+1, (idx+1) % len(data_loader),
                                len(data_loader), losses, optimizer.state_dict()['param_groups'][0]['lr'])
            logger.info(info)
    return


def main(args):
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_list

    device = torch.device(args.device)
    logger.info(device)

    # create data loader
    train_loader = build_data_loader(args)

    # build model
    model = model_build.build(args, True)

    # optimizer and lr_scheduler
    if args.optimizer == 'SGD':
        optimizer = torch.optim.SGD(model.parameters(),
                                    lr=args.base_lr,
                                    momentum=args.momentum,
                                    weight_decay=args.weight_decay)
    elif args.optimizer == 'Adam':
        optimizer = torch.optim.Adam(model.parameters(),
                                    lr=args.base_lr,
                                    weight_decay=args.weight_decay)
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, args.lr_drop, gamma=0.1)

    # resume
    if args.resume:
        print('resume from {}'.format(args.resume))
        checkpoint = torch.load(args.resume, map_location='cpu')
        model.load_state_dict(checkpoint['model'])
        if 'optimizer' in checkpoint and 'lr_scheduler' in checkpoint and 'epoch' in checkpoint:
            optimizer.load_state_dict(checkpoint['optimizer'])
            lr_scheduler.load_state_dict(checkpoint['lr_scheduler'])
            args.start_epoch = checkpoint['epoch'] + 1

    # start training
    start_time = time.time()
    for epoch in range(args.start_epoch, args.epochs):
        train_one_epoch(model, train_loader, lr_scheduler, optimizer, device, epoch, args.clip_max_norm)
        lr_scheduler.step()
        if args.output_dir:
            if not os.path.isdir(args.output_dir):
                os.system('mkdir {}'.format(args.output_dir))
            if not os.path.isdir(osp.join(args.output_dir, ts)):
                os.system('mkdir {}/{}'.format(args.output_dir, ts))
            if (epoch + 1) % 20 == 0:
                checkpoint_path = osp.join(args.output_dir, ts, 'checkpoint{}.pth'.format('%05d'%epoch))
                torch.save({
                    'model': model.state_dict(),
                    'optimizer': optimizer.state_dict(),
                    'lr_scheduler': lr_scheduler.state_dict(),
                    'epoch': epoch,
                    'args': args,
                }, checkpoint_path)

    total_time = time.time() - start_time
    total_time_str = str(datetime.timedelta(seconds=int(total_time)))
    logger.info('Training time {}'.format(total_time_str))


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Cat feeder training script', parents=[get_args_parser()])
    args = parser.parse_args()
    print(args)

    main(args)