# RDFIZATION

Le jeu de données pose deux problèmes :

    1.  Certains prédicats ont une provenance registre et une provenance TDC.
        Mais il faut parfois pouvoir exploiter une valeur unique dans l'interface (listings, tris, statistiques).
        On aimerait éviter de multiplier les champs dans l'IHM, car c'est chiant à lire, l'entrée n'est pas la source, mais la donnée, disons.
        En cas de contradiction, la valeur unifiée est placée dans un nouveau prédicat en _valeur. On pense le créer systématiquement quand les valeurs divergent. Faut-il le créer cependant si les valeurs ne divergent pas ?
    
    2.  Certains prédicats ont plusieurs valeurs (même sur une même source).
        Il faut une heuristique pour isoler une valeur unique à mettre dans le prédicat _valeur.
        Et agglutiner toutes les valeurs en un champ unique _saisie

Le prédicat _saisie est créé quand :
    1.  Il y a une hypothèse sur la valeur extractible.
    2.  Si plusieurs valeurs divergentes sont données. Il prend alors pour objet l'agglutination de toutes ces valeurs.