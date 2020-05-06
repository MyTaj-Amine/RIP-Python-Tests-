'''
@author: jcsombria
'''
import random
import time
import cherrypy

class Signal(object):

  def sample(self):
    return random.random()

class Sampler(object):
  def __init__(self, signal):
    self.signal = signal
    self.observers = []
    self.steps = 0

  def register(self, o):
    self.observers.append(o)

  def notify(self, data):
    for o in self.observers:
      try:
        o.update(data)
      except:
        pass

  def start(self):
    self.running = True
    while self.running:
      self.steps += 1
      data = self.signal.sample()
      self.notify(data)
      self.wait()
      #print(self.steps)
      #print(self.observers)

  def stop(self):
    self.running = False

  def wait(self):
    pass

class PeriodicSampler(Sampler):

  def __init__(self, first_sample, period, signal):
    super().__init__(signal)
    self.Ti = first_sample
    self.Ts = period
    self.reset()

  def notify(self, data):
    data = {
      'timestamp': self.last,
      'value': self.signal.sample(),
    }
    super().notify(data)

  def wait(self):
    # Wait until the next sampling time
    if self.steps > 1:
      self.next = self.time / self.Ts + self.Ts
      interval = self.Ts - self.time % self.Ts
      time.sleep(interval)
      self.time = time.time() - self.t0
      self.last = self.time
    else:
      self.next = self.time / self.Ti + self.Ti
      interval = self.Ti - self.time % self.Ts
      time.sleep(interval)
      self.time = time.time() - self.t0
      self.last = self.time

  def sample(self):
    self.signal.sample()

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


class PeriodicSoD(PeriodicSampler):

  def __init__(self, first_sample, period, signal, threshold):
    super().__init__(first_sample, period, signal)
    self.threshold = threshold
    self.firstStep = True

# change this condition
  def condition(self):
    lastparam = 2
    param = random.randint(1, 7)
    if abs(lastparam - param) < self.threshold:
      #print('\nCondition satisfied')
      return True
    else:
     # print('\ncondition not satisfied')
      return False

  def wait(self):
    event = False
    while not event:
      try:
          if self.firstStep:
              event = True
              self.firstStep = False
          else:
              event = self.condition()
      except:
        print('Cannot evaluate sampling condition.')
      super().wait()
