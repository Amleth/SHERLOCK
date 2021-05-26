mkdir -p ./out/corpora_icono/mercure_galant
mkdir -p ./caches/corpora_icono/mercure_galant
python3 ./rdfizers/corpora_icono/main.py \
 --collection_id "mg_musique" \
 --dossier_coll "./mercure-galant/images" \
 --excel_index "./sources/corpora_icono/collections.xlsx" \
 --output_ttl "./out/corpora_icono/mercure_galant/mg_musique.ttl" \
 --cache_images "./caches/corpora_icono/mercure_galant/mg_musique.yaml" \
 --cache_corpus "./caches/mercure_galant/cache_corpus.yaml"