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
        files = os.listdir(path)
        for file in files:
            if file[-4:] == '.xml':
                print(os.path.join(path, file))
                json_data = self.load_xml_to_json(os.path.join(path, file))
                print(json.dumps(json_data, indent=4, ensure_ascii=False))
        self.json_data = json_data
    except FileNotFoundError:
        print(f"The directory '{path}' or '{file}' does not exist.")
    except PermissionError:
        print(f"Permission denied to access the directory '{directory}'.")

  def load_xml_to_json(self, path):
    tree = ET.parse(path)
    root = tree.getroot()
    cluster = {
      'id': root.attrib['id'], 
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
              'id': sub_child.attrib.get('id'),
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

if __name__ == '__main__':
  cluster = Cluster()

