import cv2
import random
import numpy as np
import imutils

from functions import *
from lib.InterceptionWrapper import InterceptionMouseState, InterceptionMouseStroke


class Bot:

	TARGET_MIN_NAME_SIZE = (40, 5)
	TARGET_LONG_NAME_FAULT = 5 # todo dynamic

	TARGET_BAR_HF5 = 'img/hf5target_bar_RBG.png'

	TARGET_BAR_DEFAULT_WIDTH = 188
	TARGET_BAR_HEIGHT = 50

	HP_COLOR = [111, 23, 19]
	HP_COLOR_VARIATION = [111, 23, 20]

	MOVE_MOUSE_DOWN = 50

	CUT_SCREEN_TOP = 50
	CUT_SCREEN_BOTTOM = 350
	CUT_SCREEN_BOTTOM_TARGET_BAR = 900

	# to find hp string on the target bar
	LENGTH_FROM_RIGHT_BORDER = 20
	LENGTH_FROM_TOP_BORDER = 28
	LENGTH_OF_HP_STRING = 187
	LENGTH_OF_HP_BOTTOM_BORDER = 59

	CHARACTER_HEIGHT = 220
	CHARACTER_WIDTH = 100


	def __init__(self, autohot_py):
		self.autohot_py = autohot_py
		self.window_info = get_window_info()
		self.useless_steps = 0


	def get_targeted_hp(self):
		target_bar_coordinates = {}
		filled_red_pixels = 1

		img = get_screen(
			self.window_info["x"],
			self.window_info["y"],
			self.window_info["x"] + self.window_info["width"],
			self.window_info["y"] + self.window_info["height"] - self.CUT_SCREEN_BOTTOM_TARGET_BAR
		)

		img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		# cv2.imwrite('grey.png', img_gray)
		template = cv2.imread(self.TARGET_BAR_HF5, 0)
		# cv2.imwrite('templateTargetBar.png', template)
		w, h = template.shape[::-1]
		res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

		threshold = 0.8
		loc = np.where(res >= threshold)
		if np.count_nonzero(loc) == 2:
			for pt in zip(*loc[::-1]):
				target_bar_coordinates = {"x": pt[0], "y": pt[1]}
				cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 2)
		# cv2.imwrite('target_bar.png', img)

		if not target_bar_coordinates:
			return -1

		pil_image_hp = get_screen(
			self.window_info["x"] + target_bar_coordinates['x'] + self.LENGTH_FROM_RIGHT_BORDER,
			self.window_info["y"] + target_bar_coordinates['y'] + self.LENGTH_FROM_TOP_BORDER,
			self.window_info["x"] + target_bar_coordinates['x'] + self.LENGTH_OF_HP_STRING,
			self.window_info["y"] + target_bar_coordinates['y'] + self.LENGTH_OF_HP_BOTTOM_BORDER
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
			self.window_info["y"] + self.CUT_SCREEN_TOP,
			self.window_info["x"] + self.window_info["width"],
			self.window_info["y"] + self.window_info["height"] - self.CUT_SCREEN_BOTTOM
		)

		# temp = Image.fromarray(img, "RGB")
		# temp.show()

		try:
			rawCenter = self.get_target_centers(img)[0]
		except IndexError:
			return False

		left = list(rawCenter[rawCenter[:, :, 0].argmin()][0])
		right = list(rawCenter[rawCenter[:, :, 0].argmax()][0])

		if right[0] - left[0] < 20:
			return False

		center = round((right[0] + left[0]) / 2)
		center = int(center)

		if not center:
			return False

		# Slide mouse down to find target
		x = int((center + self.window_info["x"]) / 2) + self.TARGET_LONG_NAME_FAULT   # maybe cuz dual monitors
		y = left[1] + self.window_info["y"] + self.MOVE_MOUSE_DOWN + self.CUT_SCREEN_TOP

		self.autohot_py.moveMouseToPosition(x, y)
		self.click_target()

		return True


	def get_target_centers(self, img):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		# temp = Image.fromarray(gray)
		# temp.show()
		# cv2.imwrite('1_gray_img.png', gray)

		# Find only white text
		ret, threshold1 = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)
		# cv2.imwrite('2_threshold1_img.png', threshold1)

		# Morphological transformation
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, self.TARGET_MIN_NAME_SIZE)
		closed = cv2.morphologyEx(threshold1, cv2.MORPH_CLOSE, kernel)
		# cv2.imwrite('3_morphologyEx_img.png', closed)
		closed = cv2.erode(closed, kernel, iterations=1)
		# cv2.imwrite('4_erode_img.png', closed)
		closed = cv2.dilate(closed, kernel, iterations=1)
		# cv2.imwrite('5_dilate_img.png', closed)

		(centers, hierarchy) = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		return centers


	def click_target(self):
		stroke = InterceptionMouseStroke()
		stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
		self.autohot_py.sendToDefaultMouse(stroke)
		# time.sleep(0.02)
		stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
		self.autohot_py.sendToDefaultMouse(stroke)

	def go_somewhere(self):
		# self.set_default_camera()

		self.autohot_py.moveMouseToPosition(900, 800)  # @TODO dynamic
		time.sleep(0.1)

		for i in range(2):
			stroke = InterceptionMouseStroke()
			stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
			self.autohot_py.sendToDefaultMouse(stroke)
			time.sleep(0.2)
			stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
			self.autohot_py.sendToDefaultMouse(stroke)


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
		self.autohot_py.moveMouseToPosition(500, 500)
		stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
		self.autohot_py.sendToDefaultMouse(stroke)

	def isStacked(self):
		# self.set_default_camera()
		# time.sleep(0.5)

		x1 = self.window_info["width"] / 2 - self.CHARACTER_WIDTH / 2
		y1 = self.window_info["height"] / 2 - self.CHARACTER_HEIGHT / 2
		x2 = self.window_info["width"] / 2 + self.CHARACTER_WIDTH / 2
		y2 = self.window_info["height"] / 2 + self.CHARACTER_HEIGHT / 2

		firstFrame = get_screen(x1, y1, x2, y2)
		firstFrame = cv2.cvtColor(firstFrame, cv2.COLOR_BGR2GRAY)
		time.sleep(0.8)
		secondFrame = get_screen(x1, y1, x2, y2)
		secondFrame = cv2.cvtColor(secondFrame, cv2.COLOR_BGR2GRAY)

		res = cv2.matchTemplate(firstFrame, secondFrame, cv2.TM_CCOEFF_NORMED)
		threshold = 0.95
		loc = np.where(res >= threshold)

		for pt in zip(*loc[::-1]):
			return True
		return False

	def isDropStillLeft(self):
		template = cv2.imread('img/gold2.png', 0)
		w, h = template.shape[::-1]

		img = get_screen(
			self.window_info["width"] / 2 - self.CHARACTER_WIDTH - 100,
			self.window_info["height"] / 2 - self.CHARACTER_HEIGHT,
			self.window_info["width"] / 2 + self.CHARACTER_WIDTH + 100,
			self.window_info["height"] / 2 + self.CHARACTER_HEIGHT
		)
		# cv2.imwrite('screen.png', img)

		boundaries = [
			# ([17, 15, 100], [50, 56, 200]),
			([86, 31, 4], [220, 88, 50]),
			# ([25, 146, 190], [62, 174, 250]),
			# ([103, 86, 65], [145, 133, 128])
		]

		for (lower, upper) in boundaries:
			# create NumPy arrays from the boundaries
			lower = np.array(lower, dtype="uint8")
			upper = np.array(upper, dtype="uint8")

			# find the colors within the specified boundaries and apply
			# the mask
			mask = cv2.inRange(img, lower, upper)
			output = cv2.bitwise_and(img, img, mask=mask)

			# show the images
			# cv2.imshow("findGold", output)
			# cv2.waitKey(0)

			ret, threshold1 = cv2.threshold(output, 1, 255, cv2.THRESH_BINARY)
			cv2.imwrite('2_threshold1_img.png', threshold1)

			# Morphological transformation
			kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
			closed = cv2.morphologyEx(threshold1, cv2.MORPH_CLOSE, kernel)
			cv2.imwrite('4_morph_img.png', closed)
			closed = cv2.cvtColor(closed, cv2.COLOR_BGR2GRAY)

			# closed = cv2.erode(closed, kernel, iterations=1)
			# cv2.imwrite('4_erode_img.png', closed)
			# kernel = (1, 1)
			# closed = cv2.dilate(closed, kernel, iterations=1)
			# cv2.imwrite('3_dilate_img.png', closed)
			template = cv2.imread('img/whiteBox.png', 0)

			res = cv2.matchTemplate(closed, template, cv2.TM_CCOEFF_NORMED)

			threshold = 0.9
			loc = np.where(res >= threshold)
			for pt in zip(*loc[::-1]):
				# return True
				cv2.rectangle(closed, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 2)
			cv2.imwrite('findGold.png', img)
			return False
