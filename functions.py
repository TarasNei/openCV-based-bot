from PIL import ImageGrab, Image

from numpy import *
import time
import win32gui

WINDOW_SUBSTRING = "Lineage"


def get_window_info():
	# set window info
	window_info = {}
	win32gui.EnumWindows(set_window_coordinates, window_info)
	return window_info


# EnumWindows handler
# sets L2 window coordinates
def set_window_coordinates(hwnd, window_info):
	if win32gui.IsWindowVisible(hwnd):
		if WINDOW_SUBSTRING in win32gui.GetWindowText(hwnd):
			rect = win32gui.GetWindowRect(hwnd)
			x = rect[0]
			y = rect[1]
			w = rect[2] - x
			h = rect[3] - y
			window_info['x'] = x
			window_info['y'] = y
			window_info['width'] = w
			window_info['height'] = h
			window_info['name'] = win32gui.GetWindowText(hwnd)
			win32gui.SetForegroundWindow(hwnd)


def get_screen(x1, y1, x2, y2):
	box = (x1 + 8, y1 + 30, x2 - 8, y2)
	screen = ImageGrab.grab(box)
	img = array(screen.getdata(), dtype=uint8)
	reshaped = img.reshape((screen.size[1], screen.size[0], 3))

	# temp = Image.fromarray(reshaped, "RGB")
	# temp.show()

	return reshaped


def smooth_move(autohotpy, x, y):
	flags, cursor, (startX, startY) = win32gui.GetCursorInfo()
	# coordinates = draw_line(startX, startY, x, y)
	# autohotpy.moveMouseToPosition(x, y)

	# x = 0
	# for dot in coordinates:
	# 	x += 1
	# 	if x % 2 == 0 and x % 3 == 0:
	# 		time.sleep(0.01)
		# autohotpy.moveMouseToPosition(dot[0], dot[1])


def draw_line(x1=0, y1=0, x2=0, y2=0):
	coordinates = []

	dx = x2 - x1
	dy = y2 - y1

	sign_x = 1 if dx > 0 else -1 if dx < 0 else 0
	sign_y = 1 if dy > 0 else -1 if dy < 0 else 0

	if dx < 0:
		dx = -dx
	if dy < 0:
		dy = -dy

	if dx > dy:
		pdx, pdy = sign_x, 0
		es, el = dy, dx
	else:
		pdx, pdy = 0, sign_y
		es, el = dx, dy

	x, y = x1, y1

	error, t = el / 2, 0

	coordinates.append([x, y])

	while t < el:
		error -= es
		if error < 0:
			error += el
			x += sign_x
			y += sign_y
		else:
			x += pdx
			y += pdy
		t += 1
		coordinates.append([x, y])

	return coordinates
