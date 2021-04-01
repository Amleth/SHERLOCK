SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIR=$SCRIPT_DIR/..

mkdir -p $DIR/out/ontologies

cp $DIR/modal-tonal-ontology/modality-tonality-ontology.owl $DIR/out/ontologies
cp $DIR/modal-tonal-ontology/modality-tonality-ontology-ex.owl $DIR/out/ontologies

python3 $DIR/rdfizers/skolemisation/skolemisation.py \
    --inowl $DIR/sources/modality-tonality-ontologies/Praetorius_1612_1619.owl \
    --query $DIR/rdfizers/skolemisation/skolemisation.sparql \
    --outowl $DIR/out/ontologies/Praetorius_1612_1619_skolemized.owl