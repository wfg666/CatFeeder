import cv2, glob, sys, os
import numpy as np
import os.path as osp
import random, math

class Augmentation():
	def __init__(self):
		self.color_range = 10
		self.crop_precent_range = 0.30
		self.lum_range1 = 5
		self.lum_range2 = 10
		self.index = 0
		

	def random_channel(self, image):
		channel_idx = [0, 1, 2]
		random.shuffle(channel_idx)
		image1 = image
		image[:,:,0] = image1[:, :, channel_idx[0]]
		image[:,:,1] = image1[:, :, channel_idx[1]]
		image[:,:,2] = image1[:, :, channel_idx[2]]
		return image


	def add_color_noise(self, image):
		ran_color_range_0 = random.randint(-self.color_range, self.color_range)
		ran_color_range_1 = random.randint(-self.color_range, self.color_range)
		ran_color_range_2 = random.randint(-self.color_range, self.color_range)

		image[:,:,0] += ran_color_range_0
		image[:,:,1] += ran_color_range_1
		image[:,:,2] += ran_color_range_2

		image = self.random_channel(image)

		return image

	def add_lum_noise(self, image, lum_range1=None, lum_range2=None):
		if lum_range2 is None:
			ran_lum_range_0 = 1 - random.randint(-self.lum_range1, self.lum_range1)/100.0
			ran_lum_range_1 = random.randint(-self.lum_range2, self.lum_range2)
		else:
			ran_lum_range_0 = 1 - random.randint(lum_range1, lum_range1)/100.0
			ran_lum_range_1 = random.randint(lum_range2, lum_range2)
		image = self.random_contrast(image, ran_lum_range_0, ran_lum_range_1)
		# ran_lum_range_1 = random.randint(-self.lum_range2, self.lum_range2)
		# image = self.random_contrast(image, 1, ran_lum_range_1)
		return image

	def random_contrast(self, img1, c, b): # 亮度就是每个像素所有通道都加上b
		rows, cols = img1.shape
		blank = np.zeros([rows, cols], img1.dtype) # np.zeros(img1.shape, dtype=ui
		dst = cv2.addWeighted(img1, c, blank, 1-c, b)
		return dst

	def add_GaussianBlur(self, img, blur=(0, 2, 4, 6, 8)):
		min_size = 1
		addition = random.choice(blur)
		size = min_size + addition
		kernel_size = (size, size)
		img = cv2.GaussianBlur(img, kernel_size, 0)
		return img


	def random_erase(self, img, mask=None, padding_ratio=0.1, thr=40):
		if mask is None:
			maxsize = (img.shape[0] * img.shape[1] * padding_ratio) ** 0.5
		else:
			maxsize = (cv2.countNonZero(mask) * padding_ratio) ** 0.5
		if maxsize < 1:
			return img
		size = random.randint(0, int(maxsize))

		y, x = np.where(mask == 255)
		idx = random.randint(0, len(x) - 1)
		x_start = x[idx]
		y_start = y[idx]

		val=[x for x in range(0, thr)] + [x for x in range(255-thr, 255)]
		idx = random.randint(0, len(val) - 1)
		img[y_start:y_start+size, x_start:x_start+size, :] = val[idx]

		# balabala
		return img


	def random_crop(self, image, mask, min_ratio=0.9, max_ratio=1.0):

		h, w = image.shape[:2]
		
		ratio = random.random()
		
		scale = min_ratio + ratio * (max_ratio - min_ratio)
		
		new_h = int(h*scale)    
		new_w = int(w*scale)
		
		y = np.random.randint(0, h - new_h)    
		x = np.random.randint(0, w - new_w)
		
		image = image[y:y+new_h, x:x+new_w]
		if mask is not None:
			mask  = mask[y:y+new_h, x:x+new_w]
	
		return image, mask, x+0.5*image.shape[1], y+0.5*image.shape[0]


	# def fliplr(self, img):
	#     '''flip horizontal'''
	#     # img_flip = tf.image.flip_left_right(img)
	#     img_flip = cv2.flip(image,1)
	#     return img_flip

	# def fliptb(self, img):
	#     '''flip horizontal'''
	#     # img_flip = tf.image.flip_up_down(img)
	#     img_flip = cv2.flip(image,0)
	#     return img_flip