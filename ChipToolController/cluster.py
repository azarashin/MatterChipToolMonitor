from environment import Environment
import os
import xml.etree.ElementTree as ET
import json

class Cluster:
  def __init__(self):
    self._env = Environment()
    try:
        path = os.path.join(self._env.path_to_connectedhomeip, 'data_model/1.3/clusters')
        print(path)
        self.clusters = []
        files = os.listdir(path)
        for file in files:
            if file[-4:] == '.xml':
#                print(os.path.join(path, file))
                json_data = self.load_xml_to_json(os.path.join(path, file))
#                print(json.dumps(json_data, indent=4, ensure_ascii=False))
                if json_data and json_data['id'] is not None and json_data['id'] != '':
                    self.clusters.append(json_data)
    except FileNotFoundError:
        print(f"The directory '{path}' or '{file}' does not exist.")
    except PermissionError:
        print(f"Permission denied to access the directory '{directory}'.")

  def get_name(self, id):
#    for t in self.clusters:
#      print((t['id'], id, t['name']))
    targets = [d for d in self.clusters if d['id'] == int(id, 16)]
    if len(targets) > 0:
      return targets[0]['name']
    return None

  def load_xml_to_json(self, path):
    tree = ET.parse(path)
    root = tree.getroot()
    id = root.attrib['id']
    if id == '':
      return None
    cluster = {
      'id': int(id[2:], 16), 
      'name': root.attrib['name'], 
      'revision': root.attrib['revision'], 
      'classification': None, 
      'cluster_ids': [], 
      'features': [], 
      'attributes': [], 
      'commands': [],
      'events': []
    }
    for child in root:
      if child.tag == 'classification':
        cluster['classification'] = {
          'hierarchy': child.attrib['hierarchy'], 
          'role': child.attrib['role'], 
          'pics_code': child.attrib['picsCode'], 
          'scope': child.attrib.get('scope')
        }
      if child.tag == 'clusterIds':
        for sub_child in child:
          if sub_child.tag == 'clusterId': 
            cluster_element = {
              'id': int(sub_child.attrib.get('id')[2:], 16),
              'name': sub_child.attrib.get('name'),
            }
            cluster['cluster_ids'].append(cluster_element)

      if child.tag == 'commands':
        for sub_child in child:
          if sub_child.tag == 'command': 
            command = {
              'id': sub_child.attrib['id'],
              'name': sub_child.attrib['name'],
              'direction': sub_child.attrib.get('direction'),
              'response': sub_child.attrib.get('response')
            }
            cluster['commands'].append(command)

      if child.tag == 'events':
        for sub_child in child:
          if sub_child.tag == 'event': 
            event = {
              'id': sub_child.attrib['id'],
              'name': sub_child.attrib['name'],
              'priority': sub_child.attrib.get('priority')
            }
            cluster['events'].append(event)

    return cluster

  def id_to_name(self, id):
    targets = [d for d in self.clusters if d['id'] == id]
    if len(targets) > 0:
      return targets[0]['name']
    return None

if __name__ == '__main__':
  cluster = Cluster()

