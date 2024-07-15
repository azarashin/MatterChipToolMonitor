import os
import json
import datetime
import getpass

class Environment:
    def __init__(self):
        self._path = '.env'
        is_file = os.path.isfile(self._path)
        if is_file:
            self.json_string = open(self._path).read()
            self.json_data = json.loads(self.json_string)
            self.wifi_ssid = self.json_data['wifi_ssid']
            self.wifi_pass = self.json_data['wifi_pass']
            self.path_to_connectedhomeip = self.json_data['path_to_connectedhomeip']
            self.device_list = self.json_data['device_list']
        else:
            self.wifi_ssid = input('WiFi SSID: ')
            self.wifi_pass = getpass.getpass('WiFi password: ')
            self.path_to_connectedhomeip = ('Path to connectedhomeip')
            self.json_data = {
                'wifi_ssid': self.wifi_ssid, 
                'wifi_pass': self.wifi_pass, 
                'path_to_connectedhomeip': self.path_to_connectedhomeip,
                'device_list': []
            }
            self.json_string = json.dumps(self.json_data, sort_keys=True, indent=4)
            open(self._path, 'w').write(self.json_string)

    def __str__(self):
        return  self.json_string

    def add_device(self, device):
        if not 'mac' in device:
            print('FATAL: failed to add new device.')
            return False
        self.json_data['device_list'] = [d for d in self.json_data['device_list'] if d.get('mac') != device['mac']]
        self.json_data['device_list'].append(device)
        self.json_string = json.dumps(self.json_data, sort_keys=True, indent=4)
        open(self._path, 'w').write(self.json_string)

    def datetime_str(self):
        dt = datetime.datetime.now()
        return dt.strftime('%Y%m%d_%H%M%S')
    

if __name__ == '__main__':
  env = Environment()
  print(env)
