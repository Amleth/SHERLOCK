# Édition MG
    
- Gestion des ressources
    - hébergement des images IIIF pour remplacer les `"attributes": { "url": "images/1678-01_224.JPG" }`
    - Où sont les fichiers MEI ? Si nous ne sommes pas en mesure de distinguer dans la source TEI les images de partition des autres images, alors cette distinction pourrait apparaître dans le nom des images. AP propose "E" pour estampes. Un "M" pour musique serait-il possible ? Il faudrait alors modifier les fichiers TEI en conséquence (à voir avec Nathalie).
- Données sémantiques
    - graph livraisons (LRMoo)
    - graph gravures (LRMoo + CRM)
    - graph musique (LRMoo + CRM)
- Navigation dans le corpus (*« Les livraisons », « Les gravures », « La musique »*)
- Affichage des articles
    - dans certains articles il y a des liens vers des images
    - certaines images ne sont pas rattachées à un article, et donc elles sont listées dans la livraison au même niveau que les articles

# Indexation simple des articles

- Données sémantiques :
    - Réunion (AP+NBB) pour aligner les mots-clefs et le thésaurus d'indexation des gravures.
    - A Générer le E32 de E55 à partir du fichier Word (idée d'un export vaguement XML pour garder la structure arborescente)
    - B Des tas de fichiers RTF qui contiennent les indexations
    - A + B => Des tas de E13, signées par l'équipe Mercure, qui associent des F2 article à des E55. Quel est le P177 ?
- Interface : un onglet « Indexation » qui pointe vers l'arbre sur le navigateur SHERLOCK. On peut ainsi accéder aux articles indexés, et retourner dans l'application de lecture via des liens `rdfs:seeAlso`.

# Indexation sémantique des articles

- Données sémantiques : des E13

# Annotations

- On lit un article, on sélectionne un passage, on le connecte à un truc via une E13.
- Difficultés technique :
    - mode authentifié dans l'application
    - Je sais comment sélectionner une portion d'article (grâce aux chemins XPath). Mais comment fais-je pour aller chercher le concept qui m'intéresse ?
        - Dans un premier temps, on saisit directement l'URI de la chose qui annote le passage.
        - Dans un second temps : ElasticSearch.
- Quand on consulte un article, il faut pouvoir voir les annotations.

# Édition des référentiels

- On a l'API authentifiée, mais les formulaires vont être un peu long à développer.