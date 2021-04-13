mkdir -p ./out/iiif
mkdir -p ./caches/iiif
python3 ./rdfizers/iiif/main.py \
 --collection_id "MGE" \
 --iiif_excel_coll "./sources/iiif/MGE/MGE.xlsx" \
 --iiif_excel_index "./sources/iiif/collections.xlsx" \
 --output_ttl "./out/iiif/MGE.ttl" \
 --cache_40CM "./caches/iiif/MGE.yaml"