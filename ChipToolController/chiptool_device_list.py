from environment import Environment
import subprocess
import re
import json
from cluster import Cluster
from command_executor import CommandExecutor
from device_type import DeviceType

class ChipToolDeviceList:
  def __init__(self, env, executor, device_dic):
    self._env = env
    self._executor = executor
    self._cluster = Cluster()
    self._important_log = []
    self._device_dic = device_dic
    self._pattern_header_device_types = r'CHIP:TOO:.*DeviceTypeList: ([0-9]+) entries'
    self._pattern_index = r'CHIP:TOO:.*\[([0-9]+)\]:'
    self._pattern_id = r'CHIP:TOO:.*DeviceType: ([0-9]+)'
    self._pattern_revision = r'CHIP:TOO:.*Revision: ([0-9]+)'

  def add_important_log(self, line):
    self._important_log.append(line)

  def get_important_log(self):
    return self._important_log

  def get_attrib_in_get_list(self, lines, index):
    line = lines[index]
    m = re.search(self._pattern_header_device_types, line)
    device_types = []
    if m:
      number_of_device_types = int(m.group(1))
      print(f'number_of_device_types: {number_of_device_types}')
      for i in range(number_of_device_types):
        m1 = re.search(self._pattern_index, lines[index + i * 4 + 1])
        m2 = re.search(self._pattern_id, lines[index + i * 4 + 2])
        m3 = re.search(self._pattern_revision, lines[index + i * 4 + 3])
        if m1 and m2 and m3:
          device_type_id = int(m2.group(1))
          device = {
            'index': int(m1.group(1)), 
            'device_type_id': device_type_id, 
            'revision': int(m3.group(1)), 
            'device_name': self._device_dic.id_to_name(device_type_id)
          }
          device_types.append(device)
        else:
          return None, None, False
      return 'device_types', device_types, False
    return None, None, False


  def get_list(self, node_id, endpoint_id):
    result = {
      'success': False, 
      'device_types': [], 
      'error': ''
    } 
    raw = ''
    try:
        commands = [
          f'chip-tool', f'descriptor', f'read', f'device-type-list', f'{node_id}', f'{endpoint_id}'
        ]
        pipe = self._executor.run(commands)
        result['success'] = False
        line = '#'
        lines = []
        while line != '':
            line = pipe.stdout.readline()
            lines.append(line)
            raw += line
            if line != '':
                print(line, end='')
        for i in range(len(lines)):
            line = lines[i]
            if 'CHIP:SPT: VerifyOrDie failure' in line:
                result['success'] = False
                result['error'] = 'CHIP:SPT: VerifyOrDie failure' # Maybe this script should run as sudo. 
                return result, None
            if 'CHIP:TOO: Run command failure:' in line:
                result['success'] = False
                result['error'] = 'CHIP:TOO: Run command failure:' # not found NodeId
                return result, None

            attrib, value, additional = self.get_attrib_in_get_list(lines, i)
            if attrib:
                if additional:
                    if not attrib in result:
                        result[attrib] = []
                    result[attrib].append(value)
                else:
                    result[attrib] = value
        print(f'returncode: {pipe.returncode}')
        if len(result['device_types']) > 0:
            result['success'] = True
            self._env.set_device_type_list(node_id, endpoint_id, result['device_types'])
            return result, raw
        else:
            result['success'] = False
            result['error'] = 'no endpoint'
            return result, raw
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        return result, raw


if __name__ == '__main__':
  env = Environment()
  executor = CommandExecutor()
  dt = DeviceType()
  ct = ChipToolDeviceList(env, executor, dt)
  ret, raw = ct.get_list(1234, 1)
  print(ret)
  print(json.dumps(ret, indent=4, ensure_ascii=False))
  print(ct.get_important_log())

