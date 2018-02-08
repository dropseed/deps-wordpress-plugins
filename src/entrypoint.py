import os

from collect import collect
from act import act


RUN_AS = os.getenv('RUN_AS')

if RUN_AS == 'collector':
    collect()
elif RUN_AS == 'actor':
    act()
