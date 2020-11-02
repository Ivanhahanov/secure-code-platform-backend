#!/usr/bin/env python3
import requests
import sys
server = sys.argv[1]
r = requests.get(server).text
print(r)