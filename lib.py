import os
import json
from datetime import datetime

def parse_datetime(datetime_string):
    return datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%SZ')


def readj(filename):
    with open(filename, "r") as f:
        return json.load(f)


def make_parents(filename, dir=False):
    base = filename if dir else os.path.dirname(filename)
    if base and not os.path.exists(base):
        os.makedirs(base)
