'''
@author: Amine
'''
from rip.RIPGeneric import RIPGeneric

class RIPRedPitaya(RIPGeneric):
  '''
  RIP Implementation for Red Pitaya
  '''

  def __init__(self, name='RedPitaya', description='An implementation of RIP to control Red Pitaya', authors='Amine', keywords='Red Pitaya'):
    '''
    Constructor
    '''
    super().__init__(name, description, authors, keywords)

    self.readables.append({
        'name':'x',
        'description':'Testing readable variable',
        'type':'float',
        'min':'-Inf',
        'max':'Inf',
        'precision':'0'
    })
    self.writables.append({
        'name':'x',
        'description':'Testing writable variable',
        'type':'float',
        'min':'-Inf',
        'max':'Inf',
        'precision':'0'
    })

  def set(self, expid, variables, values):
    '''
    Writes one or more variables to the workspace of the current session
    '''
    # TO DO: do something with variables and values
    pass

  def get(self, expid, variables):
    '''
    Retrieve one or more variables from the workspace of the current session
    '''
    # TO DO: do something with variables and values
    toReturn = {}
    return toReturn

  def getValuesToNotify(self):
    return [
      ['time', 'x'],
      [self.sampler.lastTime(), 1]
    ]
