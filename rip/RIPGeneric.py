'''
@author: jcsombria
'''
from jsonrpc.JsonRpcServer import JsonRpcServer
from jsonrpc.JsonRpcBuilder import JsonRpcBuilder
from rip.core.RIPMeta import *
from AppConfig import config
import samplers
import os
import time
import cherrypy

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
    self.clients = []
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
    self.variable_config = config['control']['info']['readables']
    self.general_config = config['control']['info']['sampling_methods']
    self.sampling_method()


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
    if not self.running:
      self.running = True

  @property
  def running(self):
    return self._running

  @running.setter
  def running(self):
    pass

  def sampling_method(self):
      self.sampling_method = self.variable_config[0]['sampling']['type']
      if self.sampling_method == 'PeriodicSampler':
        self.first_sample =  float(self.general_config['PeriodicSampler']['first_sampling'])
        self.period = float(self.general_config['PeriodicSampler']['period'])
        self.s = samplers.Signal()
        self.sampler = samplers.Periodic(self.first_sample, self.period,  self.s)
      elif self.sampling_method == 'PeriodicSoD':
        self.first_sample = float(self.general_config['PeriodicSendOnDelta']['first_sampling'])
        self.period = float(self.general_config['PeriodicSendOnDelta']['period'])
        self.s = samplers.Signal()
        self.threshold =  float(self.variable_config[0]['sampling']['params']['delta'])
        self.sampler = samplers.SoDsampler(self.first_sample, self.period,  self.s, self.threshold)
      else:
          print('sampling method dont found')


  def connect(self):
    #if len(self.clients) == 0:
    if self.sampler.steps == 0:
      self.sampler.reset()
      sampler = threading.Thread(target=lambda: self.sampler.start())
      sampler.start()
    evgen = EventGenerator()
    self.sampler.register(evgen)
    return evgen

  @cherrypy.expose
  def reconnect(self):
    fileId = cherrypy.request.cookie['fileId'].value
    file_name = str(fileId) + '.txt'
    #filepath = os.path.join('C:/Users/34603/PycharmProjects/rip-python-server-NewVersion/log', file_name)
    f = open(file_name, "r")
    content = f.read()
    f.close()
    return content

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


import threading
class EventGenerator(object):

  def __init__(self):
    self.event = threading.Event()
    self.Eventosend = ''
    self.lostevents = ''
    self.is_disconnected = False
    self.userID = 0
    self.userSession = ''
    self.reconnect = False
    self.resend = True

  def update(self, data):
    self.data = data
    self.event.set()


  def next(self):
    while True:
      self.event.wait()
      # Gather result
      timestamp = self.data['timestamp']
      result = {"result": self.data}
      # Build SSE message
      eventname = 'periodiclabdata'
      id = round(timestamp * 1000)
      data = ujson.dumps(result)
      self.event.clear()
      self.Eventosend = 'event: %s\nid: %s\ndata: %s\n\n' % (eventname, id, data)
      if self.resend:
          yield self.lostevents
          file_name = str(self.userSession) + '.txt'
          f = open(file_name, "w")
          f.close()
          self.resend = False
          self.reconnect = False
      try:
        if not self.is_disconnected:
          yield self.Eventosend
        else:
          file_name = str(self.userSession) + '.txt'
          f = open(file_name, "a")
          f.write(self.Eventosend)
          f.close()
      except:
        print(f'\nUser{self.userID} disconnected')
        print("User's sessionID :" + self.userSession)
        if not self.reconnect:
          self.is_disconnected = True
          print (self.is_disconnected)
          #self.reconnect = False