
# this file defines a wrapper object around the Adafruit PWM hat that is designed to be thread-safe.
# i don't know exactly how long the "set pwm" operation takes, its probably instant, but there should
# be zero downside and only upside to making it thread-safe, since it is shared hardware.



# debug mode switch that enables/disables actual hardware
PWM_WRAPPER_USE_HARDWARE = True
# debug mode switch that enables/disables print statements (will absolutely flood the logs tho)
PWM_WRAPPER_DEBUG_PRINTS = False



# TODO: add "logging" module?
import threading
if PWM_WRAPPER_USE_HARDWARE:
	import Adafruit_PCA9685


# example: pwm_L = pwm_wrapper(PWM_ADDR_L, PWM_FREQ)
class Pwm_Wrapper(object):
	def __init__(self, addr, freq):
		self.address = addr
		self.freq = freq
		if PWM_WRAPPER_USE_HARDWARE:
			self.pwm_adafruit = Adafruit_PCA9685.PCA9685(address=addr)
			self.pwm_adafruit.set_pwm_freq(freq)
		else:
			self.pwm_adafruit = None
		# the lock object: only one thread can "have" the lock at a time, others will wait till its free
		self._lock = threading.Lock()

	def set_pwm(self, channel, on, off):
		# following info comes from the docs:
		# channel: The channel that should be updated with the new values (0..15)
		# on: The tick (between 0..4095) when the signal should transition from low to high
		# off:The tick (between 0..4095) when the signal should transition from high to low
		
		# we never have any use for changing the on-point, we only care about the duty cycle...
		# TODO: eliminate the "on" arg?
		
		# take the lock, set pwm, and release the lock
		with self._lock:
			if PWM_WRAPPER_DEBUG_PRINTS:
				print("pwm=" + str(self.address) + " channel=" + str(channel) + " set to val=" + str(off))
			if PWM_WRAPPER_USE_HARDWARE:
				self.pwm_adafruit.set_pwm(channel, on, off)
			pass
		
		pass
	pass

