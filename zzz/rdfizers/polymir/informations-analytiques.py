from sherlockcachemanagement import Cache
import argparse
from lxml import etree
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

#
# ARGS
#

parser = argparse.ArgumentParser()
parser.add_argument("--analytical_data_cache")
parser.add_argument("--dataset_uuid")
parser.add_argument("--mei_cache")
parser.add_argument("--mei_sha1")
parser.add_argument("--mei_uuid")
parser.add_argument("--software_uuid")
parser.add_argument("--ttl")
parser.add_argument("--xml")
args = parser.parse_args()

#
# CACHES
#

mei_cache = Cache(args.mei_cache)
analytical_data_cache = Cache(args.analytical_data_cache)

#
# RDFLIB
#

g = Graph()

sherlock_ns = Namespace("http://data-iremus.huma-num.fr/id/")

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
g.bind("crm", crm_ns)

crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
g.bind("crmdig", crmdig_ns)

polymir_ns = Namespace("http://data-iremus.huma-num.fr/ns/polymir#")
g.bind("polymir", polymir_ns)

she_ns = Namespace("http://data-iremus.huma-num.fr/ns/sherlock#")
g.bind("she", she_ns)

#
# SHERLOCK DATA
#

E55 = {
    "CN": "184b74d9-3452-42f1-963b-40d820021dfc",
    "EN": "0bbe0556-1ac9-4ef8-b449-23e834dcc2b2",
    "NN": "14e52704-1322-4338-92a5-2b866c856d1f",
    "PN": "c9289aed-0ee9-43fa-bb67-699b9346d122",
    "SU": "791d8d87-9eb0-43f5-ae34-3f2da8ea40cb",
}

#
# GO
#

root = etree.parse(args.xml).getroot()
for pitch_coll in root:
    for analyzed_pitch in pitch_coll:
        # MEI (id, offset, pitch)
        mei_element_uuid = mei_cache.get_uuid([args.mei_sha1, "xml:id", analyzed_pitch.attrib["id"], "uuid"])
        g.add((URIRef(mei_element_uuid), she_ns["sheP_MEI_pitch"], Literal(analyzed_pitch.attrib["pitch"])))
        g.add((URIRef(mei_element_uuid), she_ns["sheP_MEI_offset"], Literal(analyzed_pitch.attrib["offset"], datatype=XSD.float)))

        # ANNOTATION
        analyzed_pitch_uuid = analytical_data_cache.get_uuid([analyzed_pitch.attrib["id"], analyzed_pitch.attrib["offset"]], True)
        s = URIRef(sherlock_ns[analyzed_pitch_uuid])
        g.add((URIRef(args.dataset_uuid), crm_ns["P106_is_composed_of"], s))
        g.add((s, RDF.type, URIRef(crm_ns["E13_Attribute_Assignment"])))
        g.add((s, RDF.type, URIRef(crmdig_ns["D1_Digital_Object"])))
        g.add((s, URIRef(crm_ns["P14_carried_out_by"]), URIRef(args.software_uuid)))
        g.add((s, URIRef(crm_ns["P177_assigned_property_type"]), URIRef(E55[analyzed_pitch.attrib["pitchType"]])))
        g.add((s, URIRef(polymir_ns["analyticalDivisions"]), Literal(analyzed_pitch.attrib["analyticalDivisions"], datatype=XSD.integer)))
        g.add((s, URIRef(polymir_ns["probability"]), Literal(analyzed_pitch.attrib["probability"], datatype=XSD.float)))

#
# BYE
#

analytical_data_cache.bye()
g.serialize(destination=args.ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")
