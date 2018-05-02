#!/usr/bin/env python3

"""
Puppet client
* PuppetCA
* PuppetDB

From: https://gist.github.com/jessereynolds/b666a48674908b2c2fbeac447f6c4c0b
"""

from .puppetbase import PuppetBaseAPI
from .puppetca import PuppetCa, PuppetCaException
from .puppetdb import PuppetDb

from .puppetcacli import PuppetCaCli, PuppetCaCliException
