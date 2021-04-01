mkdir -p $DIR/caches/polymir
for f in $(ls $DIR/sources/polymir/)
do
    f=$DIR/sources/polymir/$f
    python3 $DIR/rdfizers/polymir/informations-analytiques.py \
        --analytical_data_cache $DIR/caches/polymir/$SHA1.yaml \
        --dataset_uuid "de48731c-b714-464e-a7ae-bb93ce9bfba7" \
        --mei_cache $DIR/caches/mei/$SHA1.yaml \
        --mei_sha1 $SHA1 \
        --mei_uuid $MEI_UUID \
        --software_uuid "a3e99813-d460-4c04-a56c-dc9c11323e92" \
        --ttl $DIR/out/polymir/mei-$SHA1---software-a3e99813-d460-4c04-a56c-dc9c11323e92.ttl \
        --xml $f
done