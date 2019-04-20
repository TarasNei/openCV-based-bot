from char_classes.spoilerKeyBoardTargeting import Spoiler
from char_classes.meleeKeyboard import Melee
from lib.AutoHotPy import AutoHotPy

import threading


class Singleton(type):

	_instances = {}

	def __call__(cls, *args, **kwargs):
		"""
		kind of constructor = get instance
		"""
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class Launcher:

	__metaclass__ = Singleton

	def __init__(self, char_class):
		auto_py = AutoHotPy()
		auto_py.registerExit(auto_py.F12, self.stop_bot_event_handler)

		self.bot_thread_stop_event = threading.Event()

		self.auto_py_thread = threading.Thread(target=self.start_auto_py, args=(auto_py,))
		self.bot_thread = threading.Thread(
			target=self.start_bot,
			args=(auto_py, self.bot_thread_stop_event, char_class)
		)

		self.auto_py_thread.start()
		self.bot_thread.start()

	@staticmethod
	def stop_bot_event_handler(auto, event):
		auto.stop()

	@staticmethod
	def start_auto_py(auto):
		auto.start()

	@staticmethod
	def start_bot(auto, stop_event, character_class):
		classmap = {
			'Spoiler': Spoiler
			# 'Melee': Melee
		}
		bot = classmap[character_class](auto)
		bot.loop(stop_event)

	def stop_bot(self):
		self.bot_thread_stop_event.set()
