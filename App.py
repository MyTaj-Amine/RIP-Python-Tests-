import importlib
from HttpServer import HttpServer
from AppConfig import config

def load_control(control):
  module_name = 'rip.%s' % control['impl_module']
  module = importlib.import_module(module_name)
  control_name = control.get('impl_name', control['impl_module'])
  RIPControl = getattr(module, control_name)

  info = config['control']['info']
  return RIPControl(
    info['name'],
    info['description'],
    info['authors'],
    info['keywords'],
  )

if __name__ == "__main__":
  control = load_control(config['control'])

  HttpServer(
    host=config['server']['host'],
    port=config['server']['port'],
    control=control
  ).start(enable_ssl=False)
