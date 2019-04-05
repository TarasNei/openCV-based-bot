import cv2
import random
import numpy as np

from functions import *
from lib.InterceptionWrapper import InterceptionMouseState, InterceptionMouseStroke


class Bot:
	TARGET_NAME_PATTERN = (30, 5)

	TARGET_BAR = 'img/target_bar.png'
	TARGET_BAR_HF5 = 'img/hf5target_bar_RBG_2.png'

	TARGET_SELECT_TEMPLATE = 'img/template_target_hf5_2.png'

	TARGET_BAR_DEFAULT_WIDTH = 188
	TARGET_BAR_HEIGHT = 50

	HP_COLOR = [111, 23, 19]
	HP_COLOR_VARIATION = [111, 23, 20]

	MOB_Y_AXIS_CENTRING_FAULT = 50

	def __init__(self, autohot_py):
		self.autohot_py = autohot_py
		self.window_info = get_window_info()
		self.useless_steps = 0


	def exitAutoHotKey(self):
		self.autohot_py.stop()

	def get_targeted_hp(self):
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
			if (pixel == self.HP_COLOR) or (pixel == self.HP_COLOR_VARIATION):
				filled_red_pixels += 1

		percent = int(100 * filled_red_pixels / 150)
		return percent

	def set_target(self):
		img = get_screen(
			self.window_info["x"],
			self.window_info["y"],
			self.window_info["x"] + self.window_info["width"],
			self.window_info["y"] + self.window_info["height"] - 300
		)

		# temp = Image.fromarray(img, "RGB")
		# temp.show()

		cnts = self.get_target_centers(img)

		approxes = []
		hulls = []
		for cnt in cnts:
			# approxes.append(cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True))
			# hulls.append(cv2.convexHull(cnt))

			left = list(cnt[cnt[:, :, 0].argmin()][0])
			right = list(cnt[cnt[:, :, 0].argmax()][0])
			if right[0] - left[0] < 20:
				continue
			center = round((right[0] + left[0]) / 2)
			center = int(center)

			if not center:
				return False
			# smooth_move(self.autohot_py, center + self.window_info["x"], left[1] + 110 + self.window_info["y"])
			# time.sleep(0.1)

			# Slide mouse down to find target
			x = int((center + self.window_info["x"]) / 2)                 # maybe cuz dual monitors
			y = left[1] + self.window_info["y"] + self.MOB_Y_AXIS_CENTRING_FAULT

			self.autohot_py.moveMouseToPosition(x, y)

			if self.find_from_targeted(left, right):
				self.click_target()
				return True

			self.click_target()

			# iterator = 50
			# while iterator < 150:
			# 	time.sleep(0.3)
			#
				# if self.find_from_targeted(left, right):
				# 	return True
			# 	iterator += 30

		return False

	def get_target_centers(self, img):

		# Hide buff line
		# img[0:70, 0:500] = (0, 0, 0)

		# Hide your name in first camera position (default)
		# img[210:230, 350:440] = (0, 0, 0)

		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		temp = Image.fromarray(gray)
		# temp.show()
		# cv2.imwrite('1_gray_img.png', gray)

		# Find only white text
		ret, threshold1 = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
		# cv2.imwrite('2_threshold1_img.png', threshold1)

		# Morphological transformation
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, self.TARGET_NAME_PATTERN)
		closed = cv2.morphologyEx(threshold1, cv2.MORPH_CLOSE, kernel)
		# cv2.imwrite('3_morphologyEx_img.png', closed)
		closed = cv2.erode(closed, kernel, iterations=1)
		# cv2.imwrite('4_erode_img.png', closed)
		closed = cv2.dilate(closed, kernel, iterations=1)
		# cv2.imwrite('5_dilate_img.png', closed)

		(centers, hierarchy) = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		return centers

	def find_from_targeted(self, left, right):
		time.sleep(0.5)
		template = cv2.imread(self.TARGET_SELECT_TEMPLATE, 0)
		w, h = template.shape[::-1]

		screen_shot = get_screen(
			self.window_info["x"],
			self.window_info["y"],
			self.window_info["x"] + self.window_info["width"],
			self.window_info["y"] + self.window_info["height"] - 300
		)
		screen_shot_gray = cv2.cvtColor(screen_shot, cv2.COLOR_BGR2GRAY)
		res = cv2.matchTemplate(screen_shot_gray, template, cv2.TM_CCOEFF_NORMED)

		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

		top_left = max_loc
		bottom_right = (top_left[0] + w, top_left[1] + h)

		cv2.rectangle(screen_shot_gray, top_left, bottom_right, 255, 2)

		target_bar_coordinates = {}
		threshold = 0.4
		loc = np.where(res >= threshold)
		# if np.count_nonzero(loc) == 2: whats for?
		for pt in zip(*loc[::-1]):
			target_bar_coordinates = {"x": pt[0], "y": pt[1]}
		# cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 2)
		# cv2.imwrite('res.png', img)

		cv2.imwrite('res.png', screen_shot_gray)
		if not target_bar_coordinates:
			return -1

		# print template.shape
		# roi = get_screen(
		# 	self.window_info["x"],
		# 	self.window_info["y"],
		# 	self.window_info["x"] + self.window_info["width"],
		# 	self.window_info["y"] + self.window_info["height"] - 300
		# )
		#
		# roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
		# cv2.imwrite('roi.png', roi)
		# ret, th1 = cv2.threshold(roi, 224, 255, cv2.THRESH_TOZERO_INV)
		# ret, th2 = cv2.threshold(th1, 135, 255, cv2.THRESH_BINARY)
		# ret, tp1 = cv2.threshold(template, 224, 255, cv2.THRESH_TOZERO_INV)
		# ret, tp2 = cv2.threshold(tp1, 135, 255, cv2.THRESH_BINARY)
		# if not hasattr(th2, 'shape'):
		# 	return False
		# wth, hth = th2.shape
		# wtp, htp = tp2.shape
		# if wth > wtp and hth > htp:
		# 	res = cv2.matchTemplate(th2, tp2, cv2.TM_CCORR_NORMED)
		# 	if res.any():
		# 		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
		# 		if max_val > 0.7:
		# 			return True
		# 		else:
		# 			return False
		# return False

	def click_target(self):
		stroke = InterceptionMouseStroke()
		stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
		self.autohot_py.sendToDefaultMouse(stroke)
		time.sleep(0.02)
		stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
		self.autohot_py.sendToDefaultMouse(stroke)

	def go_somewhere(self):

		self.set_default_camera()
		if random.choice([True, False]):
			self.autohot_py.moveMouseToPosition(900, 650)  # @TODO dynamic
		else:
			self.autohot_py.moveMouseToPosition(100, 650)  # @TODO dynamic

		time.sleep(0.1)
		for i in range(2):
			stroke = InterceptionMouseStroke()
			stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
			self.autohot_py.sendToDefaultMouse(stroke)
			time.sleep(0.2)
			stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
			self.autohot_py.sendToDefaultMouse(stroke)
		# time.sleep(1)
		# self.set_default_camera()

	def set_default_camera(self):
		self.autohot_py.PAGE_DOWN.press()
		time.sleep(0.1)
		self.autohot_py.PAGE_DOWN.press()
		time.sleep(0.1)
		self.autohot_py.PAGE_DOWN.press()
		time.sleep(0.1)

	def turn(self):
		# turn right
		time.sleep(0.02)
		stroke = InterceptionMouseStroke()

		self.autohot_py.moveMouseToPosition(350, 500)
		stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN
		self.autohot_py.sendToDefaultMouse(stroke)
		time.sleep(0.2)
		self.autohot_py.moveMouseToPosition(700, 500)
		stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
		self.autohot_py.sendToDefaultMouse(stroke)

