from environment import Environment
import subprocess
import re
import json
from cluster import Cluster
from command_executor import CommandExecutor

class ChipToolPairing:
  def __init__(self, env, executor):
    self._env = env
    self._executor = executor
    self._cluster = Cluster()
    self._important_log = []
    self._pattern_wifi = r'CHIP:DL: Found the primary WiFi interface:(.*)'
    self._pattern_mac = r'CHIP:BLE: New device connected: (.*)'
    self._pattern_command_response = r'Received Command Response Data, Endpoint=(.*) Cluster=0x(.*) Command=0x(.*)'
    self._pattern_command_response_status = r'Received Command Response Status for Endpoint=(.*) Cluster=0x(.*) Command=0x(.*) Status=0x(.*)'
    self._pattern_timeout = r'CHIP:TOO: Run command failure:.*CHIP Error 0x00000032: Timeout'
    self._pattern_vend_prod = r'CHIP:SVR: OnReadCommissioningInfo - vendorId=0x(.*) productId=0x(.*)'
    self._pattern_step = r'CHIP:CTL: Performing next commissioning step \'(.*)\''
    self._pattern_invalid_discriminator = r'CHIP:BLE: Skip connection: Device discriminator does not match: ([0-9A-Za-z]+) != ([0-9A-Za-z]+)'

  def is_invalid_discriminator(self, line):
    m = re.search(self._pattern_invalid_discriminator, line)
    if m:
      return m.group(1), m.group(2)
    return None, None

  def add_important_log(self, line):
    self._important_log.append(line)

  def get_important_log(self):
    return self._important_log

  def get_attrib_in_find(self, line):
    m = re.search(self._pattern_step, line)
    if m:
      return 'step', m.group(1), True

    m = re.search(self._pattern_vend_prod, line)
    if m:
      return 'vend_prod', {'vender_id': m.group(1), 'product_id': m.group(2)}, False

    m = re.search(self._pattern_timeout, line)
    if m:
      return 'timeout', True, False

    m = re.search(self._pattern_wifi, line)
    if m:
      return 'wifi', m.group(1), False

    m = re.search(self._pattern_mac, line)
    if m:
      return 'mac', m.group(1), False

    m = re.search(self._pattern_command_response, line)
    if m:
      ret = {'end_point':m.group(1), 'cluster_id':m.group(2).replace('_', ''), 'command':m.group(3).replace('_', '')}
      ret['cluster_name'] = self._cluster.get_name(ret['cluster_id'])
      return 'command_response', ret, True

    m = re.search(self._pattern_command_response_status, line)
    if m:
      ret = {'end_point':m.group(1), 'cluster_id':m.group(2).replace('_', ''), 'command':m.group(3).replace('_', ''), 'status':m.group(4).replace('_', '')}
      ret['cluster_name'] = self._cluster.get_name(ret['cluster_id'])
      return 'command_response_status', ret, True

    return None, None, False

  def find_without_discriminator(self, node_id, pin_code):
    result, raw = self.find(node_id, pin_code, '0000')
    if result['success']:
      return result, raw
    discriminator = result['discriminator']
    if discriminator:
      result, raw = self.find(node_id, pin_code, discriminator)
      return result, raw
    return result, None

  def find(self, node_id, pin_code, discriminator):
    result = {
      'success': False, 
      'wifi': '', 
      'mac': '', 
      'command_response': [], 
      'command_response_status': [], 
      'vend_prod': None, 
      'step': [],
      'timeout': False, 
      'discriminator': None, 
      'node_id': None, 
      'error': ''
    } 
    raw = ''
    try:
        commands = [
          f'chip-tool', f'pairing', f'ble-wifi', f'{node_id}', f'{self._env.wifi_ssid}' , f'{self._env.wifi_pass}', 
          f'{pin_code}' , f'{discriminator}'
        ]
        pipe = self._executor.run(commands, [4, 5, 6, 7])
        result['success'] = False
        line = '#'
        while line != '':
            line = pipe.stdout.readline()
            raw += line
            if 'CHIP:SPT: VerifyOrDie failure' in line:
                result['success'] = False
                result['error'] = 'CHIP:SPT: VerifyOrDie failure' # Maybe this script should run as sudo. 
                return result, None
            correct_discriminator, actual_discriminator = self.is_invalid_discriminator(line)
            if correct_discriminator and actual_discriminator:
                result['success'] = False
                result['error'] = f'Invalid Discriminator. Correct: {correct_discriminator}, Actual: {actual_discriminator}'
                result['discriminator'] = correct_discriminator
                return result, None


            attrib, value, additional = self.get_attrib_in_find(line)
            if attrib:
                if additional:
                    if not attrib in result:
                        result[attrib] = []
                    result[attrib].append(value)
                else:
                    result[attrib] = value
            if line != '':
                print(line, end='')
        print(f'returncode: {pipe.returncode}')
        if result['mac'] != '':
            result['success'] = True
            result['node_id'] = int(node_id)
            result['discriminator'] = discriminator
            self._env.add_device(result)
            return result, raw
        else:
            result['success'] = False
            result['error'] = pipe.stderr
            return result, raw
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        return result, raw
    


if __name__ == '__main__':
  env = Environment()
  executor = CommandExecutor()
  ct = ChipToolPairing(env, executor)
  ret, raw = ct.find(1234, 20202021, 3840)
  print(raw)
  print(json.dumps(ret, indent=4, ensure_ascii=False))
  print(ct.get_important_log())

