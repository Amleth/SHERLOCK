rm -rf out
mkdir out
touch cache_personnes.yaml
python3 personnes.py\
    --inputrdf ./sources/thesaurus_personnes.rdf\
    --outputttl ./out/personnes.ttl\
    --corpus_cache faux_cache_corpus.yaml\