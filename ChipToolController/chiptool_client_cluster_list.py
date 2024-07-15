from environment import Environment
import subprocess
import re
import json
from cluster import Cluster
from command_executor import CommandExecutor

class ChipToolClientClusterList:
  def __init__(self, env, executor, cluster_dic):
    self._env = env
    self._executor = executor
    self._cluster_dic = cluster_dic
    self._important_log = []
    self._pattern_header_client_clusters = r'CHIP:TOO:.*ClientList: ([0-9]+) entries'
    self._pattern_client_cluster = r'CHIP:TOO: .*\[([0-9]+)\]: *([0-9]+)'

  def add_important_log(self, line):
    self._important_log.append(line)

  def get_important_log(self):
    return self._important_log

  def get_attrib_in_get_list(self, lines, index):
    line = lines[index]
    m = re.search(self._pattern_header_client_clusters, line)
    client_clusters = []
    if m:
      number_of_client_clusters = int(m.group(1))
      print(f'number_of_client_clusters: {number_of_client_clusters}')
      for i in range(number_of_client_clusters):
        m2 = re.search(self._pattern_client_cluster, lines[index + i + 1])
        if m2:
          cluster_id = int(m2.group(2))
          cluster = {
            'index': int(m2.group(1)), 
            'client_cluster_id': cluster_id, 
            'client_cluster_name': self._cluster_dic.id_to_name(cluster_id)
          }
          client_clusters.append(cluster)
        else:
          return None, None, False
      return 'client_clusters', client_clusters, False
    return None, None, False


  def get_list(self, node_id, endpoint_id):
    result = {
      'success': False, 
      'client_clusters': [], 
      'error': ''
    } 
    raw = ''
    try:
        commands = [
          f'chip-tool', f'descriptor', f'read', f'client-list', f'{node_id}', f'{endpoint_id}'
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
        if len(result['client_clusters']) > 0:
            result['success'] = True
            self._env.set_client_cluster_list(node_id, endpoint_id, result['client_clusters'])
            return result, raw
        else:
            result['success'] = False
            result['error'] = 'no client_cluster'
            return result, raw
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        return result, raw


if __name__ == '__main__':
  env = Environment()
  executor = CommandExecutor()
  cluster_dic = Cluster()
  ct = ChipToolClientClusterList(env, executor, cluster_dic)
  ret, raw = ct.get_list(1234, 1)
  print(ret)
  print(json.dumps(ret, indent=4, ensure_ascii=False))
  print(ct.get_important_log())

