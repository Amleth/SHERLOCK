python ./rdfizers/referentiel_ancien_regime/congregations.py \
    --input_rdf "./sources/referentiel_ancien_regime/thesaurus_congregations.rdf" \
    --output_ttl "./out/referentiel_ancien_regime/congregations.ttl" \
    --cache_corpus "./caches/mercure_galant/cache_corpus.yaml" \
    --cache_congregations "./caches/ancien_regime/cache_congregations.yaml" \
    --cache_lieux_uuid "./out/referentiel_ancien_regime/lieux_label_uuid.yaml" \
    --situation_geo "./sources/referentiel_ancien_regime/congregations_sheP_situation_géohistorique.txt"
