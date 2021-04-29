import argparse
from lxml import etree
from sherlockizemeifn import go

parser = argparse.ArgumentParser()
parser.add_argument("--cache")
parser.add_argument("--file")
parser.add_argument("--sha1")
parser.add_argument("--ttl")
args = parser.parse_args()

root = etree.parse(args.file).getroot()

go(cachefile=args.cache, root=root, sha1=args.sha1, ttl=args.ttl)
