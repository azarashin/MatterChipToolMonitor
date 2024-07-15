from environment import Environment
import subprocess
import re
import json
from cluster import Cluster
from command_executor import CommandExecutor

class ChipToolDeviceList:
  def __init__(self, env, executor):
    self._env = env
    self._executor = executor
    self._cluster = Cluster()
    self._important_log = []
    self._pattern_header_endpoints = r'CHIP:TOO:   PartsList: ([0-9]+) entries'
    self._pattern_endpoint = r'CHIP:TOO: .*\[([0-9]+)\]: *([0-9]+)'

  def add_important_log(self, line):
    self._important_log.append(line)

  def get_important_log(self):
    return self._important_log

  def get_attrib_in_get_list(self, lines, index):
    line = lines[index]
    m = re.search(self._pattern_header_endpoints, line)
    endpoints = []
    if m:
      number_of_endpoints = int(m.group(1))
      print(f'number_of_endpoints: {number_of_endpoints}')
      for i in range(number_of_endpoints):
        m2 = re.search(self._pattern_endpoint, lines[index + i + 1])
        if m2:
          endpoints.append({'index': int(m2.group(1)), 'endpoint_id': int(m2.group(2))})
        else:
          return None, None, False
      return 'endpoints', endpoints, False
    return None, None, False


  def get_list(self, node_id):
    result = {
      'success': False, 
      'endpoints': [], 
      'error': ''
    } 
    raw = ''
    try:
        commands = [
          f'chip-tool', f'descriptor', f'read', f'parts-list', f'{node_id}', f'0'
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
        if len(result['endpoints']) > 0:
            result['success'] = True
            self._env.set_endpoint_list(node_id, result['endpoints'])
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
  ct = ChipToolDeviceList(env, executor)
  ret, raw = ct.get_list(1234)
  print(ret)
  print(json.dumps(ret, indent=4, ensure_ascii=False))
  print(ct.get_important_log())

