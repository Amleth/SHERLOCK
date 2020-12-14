rm -rf out
mkdir out
touch cache_personnes.yaml
python3 personnes.py\
    --rdf ./sources/thesaurus_personnes.rdf\
    --ttl ./out/personnes.ttl\