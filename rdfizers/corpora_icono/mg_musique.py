import argparse
from rdflib import Graph, Namespace, DCTERMS, RDF, RDFS, SKOS, URIRef as u, XSD, Literal as l
from sherlockcachemanagement import Cache

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--dossier_images")
parser.add_argument("--output_ttl")
parser.add_argument("--cache_images")

# Caches
cache_images = Cache(args.cache_images)


