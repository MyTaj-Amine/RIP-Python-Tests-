# This file contains the configuration of the RIP server application.
config = {
  # TO DO: The server will listen to host:port
  'server': {
    'host': '127.0.0.1',
    'port': 8080,
  },
  # The 'control' section configures the mapping between the RIP protocol
  # and the actual implementation of the functionality.
  # The 'impl' field should contain the name of the module (.py) and the
  # class that implement the control interface
  'control': {
    'impl_module': 'RIPGeneric',
    #'samling_method':'PeriodicSampler',
    # Also, if the class name is not the same as the module name:
    #'impl_name': 'RIPOctave',
    'info': {
      'name': 'RIP Generic',
      'description': 'A generic implementation of RIP',
      'authors': 'A. My-taj , J. Chacon',
      'keywords': 'Raspberry PI, RIP',
      # Server readable objects
      'readables': [{
        'name': 'time',
        'description': 'Server time in seconds',
        'type': 'float',
        'min': '0',
        'max': 'Inf',
        'precision': '0'
      }, {
        'name': 'Sampling_method',
        'description': 'the sampling method to be applied ',
        'type': 'String',
        'value': 'PeriodicSoD',
        #'value': 'PeriodicSoD',
      },{
        'name': 'Sampling_params',
        'description': 'the sampling parameters to be applied ',
        'type': 'String',
        'params': [{
          'name': 'first_Sampling',
          'description': 'The time in which the first sampling is done',
          'type': 'float',
          'value': '2',
        },{
          'name': 'sampling_period',
          'description': 'the sampling period ',
          'type': 'float',
          'value': '0.5',
        },{
          'name': 'sampling_signal',
          'description': 'A random numbers generator',
          'type': 'float',
          'min': '0',
          'max': '0.999',
          'precision': '0'
      },{
          'name': 'sampling_threshold',
          'description': 'The threshold that determines when to fire the event',
          'type': 'float',
          'value': '2',
        }],
      }],
      # Server writable objects
      'writables': []
    },
  }
}
