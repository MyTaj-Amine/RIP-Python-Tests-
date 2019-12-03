'''
@author: jcsombria
'''
import time

from jsonrpc.JsonRpcServer import JsonRpcServer
from jsonrpc.JsonRpcBuilder import JsonRpcBuilder
from rip.RIPMeta import *
import random
builder = JsonRpcBuilder()

class RIPGeneric(JsonRpcServer):
  '''
  RIP Server - Reference Implementation
  '''

  def __init__(self, info={}):
    '''
    Constructor
    '''
    metadata = self._parse_info(info)
    super().__init__(metadata['name'], metadata['description'])
    self.metadata = metadata
    self.ssePeriod = 15
    self.sseThreshold = 1
    self.sseFirst = 9
    self.sseFirstConnect = False
    self.sseRunning = False
    self._running = False
    self.addMethods({
      'get': { 'description': 'To read server variables',
        'params': { 'expId': 'string', 'variables': '[string]' },
        'implementation': self.get,
      },
      'set': { 'description': 'To write server variables',
        'params': { 'expId': 'string', 'variables': '[string]', 'values':'[]' },
        'implementation': self.set,
      },
    })

  def default_info(self):
    return {
      'name':'RIP Generic',
      'description':'Generic RIP Server Implementation.',
      'authors': 'J. Chacon',
      'keywords': 'Raspberry PI, RIP',
      'readables': [{
        'name':'time',
        'description':'Server time in seconds',
        'type':'float',
        'min':'0',
        'max':'Inf',
        'precision':'0',
      }],
      'writables': [],
    }

  def _parse_info(self, info):
    metadata = self.default_info()
    for p in info:
      try:
        metadata[p] = info[p]
      except:
        print('[WARNING] Property: %s not specified. Setting default value.' % p)
    return metadata

  def start(self):
    '''
    Iniatilizes the server. Any code meant to be run at init should be here.
    '''
    if not self.sseRunning:
        self.sseRunning = True
        #self.sampler = Sampler(self.ssePeriod)
        self.sampler = SamplerSOD(self.ssePeriod, self.sseFirst, self.sseThreshold)
    self._running = True

  @property
  def running(self):
    return self._running

  @running.setter
  def running(self):
    pass

  def info(self, address='127.0.0.1:8080'):
    '''
    Retrieve the experience's info
    '''
    try:
      info = self.info_string
    except:
      info = self.build_info(address)
      self.info_string = info
    return info

  def build_info(self, address):
    '''
    Generate the experience's info string
    '''
    info = RIPServerInfo(
      self.name,
      self.description,
      authors=self.metadata['authors'],
      keywords=self.metadata['keywords']
    )
    readables = RIPVariablesList(
      list_=self.metadata['readables'],
      methods=[self.buildSSEGetInfo(address), self.buildPOSTGetInfo(address)],
      read_notwrite=True
    )
    writables = RIPVariablesList(
      list_=self.metadata['writables'],
      methods=[self.buildPOSTSetInfo(address)],
      read_notwrite=False
    )
    meta = RIPMetadata(info, readables, writables)
    return str(meta)

  def buildSSEGetInfo(self, address):
    return RIPMethod(
      url='%s/RIP/SSE' % address,
      description='Suscribes to an SSE to get regular updates on the servers\' variables',
      type_='GET',
      params=[
        RIPParam(name='Accept',required='no',location='header',value='application/json'),
        RIPParam(name='expId',required='yes',location='query',type_='string'),
        RIPParam(name='variables',required='no',location='query',type_='array',subtype='string'),
      ],
      returns='text/event-stream',
      example='%s/RIP/SSE?expId=%s' % (address, self.metadata['name']),
    )

  def buildPOSTGetInfo(self, address):
    elements = [{'description': 'Experience id','type': 'string'},
    {'description': 'Name of variables to be retrieved','type': 'array','subtype': 'string'}]
    return RIPMethod(
      url='%s/RIP/POST' % address,
      description='Sends a request to retrieve the value of one or more servers\' variables on demand',
      type_='POST',
      params=[
        RIPParam(name='Accept',required='no',location='header',value='application/json'),
        RIPParam(name='Content-Type',required='yes',location='header',type_='application/json'),
        RIPParam(name='jsonrpc',required='yes',type_='string',location='body',value='2.0'),
        RIPParam(name='method',required='yes',type_='string',location='body',value='get'),
        RIPParam(name='params',required='yes',type_='array',location='body',elements=elements),
        RIPParam(name='id',required='yes',type_='int',location='body'),
      ],
      returns='application/json',
      example={ '%s/RIP/POST' % address: {
        'headers': {'Accept': 'application/json','Content-Type': 'application/json'},
        'body': {'jsonrpc':'2.0', 'method':'get', 'params':['%s' % self.metadata['name'], [r['name'] for r in self.metadata['readables']]], 'id':'1'}
      }}
    )

  def buildPOSTSetInfo(self, address):
    elements = [{'description': 'Experience id','type': 'string'},
    {'description': 'Name of variables to write','type': 'array','subtype': 'string'},
    {'description': 'Value for variables','type': 'array','subtype': 'mixed'}]
    params_post_set = [
      RIPParam(name='Accept',required='no',location='header',value='application/json'),
      RIPParam(name='Content-Type',required='yes',location='header',type_='application/json'),
      RIPParam(name='jsonrpc',required='yes',type_='string',location='body',value='2.0'),
      RIPParam(name='method',required='yes',type_='string',location='body',value='set'),
      RIPParam(name='params',required='yes',type_='array',location='body',elements=elements),
      RIPParam(name='id',required='yes',type_='int',location='body'),
      RIPParam(name='variables',required='no',location='query',type_='array',subtype='string'),
    ]
    example_post_set = {
      '%s/RIP/POST' % address: {
        'headers': {'Accept': 'application/json','Content-Type': 'application/json'},
        'body': {'jsonrpc':'2.0','method':'set','params':['%s' % self.metadata['name'],[w['name'] for w in self.metadata['writables']],['val' for w in self.metadata['writables']]],'id':'1'}
      }
    }
    return RIPMethod(
      url='%s/RIP/POST' % address,
      description='Sends a request to retrieve the value of one or more servers\' variables on demand',
      type_='POST',
      params=params_post_set,
      returns='application/json',
      example=example_post_set
    )

  def set(self, expid, variables, values):
    '''
    Sends one or more variables to the server
    '''
    pass

  def get(self, expid, variables):
    '''
    Retrieve one or more variables from the server
    '''
    pass

  def _getReadables(self):
    readables = []
    for r in self.metadata['readables']:
      readables.append(r['name'])
    return readables

  def _getWritables(self):
    writables = []
    for r in self.metadata['writables']:
      writables.append(r['name'])
    return writables

  '''
      The last periodic send data next sample
   '''
  #def nextSample(self):
   # '''
    #Retrieve the next periodic update
   # '''
    # TO DO: Remove this code and start when the first client arrives
   # if not self.sseRunning:
      #self.sseRunning = True
      #self.sampler = Sampler(self.ssePeriod)
      #self.sampler = PeriodicSODSampler.SODSampler(self.first_sample, self.ssePeriod, self.ssethreshold)

    #while self.sseRunning:
     # self.sampler.wait()
      #try:
       # self.preGetValuesToNotify()
        #toReturn = self.getValuesToNotify()
        #self.postGetValuesToNotify()
      #except:
       # toReturn = 'ERROR'
      #response = {"result":toReturn};
      #event = 'periodiclabdata'
      #id = round(self.sampler.time * 1000)
      #data = ujson.dumps(response)
      #yield 'event: %s\nid: %s\ndata: %s\n\n' % (event, id, data)

  def nextSample(self):
    '''
    Retrieve the next periodic update
    '''
    if not self.sseRunning:
     self.sseRunning = True
     self.sampler = SamplerSOD(self.ssePeriod, self.sseFirst, self.sseThreshold)

    #self.sampler.wait_first_sample()
    #try:
      #firstSample = self.getValuesToNotify()
    #except:
      #firstSample = "ERROR first sample"
    #response = {"First_sample result": firstSample};
    #event = 'PeriodicSendOnDelta'
    #id = round(self.sampler.time * 1000)
    #data = ujson.dumps(response)
    #yield 'event: %s\nid: %s\ndata: %s\n\n' % (event, id, data)

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

  def preGetValuesToNotify(self):
    '''
    To do before obtaining values to notify
    '''
    #self.sampler.set_param()
    pass

  def getValuesToNotify(self):
    '''
    Which values will be notified
    '''
    return [
      [ 'time' ],
      [ self.sampler.lastTime() ]
    ]

  def postGetValuesToNotify(self):
    '''
    To do after obtaining values to notify
    '''
    pass

class Sampler(object):

  def __init__(self, period):
    self.Ts = period
    self.reset()

  def wait(self):
    self.last = self.time
    self.time = time.time() - self.t0
    self.next = self.time / self.Ts + self.Ts
    interval = self.Ts - self.time % self.Ts
    time.sleep(interval)

  def reset(self):
    self.t0 = time.time()
    self.time = 0
    self.last = 0
    self.next = self.Ts

  def delta(self):
    return self.time - self.last

  def lastTime(self):
    return self.last


class SamplerSOD(Sampler):

  def __init__(self, period, first, threshold):
    super().__init__(period)
    self.Ti = first
    self.d = threshold
    self.lastparam = 2
    self.next = self.Ti
    #self.wait_first_sample()

  def wait_first_sample(self):
    self.time = time.time() - self.t0
    self.last = self.time
    self.next = self.time / self.Ti + self.Ti
    interval = self.Ti - self.time % self.Ti
    time.sleep(interval)

  def set_param(self):
    self.param = random.randint(0,10)
    if abs(self.lastparam - self.param) > self.d:
      return True
    else:
      return False

  def temps_session(self):
      temps_connection = time.time()- self.t0
      if temps_connection > 40:
        self.new = True
      else:
        self.new = False


