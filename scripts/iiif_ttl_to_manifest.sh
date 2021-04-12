mkdir -p ./out/iiif/manifestes
python3 ./rdfizers/iiif/ttl_to_manifest.py \
  --collection_id "40CM" \
  --input_ttl "./out/iiif/40CM.ttl" \
  --output_json "./out/iiif/manifestes/40CM.json" \
  --images "./sources/iiif/40CM/images"