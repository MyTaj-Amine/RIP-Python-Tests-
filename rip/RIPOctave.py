'''
@author: jcsombria
'''
import os.path
import time

from jsonrpc.JsonRpcServer import JsonRpcServer
from jsonrpc.JsonRpcBuilder import JsonRpcBuilder
from oct2py import octave
from rip.RIPMeta import *
from rip.RIPGeneric import RIPGeneric

builder = JsonRpcBuilder()

class RIPOctave(RIPGeneric):
  '''
  RIP Octave Adapter
  '''

  def __init__(self, name='RIP Octave', description='An implementation of RIP for Octave'):
    '''
    Constructor
    '''
    super().__init__(name, description)

  def set(self, expid, variables, values):
    '''
    Writes one or more variables to the workspace of the current Octave session
    '''
    n = len(variables)
    for i in range(n):
      try:
        octave.push(variables[i], values[i])
      except:
        pass

  def get(self, expid, variables):
    '''
    Retrieve one or more variables from the workspace of the current Octave session
    '''
    toReturn = {}
    n = len(variables)
    for i in range(n):
      name = variables[i]
      try:
        toReturn[name] = octave.pull(name)
      except:
        pass
    return toReturn

  def getValuesToNotify(self):
    return [
      ['time', 'x'],
      [self.sampler.lastTime(), 1]
    ]

#  def eval(self, command):
#    try:
#      result = octave.eval(command)
#    except:
#      pass
#    return result
