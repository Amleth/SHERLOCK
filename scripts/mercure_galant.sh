mkdir -p ./out/mercure_galant/
mkdir -p ./caches/mercure_galant/
python3 ./rdfizers/mercure_galant/main.py \
    --tei "./mercure-galant/xml" \
    --output_ttl "./out/mercure_galant/corpus.ttl" \
    --corpus_cache "./caches/mercure_galant/cache_corpus.yaml"
