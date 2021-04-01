mkdir -p ./out/iiif
mkdir -p ./caches/iiif
python3 ./rdfizers/iiif/40CM_coll_iiif.py --collection_id "40CM" --iiif_excel_coll "./sources/iiif/40CM/40CM.xlsx" --iiif_excel_index "./sources/iiif/collections.xlsx" --output_ttl "./out/iiif/40CM.ttl" --cache_40CM "./caches/iiif/40CM.yaml"