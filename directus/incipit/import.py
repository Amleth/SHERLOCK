import argparse
from iremusdocutils import Ikselesix
import json
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("--xlsx")
parser.add_argument("--json")
args = parser.parse_args()

xlsx = Ikselesix(args.xlsx)
for row in xlsx["Sheet1"]:
    
