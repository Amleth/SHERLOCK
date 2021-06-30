mkdir -p ./temp/referentiel_ancien_regime/directus/personnes/

python3 ./directus/referentiel_ancien_regime/personnes_skos_to_json.py \
    --skos "./sources/referentiel_ancien_regime/thesaurus_personnes.rdf" \
    --cache_corpus "./caches/mercure_galant/cache_corpus.yaml" \
    --cache_personnes "./caches/referentiel_ancien_regime/cache_personnes.yaml" \
    --json_concepts "./temp/referentiel_ancien_regime/directus/personnes/skos_to_json_concepts.json" \
    --json_index "./temp/referentiel_ancien_regime/directus/personnes/skos_to_json_index.json"