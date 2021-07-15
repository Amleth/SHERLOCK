mkdir -p ./temp/referentiel_ancien_regime/directus/personnes/
python3 ./directus/referentiel_ancien_regime/directus_to_ttl.py \
    --json "./temp/referentiel_ancien_regime/directus/personnes/directus_export_personnes.json" \
    --ttl "./out/referentiel_ancien_regime/referentiel_personnes.ttl"