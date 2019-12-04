'''
Amine Moulay Taj
'''

from rip.RIPGeneric import RIPGeneric
from samplers.PeriodicSODSampler import SamplerSOD
from rip.RIPMeta import *

class PeriodicSendOnDelta(RIPGeneric):

  def __init__(self, info={}):
    '''
    Constructor
    '''
    super().__init__(info)
    self.sseFirst = 5
    self.ssePeriod = 3
    self.sseFirstConnect = False
    self.meet_Condition = False

  def start(self):
    if not self.sseRunning:
      self.sseRunning = True
      self.sampler = SamplerSOD(self.ssePeriod, self.sseFirst)
    self._running = True

  def nextSample(self):
    '''
    Retrieve the next periodic update
    '''
    if not self.sseRunning:
      self.sseRunning = True
      self.sampler = SamplerSOD(self.ssePeriod, self.sseFirst)

    while self.sseRunning:
      if not self.sseFirstConnect:
        self.sseFirstConnect = True
        self.sampler.wait_first_sample()
        try:
          firstSample = self.getValuesToNotify()
        except:
          firstSample = "ERROR first sample"
        response = {"First_sample result": firstSample};
        event = 'PeriodicSendOnDelta'
        id = round(self.sampler.time * 1000)
        data = ujson.dumps(response)
        yield 'event: %s\nid: %s\ndata: %s\n\n' % (event, id, data)
      else:
        self.sampler.wait()
        self.meet_Condition = SamplerSOD.set_param(2)
        if self.meet_Condition:
          try:
            self.preGetValuesToNotify()
            toReturn = self.getValuesToNotify()
            self.postGetValuesToNotify()
          except:
            toReturn = 'ERROR'
          response = {"result": toReturn};
          event = 'PeriodicSendOnDelta'
          id = round(self.sampler.time * 1000)
          data = ujson.dumps(response)
          yield 'event: %s\nid: %s\ndata: %s\n\n' % (event, id, data)
