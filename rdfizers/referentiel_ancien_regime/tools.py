def print_orphans():
    q = """
        SELECT DISTINCT ?o
        WHERE {
            ?o <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#Concept> .
            FILTER NOT EXISTS {
                ?s <http://www.w3.org/2004/02/skos/core#narrower> ?o .
            }
        }
        """

    for o in list(g.query(q)):
        print(o)