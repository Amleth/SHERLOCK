mkdir -p ./out/corpora_icono/MGE
mkdir -p ./caches/corpora_icono/MGE
python3 ./rdfizers/corpora_icono/main.py \
 --collection_id "MGE" \
 --excel_coll "./sources/corpora_icono/MGE/MGE.xlsx" \
 --excel_index "./sources/corpora_icono/collections.xlsx" \
 --output_ttl "./out/corpora_icono/MGE/MGE.ttl" \
 --cache_gravures "./caches/corpora_icono/MGE/MGE.yaml" \
 --cache_corpus "./caches/mercure_galant/cache_corpus.yaml" \
 --cache_personnes "./caches/referentiel_ancien_regime/cache_personnes.yaml" \
 --cache_lieux "./caches/referentiel_ancien_regime/cache_lieux.yaml" \
 --cache_vocab_gravures "./caches/corpora_icono/MGE/vocabulaire_gravures.yaml"