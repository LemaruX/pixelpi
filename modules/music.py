import time
import math
from helpers import *
from modules import Module
import serial
from thread import start_new_thread

class Music(Module):
	def __init__(self, screen):
		super(Music, self).__init__(screen)
		self.serial = serial.Serial('/dev/ttyAMA0', 9600)
		self.data = [0 for i in range(7)]
		self.position = 0
		start_new_thread(self.check_serial, ())
		self.last_frame = time.time()
		self.delta_t = 0
		self.colors = [hsv_to_color(x / 16.0, 1, 1) for x in range(16)]
		self.inertia = [0 for x in range(16)]

	def check_serial(self):
		while self.running:
			try:
				byte = ord(self.serial.read())
				if byte == 255:
					self.position = 0
				elif self.position < 7:
					self.data[self.position] = byte
					self.position += 1
			except:
				pass
	
	def tick(self):
		self.draw()

		now = time.time()
		self.delta_t = now - self.last_frame
		self.last_frame = now

	def get_value(self, index):
		pos = index * 6.0 / 15.0
		fraction = pos % 1.0
		if fraction < 0.01:
			return self.data[int(pos)]
		lower = int(math.floor(pos))
		upper = int(math.ceil(pos))
		return self.data[lower] * fraction + self.data[upper] * (1 - fraction)

	def draw(self):
		self.screen.clear()
		for x in range(16):
			value = self.get_value(x) * 16.0 / 254.0
			for y in range(int(value)):
				self.screen.pixel[x][15 - y] = self.colors[x]
			self.inertia[x] = max(self.inertia[x], value)
			if int(self.inertia[x]) < 16:
				self.screen.pixel[x][15 - int(self.inertia[x])] = Color(255, 255, 255)
			self.inertia[x] -= self.delta_t * 15

		self.screen.update()

	def on_stop(self):
		self.serial.close()
