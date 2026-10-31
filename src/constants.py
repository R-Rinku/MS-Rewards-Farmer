import os
from os.path import abspath

USER_DATA_DIR = os.environ.get("EDGE_USER_DATA_DIR", abspath("./data-dir"))
PROFILE_NAME = os.environ.get("EDGE_PROFILE_NAME", "Default")
