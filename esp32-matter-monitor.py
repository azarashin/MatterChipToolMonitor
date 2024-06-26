from environment import Environment
from event_filter import EventFilter

import threading
import time
import os

import serial
 
class Esp32MatterMonitor:
    def __init__(self):
        self._env = Environment()
        self._event_filter = EventFilter()
        self._active = False
        self._serial = None
        self.update_logfile()
        self._log_path_raw_last = f'log/raw/last_log.log'
        self._log_path_event_last = f'log/event/last_log.log'

        if(os.path.isfile(self._log_path_raw_last)):
            os.remove(self._log_path_raw_last)
        if(os.path.isfile(self._log_path_event_last)):
            os.remove(self._log_path_event_last)
        print(self._env)

    def update_logfile(self):    
        self._log_path_raw = f'log/raw/{self._env.datetime_str()}.log'
        self._log_path_event = f'log/event/{self._env.datetime_str()}.log'
    def run(self):
        self._thread = threading.Thread(target=self._task)
        self._active = True
        self._thread.start()

    def join(self):
        self._thread.join()
        print('join-term')

    def _task(self):
        buf = b''
        timeout = 1
        self._serial = serial.Serial(self._env.path_to_serial_device,115200,timeout=timeout)
        while self._active:
            line = self._serial.readline()
            if line:
                line = line.decode('utf-8', 'replace')
#            logs = line.split('\n')
#            buf += logs[-1]

#            for line in logs:
                if self._event_filter.is_top(line):
                    self.update_logfile()

                print(line[:-2])
                open(self._log_path_raw, 'a').writelines([line])
                open(self._log_path_raw_last, 'a').writelines([line])
                event_line = self._event_filter.filter(line)
                if event_line:
                    open(self._log_path_event, 'a').writelines([event_line])
                    open(self._log_path_event_last, 'a').writelines([event_line])
        print('close')
        self._serial.close()

    def stop(self):
        print('stop')
        self._active = False


if __name__ == '__main__':
    try:
        monitor = Esp32MatterMonitor()
        monitor.run()
        monitor.join()
    except KeyboardInterrupt:
        monitor.stop()
        time.sleep(2)
