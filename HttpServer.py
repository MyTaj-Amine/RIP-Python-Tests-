# - *- coding: utf- 8 - *-
'''
@author: jcsombria
'''
import queue
import time
import cherrypy
import os
import random
import binascii
import ujson

from rip.RIPGeneric import RIPGeneric
from rip.core import *

class HttpServer(object):
  '''
  RIP Server implementation
  '''
  exposed = True

  def __init__(self, control=RIPGeneric(), host='127.0.0.1', port=8080):
    self.control = control
    self.host = host
    self.port = port
    self.experiences = [{ 'id': control.name }]
    self.firstTime = False
    self.ClientID = 0
    self.connectedClients = 0

  @cherrypy.expose
  def index(self, expId=None):
    '''
    GET - Retrieve the list of experiences or information about a specific experience
    '''
    if expId is not None:
      if expId in [e['id'] for e in self.experiences]:
        response = self.control.info(self.getAddr())
      else:
        response = '{}'
    else:
      response = self.info()
    return response.encode("utf-8")

  def getAddr(self):
    return '%s:%s' % (self.host, self.port)


  @cherrypy.expose
  def SSE(self, expId=None):
    '''
    SSE - Connect to an experience's SSE channel to receive periodic updates
    '''
    cherrypy.response.headers['Content-Type'] = 'text/event-stream'
    cherrypy.response.headers['Cache-Control'] = 'no-cache'
    cherrypy.response.headers['Connection'] = 'keep-alive'
    if expId is not None:
      # if expId in [e['id'] for e in self.experiences]:
      self.control.sseRunning = True
      if len(self.control.clients) == 0:
        self.control.sampler.reset()
      if 'session_id' not in cherrypy.request.cookie:
        file_name = str(cherrypy.session.id) + '.txt'
        filepath = os.path.join('C:/Users/34603/PycharmProjects/rip-python-server-NewVersion/log', file_name)
        f = open(filepath, "a")
        self.ClientID += 1
        print(f'\nNew user connected({self.ClientID})')
        cherrypy.session['ClientID'] = self.ClientID
        print("user's sessionID: " + cherrypy.session.id)
        self.control.clients.append(cherrypy.session.id)
        evgen = self.control.connect()
        evgen.userSession = cherrypy.session.id
        evgen.userID = self.ClientID
        # evgen.is_disconnected = False
        f.close()
        return evgen.next()
      else:
        print(f"\nUser number {cherrypy.session['ClientID']} is reconnected")
        print(f"User's sessionID: "+ cherrypy.session.id)
        evgen = self.control.connect()
        lostevents = self.control.reconnect()
        evgen.lostevents = lostevents
        evgen.userSession = cherrypy.session.id
        evgen.userID = cherrypy.session['ClientID']
        return evgen.next()
    return 'event: CLOSE\n\n'
  SSE._cp_config = {'response.stream': True}


  @cherrypy.expose
  @cherrypy.tools.accept(media='application/json')
  def POST(self):
    '''
    POST - JSON-RPC control commands (get/set)
    '''
    socket = cherrypy.request.body.fp
    message = socket.read()
    if not self.control.running:
        self.control.start()
    response = self.control.parse(message)
    return response.encode("utf-8")

  def info(self):
    '''
    Build server info string
    '''
    meta = RIPExperienceList(self.experiences, [self.buildGetInfo()])
    return str(meta)

  def buildGetInfo(self):
    return RIPMethod(
      url='%s/RIP' % self.getAddr(),
      description='Retrieves information (variables and methods) of the experiences in the server',
      type_='GET',
      params=[
        RIPParam(name='Accept',required='no',location='header',value='application/json'),
        RIPParam(name='expId',required='no',location='query',type_='string'),
      ],
      returns='application/json',
      example='http://%s/RIP?expId=%s' % (self.getAddr(), self.control.name)
    )

  def start(self, enable_ssl=False):
    base_dir = os.path.dirname(os.path.realpath(__file__))
    log_dir = os.path.join(base_dir, 'log')
    access_log_file = os.path.join(log_dir, 'access.log')
    error_log_file = os.path.join(log_dir, 'error.log')
    cherrypy.config.update({
      'tools.sessions.on': True,
      'tools.proxy.on':True,
      'server.socket_host': '0.0.0.0',
      'server.socket_port': self.port,
      'log.access_file' : access_log_file,
      'log.errors_file' : error_log_file
    })
    config = {
      '/': {
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [
          ('Content-Type', 'application/json'),
          ('Access-Control-Allow-Origin', '*'),
        ],
        'tools.encode.on': True,
        'tools.encode.encoding': 'utf-8',
        # Avoid redirect when the URL does not have an ending '\'
        'tools.trailing_slash.on': False,
      },
    }
    if enable_ssl:
      cherrypy.server.ssl_module = 'builtin'
      cherrypy.server.ssl_certificate = '%s/%s' % (base_dir, 'cert.pem')
      cherrypy.server.ssl_private_key = '%s/%s' % (base_dir, 'privkey.pem')
    cherrypy.quickstart(self, '/RIP', config)

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
  HttpServer().start()
