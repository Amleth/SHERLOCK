mkdir -p ./out/referentiel_ancien_regime
mkdir -p ./caches/referentiel_ancien_regime
python ./rdfizers/referentiel_ancien_regime/personnes.py \
  --inputrdf "./sources/referentiel_ancien_regime/thesaurus_personnes.rdf" \
  --output_ttl "./out/referentiel_ancien_regime/referentiel_personnes.ttl" \
  --cache_corpus "./caches/mercure_galant/cache_corpus.yaml" \
  --cache_personnes "./caches/referentiel_ancien_regime/cache_personnes.yaml"