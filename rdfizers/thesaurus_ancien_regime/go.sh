clear
rm -rf out
mkdir out
touch cache_personnes.yaml
# python3 personnes.py\
#     --inputrdf ./sources/thesaurus_personnes.rdf\
#     --outputttl ./out/personnes.ttl\
#     --corpus_cache faux_cache_corpus.yaml\
# python3 institutions.py\
#     --inputrdf sources/thesaurus_institutions.rdf\
#     --outputttl out/institutions.ttl\
#     --cache_institutions cache_institutions.yaml\
#     --cache_corpus ../mercure_galant/cache_corpus.yaml
python3 lieux.py\
    --inputrdf sources/thesaurus_lieux.rdf\
    --outputttl out/lieux.ttl\
    --cache_lieux cache_lieux.yaml\
    --cache_corpus ../mercure_galant/cache_corpus.yaml
