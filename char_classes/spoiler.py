from functions import *
from bot import Bot


class Spoiler(Bot):

	def loop(self, stop_event):
		spoiled = False
		i = 0

		while not stop_event.is_set():
			time.sleep(0.2)
			self.useless_steps = 0
			targeted_hp = self.get_targeted_hp()

			if targeted_hp > 0:

				if targeted_hp < 70 and not spoiled:
					print("spoil")
					spoiled = True
					self.autohot_py.F2.press()
					time.sleep(0.5)

				if i > 10:
					self.go_somewhere()
					i = 0

				print("attack the target")
				self.autohot_py.F1.press()
				continue

			elif targeted_hp == 0:

				if spoiled is True:
					spoiled = False
					print("sweep")
					time.sleep(0.3)
					self.autohot_py.F3.press()
					time.sleep(0.3)
					self.autohot_py.F3.press()
					time.sleep(0.3)
				self.autohot_py.F4.press()
				time.sleep(0.3)
				self.autohot_py.F4.press()
				time.sleep(0.3)
				self.autohot_py.F4.press()

				print("target is dead")
				continue
			else:
				print("no target yet")
				# Find and click on the victim
				if self.set_target():
					time.sleep(0.3)
					spoiled = False
					self.useless_steps = 0
					print("set_target - attack")
					self.autohot_py.F1.press()
					continue

			if self.useless_steps > 2:
				# We're stuck, go somewhere
				self.useless_steps = 0
				print("go_somewhere - we're stuck")
				self.go_somewhere()
			else:
				# Turn on 90 degrees
				self.useless_steps += 1
				self.turn()
				print("turn")

			print("next iteration")
			pass

	print("loop finished!")
