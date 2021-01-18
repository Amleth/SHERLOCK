# JSONIZE

- les entités potentielles qui ne sont référencées que par leur nom doivent l'être par un prédicat en _nom (ville, département, pays, établissement…)
- traiter les dates comme ça : "1863 ?-01-31", extraire les mois et jours
- traiter les lignes qui ont un identifiant_1_TDC

# RDFIZE

- Et merde, find_usable n'a pas marché : naissance_ville_nom_valeur / naissance_ville_nom_TDC_valeur

# VUE

- afficher une donnée avec une hypothèse
- afficher une adresse avec compléments

# DONNÉES

- Pour l'instant, je ne gère qu'une profession unique par inscrit•e
- En guise d'exemples
    - http://localhost:3000/hemef/eleve/3d170e6e-336e-417f-b25c-a2f7e6eb1698
- Point sur les colonnes inconnues
    COLONNES INCONNUES sources/1856_1861_modifié V3.xlsx
        ['classe_observations', 'classe_type']
    COLONNES INCONNUES sources/Clean_1906-1910_et_1912-1914.xlsx
        ['adresse_article_voie_TDC',
        'adresse_complements_TDC',
        'adresse_nom_voie_TDC',
        'adresse_numero_voie_TDC',
        'adresse_type_voie_TDC',
        'adresse_ville_TDC',
        'adresse_ville_ancien nom_TDC',
        'classe_discipline_TDC',
        'classe_discipline_categorie',
        'classe_discipline_categorie_TDC',
        'classe_nom_TDC',
        'classe_nom_professeur_TDC',
        'classe_observations_TDC',
        'classe_type_TDC',
        'cursus_date_entree_conservatoire_TDC',
        'cursus_date_sortie_conservatoire_TDC',
        'cursus_motif_admission_TDC',
        'cursus_motif_sortie_TDC',
        'eleve_complement_prenom_TDC',
        'eleve_cote_AN_registre_TDC',
        'eleve_date_naissance_TDC',
        'eleve_departement_naissance_TDC',
        'eleve_nom_TDC',
        'eleve_nom_epouse_TDC',
        'eleve_observations_TDC',
        'eleve_pays_naissance_TDC',
        'eleve_prenom_2_TDC',
        'eleve_profession_mere_TDC',
        'eleve_profession_pere_TDC',
        'eleve_pseudonyme_TDC',
        'eleve_remarques de saisie_TDC',
        'eleve_sexe_TDC',
        'eleve_ville_naissance_TDC',
        'exerce_lieu_exercice_TDC',
        'exerce_profession_connue_TDC',
        'identifiant_1_TDC',
        'parcours_classe_date_entree_TDC',
        'parcours_classe_date_sortie_TDC',
        'parcours_classe_motif_entree_TDC',
        'parcours_classe_motif_sortie_TDC',
        'parcours_classe_observations_eleve_TDC',
        'parcours_classe_statut_eleve_TDC',
        'pre-cursus_nom_etablissement_TDC',
        'prix_date_TDC',
        'prix_discipline_TDC',
        'prix_discipline_categorie',
        'prix_discipline_categorie_TDC',
        'prix_nom_TDC',
        'prix_nom_complément_TDC',
        'prix_type_TDC',
        'profession_nom_TDC']

## Dates divergentes

- Discuter cela :
    1907-[0368 bis] parcours classe fc450cf4-2880-4b13-beb8-981ae61f884f date_sortie ['[1914-00-00]', '[1909-00-00]']
        {'date_sortie_année': 1909}
    1907-[0394 bis] parcours classe e5b4c7e9-efdc-4490-b28b-2cf11bf1f6c3 date_sortie ['[1911-00-00]', '[1910-00-00]']
        {'date_sortie_année': 1910}
    1908-[0415 bis] parcours classe d368244f-7637-4de6-bbd8-6761fecf6980 date_sortie ['[1911-00-00]', '[1910-00-00]']
        {'date_sortie_année': 1910}
    1910-[0464 bis] parcours classe e3b2411f-a521-4fe8-9c03-430b5333c6f5 date_sortie ['[1915-00-00]', '[1910-00-00]']
        {'date_sortie_année': 1910}
    1856-0072 parcours classe c78e79f6-cd27-4b87-b5a6-f5d5ed7340f4 date_sortie_TDC ['1858-12-02', '1859-03-01']
        {'date_sortie_TDC_année': 1858, 'date_sortie_TDC_mois': 12, 'date_sortie_TDC_jour': 2}
    1857-0256 élève be3133e2-c54f-4978-a478-612d992c4de5 date_sortie_conservatoire ['[1871] ?-?-?', '[1871-00-00]']
        {'date_sortie_conservatoire_année': 1871}
    1857-0290 élève e248cedd-ef8e-480e-a382-bfc43fe14b49 date_sortie_conservatoire ['[1860-00-00]', '[1860 ?]--']
        {'date_sortie_conservatoire_année': 1860}
    1857-0294 parcours classe e5d6c864-594f-4e3e-b690-ee45cb53d630 date_sortie ['?', '1860-10-01']
        {'date_sortie_année': 1860, 'date_sortie_mois': 10, 'date_sortie_jour': 1}
    1857-0342 élève 72a0fe2b-d2a0-47c7-8953-e41dcc6615be date_sortie_conservatoire ['?-?-?', '-?-?']
    1858-0581 parcours classe 14bc624a-d75d-4064-acc5-e68895597f32 date_sortie ['?', '1863-10-01']
        {'date_sortie_année': 1863, 'date_sortie_mois': 10, 'date_sortie_jour': 1}
    1860-0903 élève 2df4c3ed-21f7-4749-85e6-43c6c2d10899 date_sortie_conservatoire ['1862-?-01', '1862-00-01']
        {'date_sortie_conservatoire_année': 1862}
    1861-1119 parcours classe 633bb961-23f8-4634-8f0f-2a126f18c026 date_sortie_TDC ['1864-10-01', '1864-02-20']
        {'date_sortie_TDC_année': 1864, 'date_sortie_TDC_mois': 2, 'date_sortie_TDC_jour': 20}

# INVESTIGATION

Montrer les prédicats qui ont des valeurs composites :
`cat out/hemef.ttl| grep ⬢ | cut -c 5- | cut -d " " -f 1 | sort | uniq`



# SITE

- onglet discipline
- titrer le filtre (date d'entrée au conservatoire)
- pour le filtrage chronologique : raisonner en années scolaires et pas en années civiles
- Manque : adresse (voir dans le nouveau tableau)
- tri des élèves en faisant sauter la particule (et la mentionner)
- passer du temps sur les écrans : ergonomie, création de l'écran par type de prix, dates et leur statut d'hypothèse
