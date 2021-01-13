touch cache.yaml
rm -rf ./out
mkdir ./out

python3 jsonize.py\
    --xlsx "sources/1856_1861_modifié V3.xlsx"\
    --divergences out/divergences_1856-1861.json\
    --json out/nosj_1856-1861.json\

python3 jsonize.py\
    --xlsx "sources/Clean_1906-1910_et_1912-1914.xlsx"\
    --divergences out/divergences_1906-1910_1912-1914.json\
    --json out/nosj_1906-1910_1912-1914.json\

# EXEMPLES D'UTILISATIONS
# ./go-jsonizer.sh | grep "COLONNE INCONNUE" | sort | uniq
# rm log.txt ; rm cache.yaml ; ./go-jsonizer.sh | grep -v "COLONNE INCONNUE" > log.txt