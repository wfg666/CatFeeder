# 
#  Created by hwx on 2021/12/15
# 
from torch.utils.data import Dataset
from dataset.augmentation import Augmentation
import torch

import cv2, glob, os
import numpy as np
import os.path as osp

class data_reader(Dataset):
	def __init__(self, image_path=None, patch_size_W=None, patch_size_H=None, ):
		super(data_reader, self).__init__()
		self.image_path = image_path
		self.img_W= 224
		self.img_H = 224
		if patch_size_W:
			self.img_W = patch_size_W
		if patch_size_H:
			self.img_H = patch_size_H

		self.outter_ratio = 0.8

		folder = glob.glob(osp.join(self.image_path, '*'))
		folder.sort()
		print(folder)
		self.imageList = []
		self.labelList = []
		for i, f in enumerate(folder):
			self.imageList = self.imageList + glob.glob(osp.join(f, '*.jpg')) + glob.glob(osp.join(f, '*.png')) + glob.glob(osp.join(f, '*.bmp')) + glob.glob(osp.join(f, '*.jpeg'))
			self.labelList = self.labelList + [i for x in range(len((glob.glob(osp.join(f, '*.jpg')) + glob.glob(osp.join(f, '*.png')) + glob.glob(osp.join(f, '*.bmp')) + glob.glob(osp.join(f, '*.jpeg')))))]
		
		np.random.seed(10)
		np.random.shuffle(self.imageList)
		np.random.seed(10)
		np.random.shuffle(self.labelList)
		
		self.length = len(self.imageList)

		self.Augmentation = Augmentation()

	def __len__(self):
		return self.length

	def __getitem__(self, index):
		image_idx = index % self.length
		label = self.labelList[image_idx]

		image_name = self.imageList[image_idx]

		img = cv2.imread(image_name).astype(np.float32)
		# data enhancement
		# crop
		# img, mask, _, _ = self.Augmentation.random_crop(img, mask)
		# resize
		img =  cv2.resize(img,  (self.img_W, self.img_H))

		# pixel
		# img = self.add_lum_noise(img)
		img = self.Augmentation.add_GaussianBlur(img, (0, 2))
		img = self.Augmentation.add_color_noise(img)

		vis = False
		if vis:
			cv2.imwrite('vis/img{}.jpg'.format(index), img)

		img = np.ascontiguousarray(img[..., ::-1])
		img = img.transpose(2, 0, 1)
		img /= 255.0
		im_as_ten = torch.from_numpy(img).float()
		return im_as_ten, label
	

if __name__ == '__main__':
	os.environ["CUDA_VISIBLE_DEVICES"] = "1"
	data_gen = data_reader('/data/catFeeder/data')
	# data_gen.__getitem__(0)

	dataloader = torch.utils.data.DataLoader(data_gen, batch_size=64, shuffle=True, num_workers=1)
	# # print(len(dataloader))
	# # for epoch in range(1):
	# # 	print(data_gen[0][0][0, 0, 0])
	# 	# for samples, targets in dataloader:
	# 		# if epoch >= 0:
	# 		# 	print('----------------------------------------')
	# 		# 	break
	# 		# print(samples.shape)
	# 		# print(targets.shape)
	for i_batch, batch_data in enumerate(dataloader):
		print(i_batch)#打印batch编号
		print(batch_data[0].shape)#打印该batch里面图片的大小
		print(batch_data[1].shape)#打印该batch里面图片的标签
