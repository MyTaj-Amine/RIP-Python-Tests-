'''
Amine Moulay Taj
'''
import time
import queue
from rip.RIPGeneric import RIPGeneric
from samplers.PeriodicSODSampler import SamplerSOD
from rip.RIPMeta import *



class PeriodicSendOnDelta(RIPGeneric):

  def __init__(self, info={}):
    '''
    Constructor
    '''
    super().__init__(info)
    self.sseFirst = 2
    self.ssePeriod = 1
    self.discon_tolerance = 20
    self.sseFirstConnect = False
    self.meet_Condition = False
    self.sent_events = 0
    self.lost_events = 0
    self.QuitTime = 0
    self.user_left = False
    self.q = queue.Queue()


  def start(self):
    if not self.sseRunning:
      self.sseRunning = True
      self.sampler = SamplerSOD(self.ssePeriod, self.sseFirst)
    self._running = True

  def nextSample(self):
    '''
    Retrieve the next periodic update
    '''
    self.ServerReconnection = time.time()

    if not self.sseRunning:
      self.sseRunning = True
      self.sampler = SamplerSOD(self.ssePeriod, self.sseFirst)

    if self.sseFirstConnect:
      print(f'Reconnection time:{time.ctime(self.ServerReconnection)}')
      if abs(self.ServerReconnection - self.QuitTime) > self.discon_tolerance:
        self.sseFirstConnect = False
        self.sampler.reset()
      else:
          self.lost_events = 0
          while not self.q.empty():
              yield 'Is a The lost events:\n'
              yield self.q.get()
              self.lost_events += 1
      print(f'Number of events losted during your disconnection is:{self.lost_events}')
      self.user_left = False

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
        # print("unfulfilled condition !!")
        self.sampler.wait()
        self.meet_Condition = SamplerSOD.set_param(2)
        if self.meet_Condition:
          try:
            self.preGetValuesToNotify()
            toReturn = self.getValuesToNotify()
            self.postGetValuesToNotify()
          except:
            toReturn = 'ERROR'
          try:
              print('Condition met and event sent')
              response = {"result": toReturn};
              event = 'PeriodicSendOnDelta'
              id = round(self.sampler.time * 1000)
              data = ujson.dumps(response)
              self.event = 'event: %s\nid: %s\ndata: %s\n\n' % (event, id, data)
              if not self.user_left:
                  yield self.event
              else:
                  self.q.put(self.event)
              self.sent_events += 1
          except GeneratorExit:
            self.QuitTime = time.time()
            print('The connection to the server is closed')
            print(f'The number of events sent during the user login: {self.sent_events}')
            print(f'Disconnection time :{time.ctime(self.QuitTime)}')
            self.user_left = True
            self.q.put(self.event)