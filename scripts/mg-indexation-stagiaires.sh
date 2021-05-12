python3 ./rdfizers/mercure_galant_indexation_stagiaires/main.py \
    --racine "./sources/mercure-galant/indexation-stagiaires/**/*.rtf" \
    --input_txt "./sources/mercure-galant/indexation-stagiaires/" \
    --output_ttl "./out/mercure_galant/indexation_stagiaires.ttl" \
    --cache_personnes "./caches/referentiel_ancien_regime/cache_personnes.yaml" \
    --cache_lieux "./caches/referentiel_ancien_regime/cache_lieux.yaml" \
    --cache_corpus "./caches/mercure_galant/cache_corpus.yaml" \
    --cache_stagiaires "./caches/mercure_galant/cache_stagiaires.yaml" \
    --cache_institutions "./caches/referentiel_ancien_regime/cache_institutions.yaml" \
    --cache_mots_clés "./caches/mercure_galant/cache_mots-clefs.yaml"