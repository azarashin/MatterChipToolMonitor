import os
import json
import datetime

class Environment:
    def __init__(self):
        path = '.env'
        is_file = os.path.isfile(path)
        if is_file:
            self.json_string = open(path).read()
            self.json_data = json.loads(self.json_string)
            self.path_to_chip_tool = self.json_data['path_to_chip_tool']
            self.path_to_serial_device = self.json_data['path_to_serial_device']
        else:
            self.path_to_chip_tool = input('full path to chip_tool: ')
            self.path_to_serial_device = input('full path to serial device: ')
            self.json_data = {
                'path_to_chip_tool': self.path_to_chip_tool, 
                'path_to_serial_device': self.path_to_serial_device, 
            }
            self.json_string = json.dumps(self.json_data, sort_keys=True, indent=4)
            open(path, 'w').write(self.json_string)

    def __str__(self):
        return  self.json_string
    
    def datetime_str(self):
        dt = datetime.datetime.now()
        return dt.strftime('%Y%m%d_%H%M%S')
