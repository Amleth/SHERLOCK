from sherlockcachemanagement import Cache
import argparse
from lxml import etree
from rdflib import DCTERMS, RDF, RDFS, Graph, Literal as l, Namespace, URIRef, URIRef as u, XSD

#
# ARGS
#

parser = argparse.ArgumentParser()
parser.add_argument("--cache")
parser.add_argument("--file")
parser.add_argument("--sha1")
parser.add_argument("--ttl")
args = parser.parse_args()

#
# CACHE
#

cache = Cache(args.cache)

#
# RDFLIB
#

g = Graph()

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
g.bind("crm", crm_ns)

crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
g.bind("crmdig", crmdig_ns)

g.bind("dcterms", DCTERMS)

polymir_ns = Namespace("http://data-iremus.huma-num.fr/ns/polymir#")
g.bind("polymir", polymir_ns)

sdt_ns = Namespace("http://data-iremus.huma-num.fr/datatypes/")
g.bind("sdt", sdt_ns)

she_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")
g.bind("she", she_ns)

meiplus_ns = Namespace("http://data-iremus.huma-num.fr/ns/meiplus#")
g.bind("meiplus", meiplus_ns)

#
# HELPERS
#


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return None


def isinteger(value):
    try:
        int(value)
        return True
    except ValueError:
        return None


a = RDF.type


def crm(x):
    return URIRef(crm_ns[x])


def dig(x):
    return URIRef(crmdig_ns[x])


def she(x):
    return URIRef(she_ns[x])


def meiplus(x):
    return URIRef(meiplus_ns[x])


def t(s, p, o):
    g.add((s, p, o))

#
# PARSE
#


mei_ns = {"tei": "http://www.music-encoding.org/ns/mei"}
xml_ns = {"xml": "http://www.w3.org/XML/1998/namespace"}

root = etree.parse(args.file).getroot()

file_uuid = u(cache.get_uuid([args.sha1, "uuid"], True))
t(file_uuid, a, dig("D1_Digital_Object"))
t(file_uuid, a, crm("E31_Document"))
t(file_uuid, crm("P2_has_type"), u("bf9dce29-8123-4e8e-b24d-0c7f134bbc8e"))  # Partition MEI
t(file_uuid, DCTERMS["format"], l("application/vnd.mei+xml"))

# P1 fichier SHERLOCK
P1_file_url_uri = u(cache.get_uuid([args.sha1, "P1_file_url_uuid"], True))
t(file_uuid, crm("P1_is_identified_by"), P1_file_url_uri)
t(P1_file_url_uri, a, crm("E42_Identifier"))
t(P1_file_url_uri, crm("P2_has_type"), u("219fd53d-cdf2-4174-8d71-6d12bdd24016"))
t(P1_file_url_uri, RDFS.label, l("http://data-iremus.huma-num.fr/files/mei/" + args.sha1 + ".mei"))

# P1 SHA1
P1_file_sha1_uri = u(cache.get_uuid([args.sha1, "P1_file_sha1_uuid"], True))
t(file_uuid, crm("P1_is_identified_by"), P1_file_sha1_uri)
t(P1_file_sha1_uri, a, crm("E42_Identifier"))
t(P1_file_sha1_uri, crm("P2_has_type"), u("01de41ec-850f-473b-bd7f-268a18afc6a3"))
t(P1_file_sha1_uri, RDFS.label, l(args.sha1))

# We census everything which has a xml:id
for e in root.xpath("//*"):
    xmlida = "{" + xml_ns["xml"] + "}id"
    if xmlida in e.attrib:
        # MEI element
        xmlid_uuid = u(cache.get_uuid([args.sha1, "xml:id", l(e.attrib[xmlida]), "uuid"], True))
        t(xmlid_uuid, RDF.type, dig("D35_Area"))

        if e.text and e.text.strip() and e.text.strip() != "None":
            t(xmlid_uuid, meiplus("text"), l(e.text.strip()))
        # MEIPLUS
        t(xmlid_uuid, meiplus("element"), l(etree.QName(e.tag).localname))
        for a in e.attrib:
            if a != xmlida:
                o = None
                if isfloat(e.attrib[a]):
                    o = l(int(e.attrib[a]), datatype=XSD.integer)
                elif isfloat(e.attrib[a]):
                    o = l(float(e.attrib[a]), datatype=XSD.float)
                else:
                    o = l(e.attrib[a])
                t(xmlid_uuid, meiplus(a), o)

        # xml:id E42
        e42_uuid = u(cache.get_uuid([args.sha1, "xml:id", l(e.attrib[xmlida]), "e42", "uuid"], True))
        t(xmlid_uuid, crm("P1_is_identified_by"), e42_uuid)
        t(e42_uuid, RDF.type, crm("E42_Identifier"))
        t(e42_uuid, RDFS.label, l(e.attrib[xmlida]))

        # P106 parent element
        if e.getparent() is not None:
            parent_element_uuid = u(cache.get_uuid([args.sha1, "xml:id", l(e.getparent().attrib[xmlida]), "uuid"], True))
            t(parent_element_uuid, crm("P106_is_composed_of"), xmlid_uuid)
        else:
            t(file_uuid, crm("P106_is_composed_of"), xmlid_uuid)

#
# BYE
#

g.serialize(destination=args.ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
cache.bye()

print(file_uuid)
