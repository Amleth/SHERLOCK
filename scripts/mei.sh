SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIR=$SCRIPT_DIR/..

# MEI

mkdir -p $DIR/caches/mei
mkdir -p $DIR/out/mei
mkdir -p $DIR/out/polymir

for f in $(ls $DIR/sources/mei/**/*.mei)
do
    SHA1=$(shasum $f | awk '{print $1}')
    MEI_UUID=$(
        python3 $DIR/rdfizers/mei/main.py \
        --cache $DIR/caches/mei/$SHA1.yaml \
        --file $f \
        --sha1 $SHA1 \
        --ttl $DIR/out/mei/$SHA1.ttl
        )
    echo $MEI_UUID 🍄 $SHA1 🍄 $f
done