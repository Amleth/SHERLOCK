python3 ./rdfizers/mercure_galant_indexation_stagiaires/main.py \
    --racine "./sources/mercure-galant/indexation-stagiaires/**/*.rtf" \
    --input_txt "./sources/mercure-galant/indexation-stagiaires/" \
    --output_ttl "./out/referentiel_ancien_regime/indexation_stagiaires.ttl" \
    --cache_personnes "./caches/referentiel_ancien_regime/cache_personnes.yaml" \
    --cache_lieux "./caches/referentiel_ancien_regime/cache_lieux.yaml" \
    --cache_corpus "./caches/mercure_galant/cache_corpus.yaml" \
    --cache_mots_clefs "./caches/mercure_galant/cache_mots_clefs.yaml"