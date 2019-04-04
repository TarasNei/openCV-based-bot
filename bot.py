import cv2
import numpy as np

from functions import *
from lib.InterceptionWrapper import InterceptionMouseState, InterceptionMouseStroke


class Bot:
	TARGET_BAR = 'img/target_bar.png'
	TARGET_BAR_HF5 = 'img/hf5target_bar_RBG_2.png'

	TARGET_BAR_DEFAULT_WIDTH = 188
	TARGET_BAR_HEIGHT = 50

	HP_COLOR = [111, 23, 19]
	HP_COLOR_VARIATION = [111, 23, 20]

	def __init__(self, autohot_py):
		self.autohot_py = autohot_py
		self.window_info = get_window_info()

		self.useless_steps = 0
		self.step = 0

	def exitAutoHotKey(self):
		self.autohot_py.stop()

	def get_targeted_hp(self):
		# hp_color = [111, 23, 20]
		target_bar_coordinates = {}
		filled_red_pixels = 1

		img = get_screen(
			self.window_info["x"],
			self.window_info["y"],
			self.window_info["x"] + self.window_info["width"],
			self.window_info["y"] + self.window_info["height"] - 190
		)

		img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		# cv2.imwrite('grey.png', img_gray)
		template = cv2.imread(self.TARGET_BAR_HF5, 0)
		# w, h = template.shape[::-1]
		res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

		threshold = 0.8
		loc = np.where(res >= threshold)
		if np.count_nonzero(loc) == 2:
			for pt in zip(*loc[::-1]):
				target_bar_coordinates = {"x": pt[0], "y": pt[1]}
		# cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 2)
		# cv2.imwrite('res.png', img)

		if not target_bar_coordinates:
			return -1

		pil_image_hp = get_screen(
			self.window_info["x"] + target_bar_coordinates['x'] + 19,  # fuckin calculations todo
			self.window_info["y"] + target_bar_coordinates['y'] + 28,
			self.window_info["x"] + target_bar_coordinates['x'] + 187,
			self.window_info["y"] + target_bar_coordinates['y'] + 59
		)

		pixels = pil_image_hp[0].tolist()
		for pixel in pixels:
			if pixel == self.HP_COLOR or pixel == self.HP_COLOR_VARIATION:
				filled_red_pixels += 1

		percent = 100 * filled_red_pixels / 150
		return percent

	def set_target(self):
		"""
		find target and click
		"""
		img = get_screen(
			self.window_info["x"],
			self.window_info["y"],
			self.window_info["x"] + self.window_info["width"],
			self.window_info["y"] + self.window_info["height"] - 300
		)

		cnts = self.get_target_centers(img)

		approxes = []
		hulls = []
		for cnt in cnts:
			approxes.append(cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True))
			hulls.append(cv2.convexHull(cnt))

			left = list(cnt[cnt[:, :, 0].argmin()][0])
			right = list(cnt[cnt[:, :, 0].argmax()][0])
			if right[0] - left[0] < 20:
				continue
			center = round((right[0] + left[0]) / 2)
			center = int(center)
			# smooth_move(self.autohot_py, center + self.window_info["x"], left[1] + 110 + self.window_info["y"])
			# time.sleep(0.1)
			# if self.find_from_targeted(left, right):
			#     self.click_target()
			#     return True

			# Slide mouse down to find target

			iterator = 50
			while iterator < 150:
				time.sleep(0.3)
				self.autohot_py.F1
				smooth_move(
					self.autohot_py,
					center + self.window_info["x"],
					left[1] + iterator + self.window_info["y"]
				)
			# if self.find_from_targeted(left, right):
			# 	self.click_target()
			# 	return True
			# iterator += 30

		return False

	def get_target_centers(self, img):

		# Hide buff line
		# img[0:70, 0:500] = (0, 0, 0)

		# Hide your name in first camera position (default)
		# img[210:230, 350:440] = (0, 0, 0)

		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		# temp = Image.fromarray(gray)
		# temp.show()
		cv2.imwrite('1_gray_img.png', gray)

		# Find only white text
		ret, threshold1 = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
		cv2.imwrite('2_threshold1_img.png', threshold1)

		# Morphological transformation
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 5))
		closed = cv2.morphologyEx(threshold1, cv2.MORPH_CLOSE, kernel)
		cv2.imwrite('3_morphologyEx_img.png', closed)
		closed = cv2.erode(closed, kernel, iterations=1)
		cv2.imwrite('4_erode_img.png', closed)
		closed = cv2.dilate(closed, kernel, iterations=1)
		cv2.imwrite('5_dilate_img.png', closed)

		(centers, hierarchy) = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		return centers
