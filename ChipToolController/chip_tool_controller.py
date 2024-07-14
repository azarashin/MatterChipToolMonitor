from environment import Environment
import subprocess
import re

class ChipToolController:
  def __init__(self):
    self._env = Environment()
    self._important_log = []
    self._pattern_wifi = r'CHIP:DL: Found the primary WiFi interface:(.*)'
    self._pattern_mac = r'CHIP:BLE: New device connected: (.*)'
    self._pattern_command_response = r'Received Command Response Data, Endpoint=(.*) Cluster=0x(.*) Command=0x(.*)'
    self._pattern_command_response_status = r'Received Command Response Status for Endpoint=(.*) Cluster=0x(.*) Command=0x(.*) Status=0x(.*)'
    self._pattern_timeout = r'CHIP:TOO: Run command failure:.*CHIP Error 0x00000032: Timeout'

  def add_important_log(self, line):
    self._important_log.append(line)

  def get_important_log(self):
    return self._important_log

  def get_attrib_in_find(self, line):
    m = re.search(self._pattern_wifi, line)
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
      ret = {'end_point':m.group(1), 'cluster':m.group(2).replace('_', ''), 'command':m.group(3).replace('_', '')}
      return 'command_response', ret, True

    m = re.search(self._pattern_command_response_status, line)
    if m:
      ret = {'end_point':m.group(1), 'cluster':m.group(2).replace('_', ''), 'command':m.group(3).replace('_', ''), 'status':m.group(4).replace('_', '')}
      return 'command_response_status', ret, True

    return None, None, False


  def find(self, node_id, pin_code, discriminator):
    result = {
      'success': False, 
      'raw': '', 
      'wifi': '', 
      'mac': '', 
      'command_response': [], 
      'command_response_status': [], 
      'timeout': False, 
      'error': ''
    } 
    try:
        commands = [
          f'chip-tool', f'pairing', f'ble-wifi', f'{node_id}', f'{self._env.wifi_ssid}' , f'{self._env.wifi_pass}', 
          f'{pin_code}' , f'{discriminator}'
        ]
        print(commands)
        pipe = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result['success'] = False
        line = '#'
        while line != '':
            line = pipe.stdout.readline()
            result['raw'] += line
            if 'CHIP:SPT: VerifyOrDie failure' in line:
                result['success'] = False
                result['error'] = 'CHIP:SPT: VerifyOrDie failure' # Maybe this script should run as sudo. 
                return result
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
        if pipe.returncode == 0:
            result['success'] = True
            return result
        else:
            result['success'] = False
            result['error'] = pipe.stderr
            return result
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        return result
    


if __name__ == '__main__':
  ct = ChipToolController()
  ret = ct.find(1234, 20202021, 3840)
  ret['raw'] = 'dummy'
  print(ret)
  print(ct.self._important_log())

