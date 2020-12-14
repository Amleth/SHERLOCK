rm -rf ./out
mkdir ./out
python3 jsonizer.py\
    --xlsx "sources/1856_1861_modifié V3.xlsx"\
    --divergences out/divergences.json\
    --divergences_cursus_parcoursclasse out/divergences_cursus_parcoursclasse.json\
    --json out/nosj.json\