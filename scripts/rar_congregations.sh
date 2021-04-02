mkdir -p ./out/referentiel_ancien_regime
mkdir -p ./caches/referentiel_ancien_regime
python3 ./rdfizers/referentiel_ancien_regime/congregations.py \
    --input_rdf "./sources/referentiel_ancien_regime/thesaurus_congregations.rdf" \
    --output_ttl "./out/referentiel_ancien_regime/referentiel_congregations.ttl" \
    --cache_corpus "./caches/mercure_galant/cache_corpus.yaml" \
    --cache_congregations "./caches/referentiel_ancien_regime/cache_congregations.yaml" \
    --cache_lieux_uuid "./out/referentiel_ancien_regime/lieux_label_uuid.yaml" \
    --situation_geo "./sources/referentiel_ancien_regime/congregations_sheP_situation_géohistorique.txt"