mkdir -p ./out/corpora_icono
mkdir -p ./caches/corpora_icono
python3 ./rdfizers/corpora_icono/main.py \
 --collection_id "40CM" \
 --excel_coll "./sources/corpora_icono/40CM/40CM.xlsx" \
 --excel_index "./sources/corpora_icono/collections.xlsx" \
 --output_ttl "./out/corpora_icono/40CM.ttl" \
 --cache_gravures "./caches/corpora_icono/40CM.yaml"