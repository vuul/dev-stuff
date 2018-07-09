#!/usr/bin/env python

__author__ = 'ldoucett'

import os
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'app_config.yaml')
with open(CONFIG_FILE, 'rb') as f:
  settings = yaml.safe_load(f)
