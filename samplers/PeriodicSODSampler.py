'''
@author: Amine MOULAY TAJ
'''
import time
import random
from .Samplers import PeriodicSampler as Periodic
#from Samplers import PeriodicSampler

class SamplerSOD(Periodic):

  def __init__(self, period, first):
    super().__init__(period)
    self.Ti = first
    self.next = self.Ti
    self.elapsed_time = 0


  def wait_first_sample(self):
    self.time = time.time() - self.t0
    self.last = self.time
    self.next = self.time / self.Ti + self.Ti
    interval = self.Ti - self.time % self.Ti
    time.sleep(interval)

  def set_param(self, d=2):
    lastparam = 2
    param = random.randint(1, 7)
    if abs(lastparam - param) < d:
        return True
    else:
        return False

  def connection_time(self):
    limit = 20
    self.elapsed_time = time.time() - self.t0
    if elapsed_time > limit:
      return True
    else:
      return False
