# MEI

mkdir -p ./caches/mei

for f in $(ls ./sources/mei/)
do
    f=./sources/mei/$f
    SHA1=$(shasum ./sources/mei/787.mei | awk '{print $1}')
    MEI_UUID=$(python3 ./corpora/mei/main.py \
        --sha1 $SHA1 \
        --cache ./caches/mei/$SHA1.yaml \
        --file $f \
        --ttl ./out/mei/$SHA1.ttl)
done

# POLYMIR

mkdir -p ./caches/polymir
for f in $(ls ./sources/polymir/)
do
    f=./sources/polymir/$f
    python3 ./rdfizers/polymir/informations-analytiques.py \
        --mei_cache ./caches/mei/$SHA1.yaml \
        --analytical_data_cache ./caches/polymir/$SHA1.yaml \
        --mei_sha1 $SHA1 \
        --dataset_uuid $MEI_UUID \
        --xml $f \
        --ttl ./out/polymir/$SHA1.ttl
done