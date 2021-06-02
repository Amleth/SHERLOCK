trap "exit" INT

file_name () {
	filename=$(basename "$1")
	extension="${filename##*.}"
	filename="${filename%.*}"

	echo $filename
}

TEI_LIVRAISONS=./out/files/mercure-galant/tei/livraisons
TEI_ARTICLES=./out/files/mercure-galant/tei/articles
JSON_ARTICLES=./out/files/mercure-galant/json/articles

rm -rf $TEI_LIVRAISONS
mkdir -p $TEI_LIVRAISONS
rm -rf $TEI_ARTICLES
mkdir -p $TEI_ARTICLES
rm -rf $JSON_ARTICLES
mkdir -p $JSON_ARTICLES

MGGHXML=./mercure-galant/xml

for f in $(ls $MGGHXML)
do
  f=$MGGHXML/$f
  livraison_id=$(file_name $f)
  echo ""
  echo LIVRAISON $livraison_id
  cp $f $TEI_LIVRAISONS
  
  # FRAGMENTATION DES FICHIERS TEI
  saxon -s:$f -xsl:./sources-processors/mercure-galant/fragment.xslt -o:$TEI_ARTICLES/TOKILL.xml
  rm $TEI_ARTICLES/TOKILL.xml

  # FORMATAGE DES FRAGMENTS TEI
  for f in $(ls $TEI_ARTICLES/$livraison_id*)
  do
    article_id=$(file_name $f)

    mv $f $f.temp0
    xmllint --noblanks $f.temp0 > $f.temp1
    tr -d "\n\r" < $f.temp1 > $f.temp2
    tr -s " " < $f.temp2 > $f
    rm $f.temp0
    rm $f.temp1
    rm $f.temp2

    # SHERLOCKISATION DES FRAGMENTS TEI
    echo "    $(file_name $f) [TEI] -> $article_id [JSON]"
    python3 ./sources-processors/mercure-galant/xml2json.py $f $JSON_ARTICLES/$article_id.json
  done
done