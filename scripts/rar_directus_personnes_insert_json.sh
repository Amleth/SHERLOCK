mkdir -p ./temp/referentiel_ancien_regime/directus/personnes/
python3 ./directus/referentiel_ancien_regime/personnes_insert_json.py \
    --json_concepts "./temp/referentiel_ancien_regime/directus/personnes/skos_to_json_concepts.json" \
    --json_index "./temp/referentiel_ancien_regime/directus/personnes/skos_to_json_index.json"