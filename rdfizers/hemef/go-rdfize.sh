clear

touch cache.yaml
rm ./out/*.ttl

python3 rdfize.py\
    --json out/nosj_1906-1910_1912-1914.json\
    --ttl out/1906-1910_1912-1914.ttl

python3 rdfize.py\
    --json out/nosj_1856-1861.json\
    --ttl out/1856-1861.ttl

cat ./out/*.ttl > ./out/hemef.ttl