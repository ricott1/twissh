# encoding: utf-8

import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from server import create_application

application = create_application('moosh', 6022)