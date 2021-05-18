mkdir -p ./out/corpora_icono/mercure_galant
mkdir -p ./caches/corpora_icono/mercure_galant
python3 ./rdfizers/corpora_icono/main.py \
 --collection_id "mg_estampes" \
 --excel_coll "./sources/corpora_icono/mercure_galant/mg_estampes.xlsx" \
 --excel_index "./sources/corpora_icono/collections.xlsx" \
 --output_ttl "./out/corpora_icono/mercure_galant/mg_estampes.ttl" \
 --cache_images "./caches/corpora_icono/mercure_galant/mg_estampes.yaml" \
 --cache_corpus "./caches/mercure_galant/cache_corpus.yaml" \
 --cache_personnes "./caches/referentiel_ancien_regime/cache_personnes.yaml" \
 --cache_lieux "./caches/referentiel_ancien_regime/cache_lieux.yaml" \
 --cache_vocab_estampes "./caches/corpora_icono/mercure_galant/vocabulaire_estampes.yaml"