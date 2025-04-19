import sys
from datetime import datetime


def log(text, inplace=False, breakpoint=False):
    timestamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    if inplace:
        sys.stdout.write(f"\r{timestamp} {text}")
    else:
        if breakpoint is True:
            print(f"\n{timestamp} {text}")
        else:
            print(timestamp, text)
