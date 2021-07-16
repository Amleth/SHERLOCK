mkdir -p ./temp/referentiel_ancien_regime/directus/indexations/
python3 ./directus/referentiel_ancien_regime/indexations_directus_to_ttl.py \
    --json "./temp/referentiel_ancien_regime/directus/indexations/directus_export_indexations.json" \
    --ttl "./out/referentiel_ancien_regime/indexations.ttl" \
    --cache_corpus "./caches/mercure_galant/cache_corpus.yaml" \
    --cache "./caches/referentiel_ancien_regime/indexations.yaml"
