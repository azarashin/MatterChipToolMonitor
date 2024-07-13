import os
import json
import datetime
import getpass

class Environment:
    def __init__(self):
        path = '.env'
        is_file = os.path.isfile(path)
        if is_file:
            self.json_string = open(path).read()
            self.json_data = json.loads(self.json_string)
            self.wifi_ssid = self.json_data['wifi_ssid']
            self.wifi_pass = self.json_data['wifi_pass']
        else:
            self.wifi_ssid = input('WiFi SSID: ')
            self.wifi_pass = getpass.getpass('WiFi password: ')
            self.json_data = {
                'wifi_ssid': self.wifi_ssid, 
                'wifi_pass': self.wifi_pass, 
            }
            self.json_string = json.dumps(self.json_data, sort_keys=True, indent=4)
            open(path, 'w').write(self.json_string)

    def __str__(self):
        return  self.json_string
    
    def datetime_str(self):
        dt = datetime.datetime.now()
        return dt.strftime('%Y%m%d_%H%M%S')

if __name__ == '__main__':
  env = Environment()
  print(env)
