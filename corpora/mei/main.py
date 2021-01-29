import argparse
from lxml import etree
import os
from pathlib import Path
from pathlib import PurePath
from pprint import pprint
from rdflib import DCTERMS, RDF, RDFS, Graph, Literal, Literal as l, Namespace, URIRef, URIRef as u, XSD
import re
import sys
import uuid

#
# ARGS
#

parser = argparse.ArgumentParser()
parser.add_argument("--mei_cache")
parser.add_argument("--mei_file")
parser.add_argument("--mei_sha1")
parser.add_argument("--ttl")
args = parser.parse_args()

#
# CACHE
#

sys.path.append(str(Path(".").absolute().parent.parent))
from Cache import Cache  # nopep8

mei_cache = Cache(args.mei_cache)

#
# RDFLIB
#

g = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
polymir_ns = Namespace("http://data-iremus.huma-num.fr/ns/polymir#")
sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
she_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")
sherlock_ns = Namespace("http://data-iremus.huma-num.fr/id/")

g.bind("crm", crm_ns)
g.bind("crmdig", crmdig_ns)
g.bind("dcterms", DCTERMS)
g.bind("polymir", polymir_ns)
g.bind("sdt", sdt_ns)
g.bind("she", she_ns)

#
# HELPERS
#

a = RDF.type


def crm(x):
    return URIRef(crm_ns[x])


def dig(x):
    return URIRef(crmdig_ns[x])


def she(x):
    return URIRef(she_ns[x])


def t(s, p, o):
    g.add((s, p, o))

#
# PARSE
#


mei_ns = {"tei": "http://www.music-encoding.org/ns/mei"}
xml_ns = {"xml": "http://www.w3.org/XML/1998/namespace"}

root = etree.parse(args.mei_file).getroot()

file_uuid = u(mei_cache.get_uuid([args.mei_sha1, "uuid"]))
t(file_uuid, a, dig("D1_Digital_Object"))
t(file_uuid, a, crm("E31_Document"))
t(file_uuid, crm("P2_has_type"), u("bf9dce29-8123-4e8e-b24d-0c7f134bbc8e"))  # Partition MEI
t(file_uuid, DCTERMS["format"], l("application/vnd.mei+xml"))

# P1 fichier SHERLOCK
P1_file_url_uri = u(mei_cache.get_uuid([args.mei_sha1, "P1_file_url_uuid"]))
t(file_uuid, crm("P1_is_identified_by"), P1_file_url_uri)
t(P1_file_url_uri, a, crm("E42_Identifier"))
t(P1_file_url_uri, crm("P2_has_type"), u("219fd53d-cdf2-4174-8d71-6d12bdd24016"))
t(P1_file_url_uri, RDFS.label, l("http://data-iremus.huma-num.fr/files/" + args.mei_sha1 + ".mei"))

# P1 SHA1
P1_file_sha1_uri = u(mei_cache.get_uuid([args.mei_sha1, "P1_file_sha1_uuid"]))
t(file_uuid, crm("P1_is_identified_by"), P1_file_sha1_uri)
t(P1_file_sha1_uri, a, crm("E42_Identifier"))
t(P1_file_sha1_uri, crm("P2_has_type"), u("01de41ec-850f-473b-bd7f-268a18afc6a3"))
t(P1_file_sha1_uri, RDFS.label, l(args.mei_sha1))

# On recense tout ce qui a un xml:id
for e in root.xpath("//*"):
    xmlida = "{" + xml_ns["xml"] + "}id"
    if xmlida in e.attrib:
        xmlid_uuid = u(mei_cache.get_uuid([args.mei_sha1, "xml:id", l(e.attrib[xmlida])], True))
        t(xmlid_uuid, RDF.type, dig("D35_Area"))
        t(xmlid_uuid, she("sheP_MEI_Element"), l(etree.QName(e.tag).localname))
        print(l(etree.QName(e.tag).localname))
        # TODO : le xml:id en E42

#
# BYE
#

g.serialize(destination=args.ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
mei_cache.bye()
