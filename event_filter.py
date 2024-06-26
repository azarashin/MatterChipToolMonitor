import datetime

class EventFilter:
    def __init__(self):
        self._keys = [
            'cpu_start: Project name:', 
            'cpu_start: Compile time', 
            'chip[SVR]: https://project-chip.github.io/connectedhomeip/qrcode.html?data=', 
            'chip[SVR]: Manual pairing code: '

        ]

    def is_top(self, raw):
        return (raw.find('ets') == 0)


    def filter(self, raw):
        dt = datetime.datetime.now()
        dtstr = dt.strftime('%Y/%m/%d-%H:%M:%S')
        for key in self._keys:
            if key in raw:
                return f'{dtstr}: {raw}'

        return None