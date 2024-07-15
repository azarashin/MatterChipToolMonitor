from environment import Environment
import os
import xml.etree.ElementTree as ET
import json

class DeviceType:
  def __init__(self):
    self._env = Environment()
    try:
#        path = os.path.join(self._env.path_to_connectedhomeip, 'data_model/1.3/clusters')
        path = os.path.join(self._env.path_to_connectedhomeip, 'data_model/1.3/device_types')
        print(path)
        self.device_types = []
        files = os.listdir(path)
        for file in files:
            if file[-4:] == '.xml':
                print(os.path.join(path, file))
                json_data = self.load_xml_to_json(os.path.join(path, file))
                if json_data:
                    self.device_types.append(json_data)
#                    if json_data['id'] is not None and json_data['id'] != '':
#                        print(json.dumps(json_data, indent=4, ensure_ascii=False))
    except FileNotFoundError:
        print(f"The directory '{path}' or '{file}' does not exist.")
    except PermissionError:
        print(f"Permission denied to access the directory '{directory}'.")

  def load_xml_to_json(self, path):
    tree = ET.parse(path)
    root = tree.getroot()
    if root.attrib['id'] == '':
      return None
    data_type = {
      'id': int(root.attrib['id'][2:], 16), 
      'name': root.attrib['name'], 
      'revision': root.attrib['revision'], 
      'classification': None, 
      'clusters': []
    }
    for child in root:
      if child.tag == 'classification':
        data_type['classification'] = {
          'class_type': child.attrib['class'], 
          'scope': child.attrib['scope']
        }
      if child.tag == 'clusters':
        for sub_child in child:
          if sub_child.tag == 'cluster': 
            cluster = {
              'id': int(sub_child.attrib['id'][2:], 16),
              'name': sub_child.attrib['name'],
              'side': sub_child.attrib['side']
            }
            data_type['clusters'].append(cluster)
    return data_type

  def id_to_name(self, id):
    targets = [d for d in self.device_types if d['id'] == id]
    if len(targets) > 0:
      return targets[0]['name']
    return None

if __name__ == '__main__':
  dt = DeviceType()

