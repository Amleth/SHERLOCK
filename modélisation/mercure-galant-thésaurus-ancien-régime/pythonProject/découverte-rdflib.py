from rdflib import Graph, Literal, Namespace, RDFS, URIRef

g = Graph()
iremus_ns = Namespace("http://data-iremus.huma-num.fr/id/")
g.bind("iremus", iremus_ns)

s = URIRef(iremus_ns["1269f40f-a960-4c94-aa8d-bff42414ad89"])
p = URIRef(RDFS.label)
o = Literal("Blip et blop")

g.add((s, p, o))

turtle = g.serialize(format="turtle").decode("utf-8")
print(turtle)