import argparse
from lxml import etree
from pathlib import Path
from rdflib import Graph, Namespace
import sys

#
# ARGS
#

parser = argparse.ArgumentParser()
parser.add_argument("--mei_cache")
parser.add_argument("--analytical_data_cache")
parser.add_argument("--mei_sha1")
parser.add_argument("--dataset_uuid")
parser.add_argument("--xml")
parser.add_argument("--ttl")
args = parser.parse_args()

#
# CACHES
#

sys.path.append(str(Path(".").absolute()))
from Cache import Cache  # nopep8

mei_cache = Cache(args.mei_cache)
analytical_data_cache = Cache(args.analytical_data_cache)

#
# RDFLIB
#

g = Graph()

polymir_ns = Namespace("http://data-iremus.huma-num.fr/ns/polymir#")
g.bind("polymir", polymir_ns)

crm_ns = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
g.bind("crm", crm_ns)

crmdig_ns = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
g.bind("crmdig", crmdig_ns)

sherlock_ns = Namespace("http://data-iremus.huma-num.fr/id/")

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
        pass
#         analyzed_pitch_uuid = get_uuid([analyzed_pitch.attrib["id"], analyzed_pitch.attrib["offset"]])
#         s = URIRef(sherlock_ns[analyzed_pitch_uuid])
#         g.add((s, RDF.type, URIRef(crm_ns["E13_Attribute_Assignment"])))
#         g.add((s, URIRef(crm_ns["P14_carried_out_by"]), URIRef(args.dataset_uuid)))
#         # g.add((s, RDF.type, URIRef(polymir_ns['AnalyzedPitch'])))
#         # g.add((s, URIRef(polymir_ns['pitchType']), URIRef(E55[analyzed_pitch.attrib["pitchType"]])))


# #
# # BYE
# #

# print(g.serialize(format="turtle", base="http://data-iremus.huma-num.fr/id/").decode("UTF8"))
# g.serialize(destination=args.ttl, format="turtle", base="http://data-iremus.huma-num.fr/id/")

analytical_data_cache.bye()
