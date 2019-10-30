'''
@author: jcsombria
'''
import os.path

from rip.RIPGeneric import RIPGeneric
from rip.matlab.MatlabConnector import CommandBuilder, MatlabConnector

import matlab.engine

class RIPMatlab(RIPGeneric):
  '''
  RIP MATLAB Adapter
  '''

  def __init__(self, info):
    '''
    Constructor
    '''
    super().__init__(info)

    self.matlab = matlab.engine.start_matlab('-desktop')

  def default_info(self):
    '''
    Default metadata.
    '''
    return {
      'name': 'Matlab',
      'description': 'An implementation of RIP to control MATLAB',
      'authors': 'J. Chacon',
      'keywords': 'MATLAB, Raspberry PI',
      'readables': [],
      'writables': [],
    }

  def set(self, expid, variables, values):
    if isinstance(variables, list):
      size = len(variables)
      for i in range(size):
        try:
          name, value = variables[i], values[i]
          self.matlab.workspace[name] = value
        except:
          pass
    else:
      try:
        name, value = variables, values
        self.matlab.workspace[name] = value
      except:
        pass
    self.matlab.set(variables, values)

  def get(self, expid, variables):
    readables = self._getReadables()
    values = []
    for n in variables:
      try:
        if n in readables:
          v = self.matlab.workspace[n]
          values.append(v)
      except:
        values.append('###ERROR###')
    return [variables, values]

  def preGetValuesToNotify(self):
    self.matlab.workspace['time'] = self.sampler.time

  def getValuesToNotify(self, expid=None):
    values = self.get(expid, self._getReadables())
    return values

  def postGetValuesToNotify(self):
    pass
