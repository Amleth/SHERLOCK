SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIR=$SCRIPT_DIR/..

# MEI

rm -rf $DIR/out/mei
rm -rf $DIR/out/files/mei

mkdir -p $DIR/caches/mei
mkdir -p $DIR/out/mei
mkdir -p $DIR/out/polymir
mkdir -p $DIR/out/files/mei

for f in $(ls $DIR/sources/mei/**/*.mei)
do
    SHA1=$(shasum $f | awk '{print $1}')

    cp $f $DIR/out/files/mei/$SHA1.mei
    
    PDF=$(dirname $f)/$(basename $f .mei).pdf
    if test -f "$PDF"; then
        cp $PDF $DIR/out/files/mei/$SHA1.pdf
    fi
    
    SIB=$(dirname $f)/$(basename $f .mei).sib
    if test -f "$SIB"; then
        cp $SIB $DIR/out/files/mei/$SHA1.sib
    fi
    
    MEI_UUID=$(
        python3 $DIR/rdfizers/mei/main.py \
        --cache $DIR/caches/mei/$SHA1.yaml \
        --file $f \
        --sha1 $SHA1 \
        --ttl $DIR/out/mei/$SHA1.ttl
        )
    echo $MEI_UUID 🍄 $SHA1 🍄 $f
done