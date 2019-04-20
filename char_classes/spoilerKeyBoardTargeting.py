from functions import *
from bot import Bot
from colors import bcolors

import random

class Spoiler(Bot):
	ATTACKS_LIMIT_BEFORE_TURN = 3

	__spoiled = False

	def loop(self, stop_event):
		attacks = 0

		while not stop_event.is_set():

			player_hp = self.get_player_hp()
			targeted_hp = self.get_targeted_hp()

			if player_hp < 80:
				self.regenerateHp()

			if targeted_hp > 0:
				print(bcolors.OKBLUE, 'target hp', targeted_hp, '%', bcolors.ENDC)
				self.useless_steps = 0
				self.spoil(targeted_hp)


				if attacks > self.ATTACKS_LIMIT_BEFORE_TURN and targeted_hp >= 100 and self.isStacked():
					print(bcolors.BOLD, 'go somewhere', bcolors.ENDC)
					self.go_somewhere()
					time.sleep(1)
					print(bcolors.BOLD, 'turn', bcolors.ENDC)
					self.turn()
					attacks = 0

				if not attacks % 7 and targeted_hp >= 95: # bad
					self.autohot_py.F5.press()
					time.sleep(0.3)
					self.autohot_py.F1.press()

				print(bcolors.OKGREEN, "attack the target", bcolors.ENDC)
				self.autohot_py.F1.press()
				attacks += 1
				continue
			elif targeted_hp == 0:

				if self.__spoiled is True:
					self.__spoiled = False
					print(bcolors.WARNING, "sweep", bcolors.ENDC)
					self.autohot_py.F3.press()
					time.sleep(0.2)
					self.autohot_py.F3.press()
					time.sleep(0.2)

				self.pickUpDrop()
				print( "target is dead, find another")

				self.set_target()
				continue
			else:
				print("no target yet")
				self.__spoiled = False
				self.useless_steps = 0
				print("define target")
				self.set_target()
				continue

				# targeted_hp = self.get_targeted_hp()
				# if targeted_hp:
				# 	time.sleep(0.5)
				# 	self.autohot_py.F1.press()
				# 	continue
				# elif self.useless_steps > 2:
				# 	# We're stuck, go somewhere
				# 	self.useless_steps = 0
				# 	print(bcolors.BOLD, 'go somewhere', bcolors.ENDC)
				# 	self.go_somewhere()
				# else:
				# 	# Turn on 90 degrees
				# 	self.useless_steps += 1
				# 	self.turn()
				# 	print("turn")

		print("loop finished!")

	def spoil(self, targeted_hp):

		if targeted_hp < 80 and not self.__spoiled:
			print(bcolors.OKGREEN, "spoil", bcolors.ENDC)
			self.__spoiled = True
			self.autohot_py.F2.press()
			time.sleep(0.3)


	def set_target(self):
		# self.autohot_py.F6.press()
		random_target = int(random.randrange(0, 1))
		# random_target = bool(random.getrandbits(1))

		if random_target:
			self.autohot_py.F6.press()
		# elif random_target == 2:
		# 	self.autohot_py.F8.press()
		else:
			self.autohot_py.F7.press()

		# if self.get_targeted_hp() <= 0:
		# 	self.set_target()
		# self.pickUpDrop()


	def regenerateHp(self):
		self.autohot_py.F10.press()

		# hp1	= self.get_player_hp()
		# time.sleep(1)
		# hp2	= self.get_player_hp()
		#
		# if  hp2 < hp1:
		# 	print(bcolors.FAIL, 'cant regen hp, under attack!', bcolors.ENDC)
		#
		# 	while True:
		# 		self.autohot_py.F5.press()
		#
		# 		if self.get_targeted_hp():
		# 			while self.get_targeted_hp():
		# 				self.autohot_py.F1.press()
		# 				time.sleep(0.75)
		# 		else:
		# 			break
		#
		# self.pickUpDrop() # in case if it was a fight
		#
		# print(bcolors.OKGREEN, 'regenerating hp', bcolors.ENDC)
		# self.autohot_py.F11.press()
		#
		# hp = self.get_player_hp()
		# while hp < 90:
		# 	print(bcolors.OKBLUE, 'hero hp -', bcolors.BOLD, int(self.get_player_hp()), bcolors.ENDC)
		# 	time.sleep(3)
		# self.autohot_py.F11.press()


	def pickUpDrop(self):
		print(bcolors.OKGREEN, "picking up drop", bcolors.ENDC)
		for i in range(4):
			self.autohot_py.F4.press()
			time.sleep(0.5)