# - *- coding: utf- 8 - *-
'''
Created on 10/11/2015
Modified on 2018/07/01

@author: jcsombria
'''
import cherrypy
import ujson
import time
import os

from rip.RIPGeneric import RIPGeneric
from rip.RIPMeta import *

class Root(object):
  exposed = True
  control = RIPGeneric()
  experiences = [
    { 'id':'TestOK' },
  ]
  host = '< host_ip >:2055'

  @cherrypy.expose
  def index(self, expId=None):
    '''
    GET - Retrieve the list of experiences or information about a specific experience
    '''
    if expId is not None:
      if expId in [e['id'] for e in self.experiences]:
        response = self.control.info()
      else:
        response = '{}'
    else:
      response = self.info()
    return response.encode("utf-8")

  @cherrypy.expose
  def SSE(self, expId=None):
    '''
    SSE - Connect to an experience's SSE channel to receive periodic updates
    '''
    cherrypy.response.headers['Content-Type'] = 'text/event-stream'
    cherrypy.response.headers['Cache-Control'] = 'no-cache'
    cherrypy.response.headers['Connection'] = 'keep-alive'

    return self.control.nextSample()
  SSE._cp_config = {'response.stream': True}

  @cherrypy.expose
  @cherrypy.tools.accept(media='application/json')
  def POST(self):
    '''
    POST - JSON-RPC control commands (get/set)
    '''
    socket = cherrypy.request.body.fp
    message = socket.read()
    response = self.control.parse(message)
    return response.encode("utf-8")

  def info(self):
    '''
    Build server info string
    '''
    params_get_info = [
      RIPParam(name='Accept',required='no',location='header',value='application/json'),
      RIPParam(name='expId',required='no',location='query',type_='string'),
    ]
    get_info = RIPMethod(
      url='http://%s/RIP' % self.host, 
      description='Retrieves information (variables and methods) of the experiences in the server',
      type_='GET',
      params=params_get_info,
      returns='application/json',
      example='http://%s/RIP?expId=TestOK' % self.host
    )
    meta = RIPExperienceList(self.experiences, [get_info])
    return str(meta)

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
  # Provides a relative log path from the original script path
  # instead from the invocation path
  base_dir = os.path.dirname(os.path.realpath(__file__))
  log_dir = os.path.join(base_dir, 'log')
  access_log_file = os.path.join(log_dir, 'access.log')
  error_log_file = os.path.join(log_dir, 'error.log')
  cherrypy.config.update({
    'server.socket_port': 2055,
    'log.access_file' : access_log_file,
    'log.errors_file' : error_log_file
  })
  config = {
    '/': {
      'tools.sessions.on': True,
      'tools.response_headers.on': True,
      'tools.response_headers.headers': [
        ('Content-Type', 'application/json'),
        ('Access-Control-Allow-Origin', '*'),
      ],
      'tools.encode.on': True,
      'tools.encode.encoding': 'utf-8',
    },
  }

  cherrypy.quickstart(Root(), '/RIP', config)
