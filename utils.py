import os
from collections import namedtuple

def makedir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

task = namedtuple('task', [
    'action',
    'args',
    'take_screenshot',
    'screenshot_name',
    'threshold'
    ])


