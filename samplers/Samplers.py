'''
@author: jcsombria
'''
import time

class PeriodicSampler(object):

  def __init__(self, period):
    # Set the sampling period
    self.Ts = period
    self.reset()

  def wait(self):
    # Wait until the next sampling time
    self.next = self.time / self.Ts + self.Ts
    interval = self.Ts - self.time % self.Ts
    time.sleep(interval)
    self.time = time.time() - self.t0
    self.last = self.time

  def reset(self):
    # Reset to the initial state
    self.t0 = time.time()
    self.time = 0
    self.last = 0
    self.next = self.Ts

  def delta(self):
    # Compute the time elapsed since the last sampling time
    return self.time - self.last

  def lastTime(self):
    # Last sampling time
    return self.last
