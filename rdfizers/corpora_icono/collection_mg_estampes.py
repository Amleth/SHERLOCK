import argparse
from rdflib import Literal as l, RDF, RDFS, URIRef as u
from helpers_python import get_xlsx_rows_as_dicts
from helpers_rdf import a, crm, crmdig, init_graph, save_graph, she, t
from sherlockcachemanagement import Cache
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--ttl")
parser.add_argument("--xlsx")
parser.add_argument("--cache")
parser.add_argument("--cache_corpus")
parser.add_argument("--cache_personnes")
parser.add_argument("--cache_lieux")
parser.add_argument("--cache_vocab_estampes")
args = parser.parse_args()

cache = Cache(args.cache)
if args.cache_corpus:
    cache_corpus = Cache(args.cache_corpus)
if args.cache_personnes:
    cache_personnes = Cache(args.cache_personnes)
if args.cache_lieux:
    cache_lieux = Cache(args.cache_lieux)
if args.cache_vocab_estampes:
    cache_vocab_estampes = Cache(args.cache_vocab_estampes)

init_graph()

###################################################################################################
# Fonction
###################################################################################################

def process(data):
    collection = she("759d110d-fd68-47bb-92fd-341bb63dbcae")
    id = data["Cote"]

    # E36 Visual Item
    gravure = she(cache.get_uuid(["estampes", id, "E36", "uuid"], True))
    t(gravure, a, crm("E36_Visual_Item"))
    t(collection, crm("P106_is_composed_of"), gravure)

    # Identifiant Mercure Galant
    gravure_id_MG = she(cache.get_uuid(["estampes", id, "E36", "identifiant MG"], True))
    t(gravure_id_MG, a, crm("E42_Identifier"))
    t(gravure_id_MG, crm("P2_has_type"), she("92c258a0-1e34-437f-9686-e24322b95305"))
    t(gravure_id_MG, RDFS.label, l(id))
    t(gravure, crm("P1_is_identified_by"), gravure_id_MG)

    # Identifiant IIIF
    gravure_id_iiif = she(cache.get_uuid(["estampes", id, "E36", "identifiant iiif"], True))
    t(gravure_id_iiif, a, crm("E42_Identifier"))
    t(gravure_id_iiif, crm("P2_has_type"), she("19073c4a-0ef7-4ac4-a51a-e0810a596773"))
    t(gravure_id_iiif, RDFS.label, u(f"http://data-iremus.huma-num.fr/iiif/3/mg_estampes--{id.replace(' ', '%20')}.tif/full/max/0/default.jpg"))
    t(gravure, crm("P1_is_identified_by"), gravure_id_iiif)

    # E12 Production
    if data["INV"] or data["SCULP"]:
        gravure_E12 = she(cache.get_uuid(["estampes", id, "E36", "E12", "uuid"], True))
        t(gravure_E12, a, crm("E12_Production"))
        t(gravure_E12, crm("P108_has_produced"), gravure)

    # Invenit
    if data["INV"]:
        gravure_invenit = she(cache.get_uuid(["estampes", id, "E36", "E12", "invenit", "uuid"], True))
        t(gravure_invenit, a, crm("E12_Production"))
        t(gravure_invenit, crm("P2_has_type"), she("4d57ac14-247f-4b0e-90ca-0397b6051b8b"))
        t(gravure_E12, crm("P9_consists_of"), gravure_invenit)

        ## E13 Attribute Assignement -  concepteur de la gravure
        gravure_invenit_auteur = she(cache.get_uuid(["estampes", id, "E36", "E12", "invenit", "auteur"], True))
        t(gravure_invenit_auteur, a, crm("E21_Person"))
        t(gravure_invenit_auteur, RDFS.label, l(data["INV"]))
        gravure_invenit_E13 = she(cache.get_uuid(["estampes", id, "E36", "E12", "invenit", "E13"], True))
        t(gravure_invenit_E13, a, crm("E13_Attribute_Assignement"))
        t(gravure_invenit_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(gravure_invenit_E13, crm("P140_assigned_attribute_to"), gravure_invenit)
        t(gravure_invenit_E13, crm("P141_assigned"), gravure_invenit_auteur)
        t(gravure_invenit_E13, crm("P177_assigned_property_type"), crm("P14_carried_out_by"))

        ## E13 Attribute Assignement - technique de la représentation
        if data["Technique de la représentation [Avec Maj et au pl.]"]:
            gravure_E29 = she(cache.get_uuid(["estampes", id, "E36", "E12", "E29"], True))
            t(gravure_E29, a, crm("E29_Design_or_Procedure"))
            t(gravure_E29, RDFS.label, l(data["Technique de la représentation [Avec Maj et au pl.]"]))
            gravure_E29_E13 = she(cache.get_uuid(["estampes", id, "E36", "E12", "E55", "E13"], True))
            t(gravure_E29_E13, a, crm("E13_Attribute_Assignement"))
            t(gravure_E29_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
            t(gravure_E29_E13, crm("P140_assigned_attribute_to"), gravure_invenit)
            t(gravure_E29_E13, crm("P141_assigned"), gravure_E29)
            t(gravure_E29_E13, crm("P177_assigned_property_type"), crm("P33_used_specific_technique"))

    # Sculpsit
    if data["SCULP"]:
        gravure_sculpsit = she(cache.get_uuid(["estampes", id, "E36", "E12", "sculpsit", "uuid"], True))
        t(gravure_sculpsit, a, crm("E12_Production"))
        t(gravure_sculpsit, crm("P2_has_type"), she("f39eb497-5559-486c-b5ce-6a607f615773"))
        t(gravure_E12, crm("P9_consists_of"), gravure_sculpsit)

        ## E13 Attribute Assignement -  sculpteur de la gravure
        gravure_sculpsit_auteur = she(cache.get_uuid(["estampes", id, "E36", "E12", "sculpsit", "auteur"], True))
        t(gravure_sculpsit_auteur, a, crm("E21_Person"))
        t(gravure_sculpsit_auteur, RDFS.label, l(data["SCULP"]))
        gravure_sculpsit_E13 = she(cache.get_uuid(["estampes", id, "E36", "E12", "sculpsit", "E13"], True))
        t(gravure_sculpsit_E13, a, crm("E13_Attribute_Assignement"))
        t(gravure_sculpsit_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(gravure_sculpsit_E13, crm("P140_assigned_attribute_to"), gravure_sculpsit)
        t(gravure_sculpsit_E13, crm("P141_assigned"), gravure_sculpsit_auteur)
        t(gravure_sculpsit_E13, crm("P177_assigned_property_type"), crm("P14_carried_out_by"))

        ## E13 Attribute Assignement - technique de la gravure
        if data["Technique de la gravure [Avec Maj et au pl.]"]:
            gravure_E55 = she(cache.get_uuid(["estampes", id, "E36", "E12", "E55", "uuid"], True))
            t(gravure_E55, a, crm("E55_Type"))
            t(gravure_E55, RDFS.label, l(data["Technique de la gravure [Avec Maj et au pl.]"]))
            gravure_E55_E13 = she(cache.get_uuid(["estampes", id, "E36", "E12", "E55", "E13"], True))
            t(gravure_E55_E13, a, crm("E13_Attribute_Assignement"))
            t(gravure_E55_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
            t(gravure_E55_E13, crm("P140_assigned_attribute_to"), gravure_sculpsit)
            t(gravure_E55_E13, crm("P141_assigned"), gravure_E55)
            t(gravure_E55_E13, crm("P177_assigned_property_type"), crm("P32_used_general_technique"))

    # Rattachement à la livraison ou à l'article
    ## Si l'article n'est pas précisé:
    if not data["Cote article OBVIL"]:
        id_image = f"MG-{id}"
        id_livraison = f"MG-{id[0:-4]}"
        if id_livraison.endswith("_"):
            id_livraison = id_livraison[0:-1]
        try:
            ### Livraison originale
            livraison_F2_originale = she(
                cache_corpus.get_uuid(["Corpus", "Livraisons", id_livraison, "Expression originale", "F2"]))
            t(livraison_F2_originale, crm("P148_has_component"), gravure)
            ### Livraison TEI
            livraison_F2_TEI = she(
                cache_corpus.get_uuid(["Corpus", "Livraisons", id_livraison, "Expression TEI", "F2"]))
            t(livraison_F2_TEI, crm("P148_has_component"), gravure)
        except:
            print("L'image " + id_image + " n'est reliée à aucune livraison")

    ## Si l'article est précisé:
    else:
        id_article = data["Cote article OBVIL"]
        id_livraison = id_article[0:11]
        try:
            if id_livraison.endswith("_"):
                id_livraison = id_livraison[0:-1]
                ### Article original
                article_F2_original = she(cache_corpus.get_uuid(
                    ["Corpus", "Livraisons", id_livraison, "Expression originale", "Articles", id_article, "F2"]))
                t(article_F2_original, crm("P148_has_component"), gravure)
                ### Article TEI
                article_F2_TEI = she(cache_corpus.get_uuid(
                    ["Corpus", "Livraisons", id_livraison, "Expression TEI", "Articles", id_article, "F2"]))
                t(article_F2_TEI, crm("P148_has_component"), gravure)
            else:
                ### Article original
                article_F2_original = she(cache_corpus.get_uuid(
                    ["Corpus", "Livraisons", id_livraison, "Expression originale", "Articles", id_article, "F2"]))
                t(article_F2_original, crm("P148_has_component"), gravure)
                ### Article TEI
                article_F2_TEI = she(cache_corpus.get_uuid(
                    ["Corpus", "Livraisons", id_livraison, "Expression TEI", "Articles", id_article, "F2"]))
                t(article_F2_TEI, crm("P148_has_component"), gravure)
        except:
            print("Article contenant la gravure : l'article " + id_article + " est introuvable dans les fichiers TEI")

    # Article annexe à la gravure
    if data["Cote article lié OBVIL"]:
        id_article = data["Cote article lié OBVIL"]
        id_livraison = id_article[0:10]
        try:
            article_F2 = she(cache_corpus.get_uuid(
                ["Corpus", "Livraisons", id_livraison, "Expression TEI", "Articles", id_article, "F2"]))
            gravure_seeAlso_E13 = she(cache.get_uuid(["estampes", id, "E36", "seeAlso", "E13"], True))
            t(gravure_seeAlso_E13, a, crm("E13_Attribute_Assignement"))
            t(gravure_seeAlso_E13, crm("P14_carried_out_by"),
              she("684b4c1a-be76-474c-810e-0f5984b47921"))
            t(gravure_seeAlso_E13, crm("P140_assigned_attribute_to"), gravure)
            t(gravure_seeAlso_E13, crm("P141_assigned"), article_F2)
            t(gravure_seeAlso_E13, crm("P177_assigned_property_type"), RDFS.seeAlso)

            ## Commentaire décrivant le lien entre la gravure et l'article
            if data["Commentaire Cote article lié OBVIL"]:
                gravure_seeAlso_P3_E13 = she(
                    cache.get_uuid(["estampes", id, "E36", "seeAlso", "note", "E13"], True))
                t(gravure_seeAlso_P3_E13, a, crm("E13_Attribute_Assignement"))
                t(gravure_seeAlso_P3_E13, crm("P14_carried_out_by"),
                  she("684b4c1a-be76-474c-810e-0f5984b47921"))
                t(gravure_seeAlso_P3_E13, crm("P140_assigned_attribute_to"), article_F2)
                t(gravure_seeAlso_P3_E13, crm("P141_assigned"), l(data["Commentaire Cote article lié OBVIL"]))
                t(gravure_seeAlso_P3_E13, crm("P177_assigned_property_type"), crm("P3_has_note"))
        except:
            print(
                "Article annexe à la gravure : l'article " + id_article + " est introuvable dans les fichiers TEI")

    # Lien Gallica
    if data["Lien au texte [ou à l'image]  dans Gallica"]:
        try:
            response = requests.get(data["Lien au texte [ou à l'image]  dans Gallica"])
            lien_gallica = u(data["Lien au texte [ou à l'image]  dans Gallica"])
            t(lien_gallica, crm("P2_has_type"), she("e73699b0-9638-4a9a-bfdd-ed1715416f02"))
            img_gallica_E13 = she(cache.get_uuid(["estampes", id, "E36", "gallica", "E13"], True))
            t(img_gallica_E13, a, crm("E13_Attribute_Assignement"))
            t(img_gallica_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
            t(img_gallica_E13, crm("P140_assigned_attribute_to"), gravure)
            t(img_gallica_E13, crm("P141_assigned"), lien_gallica)
            t(img_gallica_E13, crm("P177_assigned_property_type"), RDFS.seeAlso)
        except:
            print("'" + data["Lien au texte [ou à l'image]  dans Gallica"] + "' n'est pas une URL valide")

    # Titre sur l'image (E13)
    if data["Titre sur l'image"]:
        gravure_titre = she(cache.get_uuid(["estampes", id, "E36", "titre sur l'image"], True))
        t(gravure_titre, a, crm("E13_Attribute_Assignement"))
        t(gravure_titre, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(gravure_titre, crm("P140_assigned_attribute_to"), gravure)
        t(gravure_titre, crm("P141_assigned"), l(data["Titre sur l'image"]))
        t(gravure_titre, crm("P177_assigned_property_type"), she("01a07474-f2b9-4afd-bb05-80842ecfb527"))

    # Titre descriptif/forgé (E13)
    if data[" [titre descriptif forgé]*  (Avec Maj - accentuées]"]:
        gravure_titre = she(cache.get_uuid(["estampes", id, "E36", "titre forgé"], True))
        t(gravure_titre, a, crm("E13_Attribute_Assignement"))
        t(gravure_titre, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(gravure_titre, crm("P140_assigned_attribute_to"), gravure)
        t(gravure_titre, crm("P141_assigned"), l(data[" [titre descriptif forgé]*  (Avec Maj - accentuées]"]))
        t(gravure_titre, crm("P177_assigned_property_type"), she("58fb99dd-1ffb-4e00-a16f-ef6898902301"))

    # Titre dans le péritexte (E13)
    if data["[Titre dans le péritexte: Avis, article…]"]:
        gravure_titre = she(cache.get_uuid(["estampes", id, "E36", "titre péritexte"], True))
        t(gravure_titre, a, crm("E13_Attribute_Assignement"))
        t(gravure_titre, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(gravure_titre, crm("P140_assigned_attribute_to"), gravure)
        t(gravure_titre, crm("P141_assigned"), l(data["[Titre dans le péritexte: Avis, article…]"]))
        t(gravure_titre, crm("P177_assigned_property_type"), she("ded9ea93-b400-4550-9aa8-e5aac1d627a0"))

    # Lieu représenté
    if data["Lieux"]:

        lieu = data["Lieux"]

        ## Zone de l'image comportant la représentation du lieu (E13)
        gravure_zone_img = she(cache.get_uuid(["estampes", id, "E36", lieu, "zone de l'image (E36)", "uuid"], True))
        t(gravure_zone_img, a, crm("E36_Visual_Item"))
        gravure_zone_img_E13 = she(cache.get_uuid(["estampes", id, "E36", lieu, "zone de l'image (E36)", "E13"], True))
        t(gravure_zone_img_E13, a, crm("E13_Attribute_Assignement"))
        t(gravure_zone_img_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(gravure_zone_img_E13, crm("P140_assigned_attribute_to"), gravure)
        t(gravure_zone_img_E13, crm("P141_assigned"), gravure_zone_img)
        t(gravure_zone_img_E13, crm("P177_assigned_property_type"), crm("P106_is_composed_of"))

        ## Recherche d'UUID dans le référentiel des lieux
        try:
            lieu_uuid = she(cache_lieux.get_uuid(["lieu", str(lieu), "E93", "uuid"]))
            if lieu_uuid:
                gravure_lieu_E13 = she(cache.get_uuid(["estampes", id, "E36", lieu, "zone de l'image (E36)", "lieu représenté"], True))
                t(gravure_lieu_E13, a, crm("E13_Attribute_Assignement"))
                t(gravure_lieu_E13, crm("P14_carried_out_by"),
                  she("684b4c1a-be76-474c-810e-0f5984b47921"))
                t(gravure_lieu_E13, crm("P140_assigned_attribute_to"), gravure_zone_img)
                t(gravure_lieu_E13, crm("P177_assigned_property_type"), crm("P138_represents"))
                t(gravure_lieu_E13, crm("P141_assigned"), lieu_uuid)

        except:
            gravure_lieu_E13 = she(cache.get_uuid(
                ["collection", id, "E36", lieu, "zone de l'image (E36)", "lieu représenté"], True))
            t(gravure_lieu_E13, a, crm("E13_Attribute_Assignement"))
            t(gravure_lieu_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
            t(gravure_lieu_E13, crm("P140_assigned_attribute_to"), gravure_zone_img)
            t(gravure_lieu_E13, crm("P177_assigned_property_type"), crm("P138_represents"))
            t(gravure_lieu_E13, crm("P141_assigned"), l(lieu))

    ## Objet/Personne représentée (E13)
    if data["objet [en bdc, sg par défaut]/Sujet représenté [avec Maj.]"]:

        sujets = data["objet [en bdc, sg par défaut]/Sujet représenté [avec Maj.]"].split(";")

        for sujet in sujets:
            sujet = sujet.strip()

            ### Zone de l'image comportant la représentation du sujet (E13)
            gravure_zone_img = she(
                cache.get_uuid(["estampes", id, "E36", sujet, "zone de l'image (E36)", "uuid"], True))
            t(gravure_zone_img, a, crm("E36_Visual_Item"))
            gravure_zone_img_E13 = she(
                cache.get_uuid(["estampes", id, "E36", sujet, "zone de l'image (E36)", "E13"], True))
            t(gravure_zone_img_E13, a, crm("E13_Attribute_Assignement"))
            t(gravure_zone_img_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
            t(gravure_zone_img_E13, crm("P140_assigned_attribute_to"), gravure)
            t(gravure_zone_img_E13, crm("P141_assigned"), gravure_zone_img)
            t(gravure_zone_img_E13, crm("P177_assigned_property_type"), crm("P106_is_composed_of"))

            ### Recherche d'UUID dans le référentiel des personnes
            try:
                personne_uuid = she(cache_personnes.get_uuid(["personnes", sujet, "uuid"]))
                if personne_uuid:
                    gravure_personne_E13 = she(cache.get_uuid(
                        ["collection", id, "E36", sujet, "zone de l'image (E36)", "personne représentée"],
                        True))
                    t(gravure_personne_E13, a, crm("E13_Attribute_Assignement"))
                    t(gravure_personne_E13, crm("P14_carried_out_by"),
                      she("684b4c1a-be76-474c-810e-0f5984b47921"))
                    t(gravure_personne_E13, crm("P140_assigned_attribute_to"), gravure_zone_img)
                    t(gravure_personne_E13, crm("P177_assigned_property_type"), crm("P138_represents"))
                    t(gravure_personne_E13, crm("P141_assigned"), personne_uuid)
            except:

                ### Recherche d'UUID dans le vocabulaire d'indexation des gravures
                try:
                    objet_uuid = she(cache_vocab_estampes.get_uuid(["vocabulaire indexation gravures", sujet, "uuid"]))
                    if objet_uuid:

                        if "médaille" not in sujet:
                            gravure_objet_E13 = she(cache.get_uuid(
                                ["collection", id, "E36", sujet, "zone de l'image (E36)", "objet représenté"], True))
                            t(gravure_objet_E13, a, crm("E13_Attribute_Assignement"))
                            t(gravure_objet_E13, crm("P14_carried_out_by"),
                              she("684b4c1a-be76-474c-810e-0f5984b47921"))
                            t(gravure_objet_E13, crm("P140_assigned_attribute_to"), gravure_zone_img)
                            t(gravure_objet_E13, crm("P177_assigned_property_type"), crm("P138_represents"))
                            t(gravure_objet_E13, crm("P141_assigned"), objet_uuid)

                        ### Si l'objet représenté est une médaille (E13)
                        if "médaille" in sujet:
                            #### E13 Attribute Assignement - la médaille
                            t(objet_uuid, a, crm("E55_Type"))
                            t(objet_uuid, crm("P2_has_type"), she("4b51d9dc-3623-47f4-ab45-239604e18930"))

                            gravure_médaille_E13 = she(cache.get_uuid(
                                ["collection", id, "E36", sujet, "zone de l'image (E36)", "objet représenté"], True))
                            t(gravure_médaille_E13, a, crm("E13_Attribute_Assignement"))
                            t(gravure_médaille_E13, crm("P14_carried_out_by"),
                              she("684b4c1a-be76-474c-810e-0f5984b47921"))
                            t(gravure_médaille_E13, crm("P140_assigned_attribute_to"), gravure_zone_img)
                            t(gravure_médaille_E13, crm("P177_assigned_property_type"), crm("P138_represents"))
                            t(gravure_médaille_E13, crm("P141_assigned"), objet_uuid)

                            #### Si la médaille comporte une inscription
                            if data["Médailles: légende"] or data["Médailles: exergue"]:
                                gravure_médaille_inscrip_E36 = she(
                                    cache.get_uuid(
                                        ["collection", id, "E36", sujet, "zone d'inscription", "uuid"], True))
                                t(gravure_médaille_inscrip_E36, a, crm("E36_Visual_Item"))
                                t(gravure_médaille_inscrip_E36, RDFS.label, l("Zone d'inscription"))
                                ##### E13 Attribute Assignement
                                gravure_médaille_inscrip_E13 = she(
                                    cache.get_uuid(
                                        ["collection", id, "E36", sujet, "zone d'inscription", "E13"], True))
                                t(gravure_médaille_inscrip_E13, a, crm("E13_Attribute_Assignement"))
                                t(gravure_médaille_inscrip_E13, crm("P14_carried_out_by"),
                                  she("684b4c1a-be76-474c-810e-0f5984b47921"))
                                t(gravure_médaille_inscrip_E13, crm("P140_assigned_attribute_to"), objet_uuid)
                                t(gravure_médaille_inscrip_E13, crm("P141_assigned"), gravure_médaille_inscrip_E36)
                                t(gravure_médaille_inscrip_E13, crm("P177_assigned_property_type"),
                                  crm("P106_is_composed_of"))

                            ##### Si la médaille comporte une inscription en légende (E13)
                            if data["Médailles: légende"]:
                                gravure_médaille_inscrip_E33 = she(
                                    cache.get_uuid(
                                        ["collection", id, "E36", sujet, "zone d'inscription",
                                         "inscription", "en légende", "uuid"], True))
                                t(gravure_médaille_inscrip_E33, a, crm("E33_Linguistic_Object"))

                                ##### E13 Attribute Assignement du E33
                                gravure_médaille_inscrip_E33_E13 = she(
                                    cache.get_uuid(
                                        ["collection", id, "E36", sujet, "zone d'inscription",
                                         "inscription", "en légende", "E13"], True))
                                t(gravure_médaille_inscrip_E33_E13, a, crm("E13_Attribute_Assignement"))
                                t(gravure_médaille_inscrip_E33_E13, crm("P14_carried_out_by"),
                                  she("684b4c1a-be76-474c-810e-0f5984b47921"))
                                t(gravure_médaille_inscrip_E33_E13, crm("P140_assigned_attribute_to"),
                                  gravure_médaille_inscrip_E36)
                                t(gravure_médaille_inscrip_E33_E13, crm("P141_assigned"), gravure_médaille_inscrip_E33)
                                t(gravure_médaille_inscrip_E33_E13, crm("P177_assigned_property_type"),
                                  crm("P165_incorporates"))
                                t(gravure_médaille_inscrip_E33_E13,
                                  she("sheP_position_du_texte_par_rapport_à_la_médaille"),
                                  she("fc229531-0999-4499-ab0b-b45e18e8196f"))

                                ##### E13 Attribute Assignement du contenu de l'inscription
                                gravure_médaille_inscrip_P190_E13 = she(
                                    cache.get_uuid(
                                        ["collection", id, "E36", sujet, "zone d'inscription",
                                         "inscription", "en légende", "contenu"], True))
                                t(gravure_médaille_inscrip_P190_E13, a, crm("E13_Attribute_Assignement"))
                                t(gravure_médaille_inscrip_P190_E13, crm("P14_carried_out_by"),
                                  she("684b4c1a-be76-474c-810e-0f5984b47921"))
                                t(gravure_médaille_inscrip_P190_E13, crm("P140_assigned_attribute_to"),
                                  gravure_médaille_inscrip_E33)
                                t(gravure_médaille_inscrip_P190_E13, crm("P141_assigned"), l(data[17]))
                                t(gravure_médaille_inscrip_P190_E13, crm("P177_assigned_property_type"),
                                  crm("P190_has_symbolic_content"))

                            ##### Si la médaille comporte une inscription en exergue (E13)
                            if data["Médailles: exergue"]:
                                gravure_médaille_inscrip_E33 = she(
                                    cache.get_uuid(
                                        ["collection", id, "E36", sujet, "zone d'inscription",
                                         "inscription", "en exergue", "uuid"], True))
                                t(gravure_médaille_inscrip_E33, a, crm("E33_Linguistic_Object"))

                                ##### E13 Attribute Assignement du E33
                                gravure_médaille_inscrip_E33_E13 = she(
                                    cache.get_uuid(
                                        ["collection", id, "E36", sujet, "zone d'inscription",
                                         "inscription", "en exergue", "E13"], True))
                                t(gravure_médaille_inscrip_E33_E13, a, crm("E13_Attribute_Assignement"))
                                t(gravure_médaille_inscrip_E33_E13, crm("P14_carried_out_by"),
                                  she("684b4c1a-be76-474c-810e-0f5984b47921"))
                                t(gravure_médaille_inscrip_E33_E13, crm("P140_assigned_attribute_to"),
                                  gravure_médaille_inscrip_E36)
                                t(gravure_médaille_inscrip_E33_E13, crm("P141_assigned"), gravure_médaille_inscrip_E33)
                                t(gravure_médaille_inscrip_E33_E13, crm("P177_assigned_property_type"),
                                  crm("P165_incorporates"))
                                t(gravure_médaille_inscrip_E33_E13,
                                  she("sheP_position_du_texte_par_rapport_à_la_médaille"),
                                  she("357a459f-4f27-4d46-b5ac-709a410bce04"))

                                ##### E13 Attribute Assignement du contenu de l'inscription
                                gravure_médaille_inscrip_P190_E13 = she(
                                    cache.get_uuid(
                                        ["collection", id, "E36", sujet, "zone d'inscription",
                                         "inscription", "en exergue", "contenu"], True))
                                t(gravure_médaille_inscrip_P190_E13, a, crm("E13_Attribute_Assignement"))
                                t(gravure_médaille_inscrip_P190_E13, crm("P14_carried_out_by"),
                                  she("684b4c1a-be76-474c-810e-0f5984b47921"))
                                t(gravure_médaille_inscrip_P190_E13, crm("P140_assigned_attribute_to"),
                                  gravure_médaille_inscrip_E33)
                                t(gravure_médaille_inscrip_P190_E13, crm("P141_assigned"), l(data[18]))
                                t(gravure_médaille_inscrip_P190_E13, crm("P177_assigned_property_type"),
                                  crm("P190_has_symbolic_content"))

                except:
                    gravure_objet_E13 = she(cache.get_uuid(["collection", id, "E36", sujet, "zone de l'image (E36)", "objet représenté"], True))
                    t(gravure_objet_E13, a, crm("E13_Attribute_Assignement"))
                    t(gravure_objet_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
                    t(gravure_objet_E13, crm("P140_assigned_attribute_to"), gravure_zone_img)
                    t(gravure_objet_E13, crm("P177_assigned_property_type"), crm("P138_represents"))
                    t(gravure_objet_E13, crm("P141_assigned"), l(sujet))


    ## Notes sur la provenance de la gravure
    if data["PROVENANCE"]:
        gravure_notes_E13 = she(cache.get_uuid(["estampes", id, "E36", "notes", "E13"], True))
        t(gravure_notes_E13, a, crm("E13_Attribute_Assignement"))
        t(gravure_notes_E13, crm("P14_carried_out_by"), she("684b4c1a-be76-474c-810e-0f5984b47921"))
        t(gravure_notes_E13, crm("P140_assigned_attribute_to"), gravure)
        t(gravure_notes_E13, crm("P141_assigned"), l(data["PROVENANCE"]))
        t(gravure_notes_E13, crm("P177_assigned_property_type"), crm("P3_has_note"))

    ## Autres liens externes
    if data["LIENS EXTERNES"]:
        try:
            response = requests.get(data["LIENS EXTERNES"])
            lien_externe = u(data["LIENS EXTERNES"])
            gravure_lien_externe_E13 = she(
                cache.get_uuid(["estampes", id, "E36", "lien externe", "E13"], True))
            t(gravure_lien_externe_E13, a, crm("E13_Attribute_Assignement"))
            t(gravure_lien_externe_E13, crm("P14_carried_out_by"),
              she("684b4c1a-be76-474c-810e-0f5984b47921"))
            t(gravure_lien_externe_E13, crm("P140_assigned_attribute_to"), gravure)
            t(gravure_lien_externe_E13, crm("P141_assigned"), lien_externe)
            t(gravure_lien_externe_E13, crm("P177_assigned_property_type"), RDFS.seeAlso)
        except:
            print("'" + data["LIENS EXTERNES"] + "' n'est pas une URL valide")


###################################################################################################
# Exécution de la fonction
###################################################################################################

rows = get_xlsx_rows_as_dicts(args.xlsx)
for row in rows:
    if row["Cote"] is not None:
        process(row)

###################################################################################################
# Création du graphe et du cache
###################################################################################################

cache.bye()
save_graph(args.ttl)





#
# 				## Bibliographie relative à la gravure
# 				if data[21]:
# 					biblio = she(cache.get_uuid(["estampes", id, "E36", "bibliographie", "uuid"], True))
# 					t(biblio, a, crm("E31_Document"))
# 					t(biblio, RDFS.label, l(data[21]))
# 					## E13 Attribute Assignement
# 					gravure_biblio_E13 = she(cache.get_uuid(["estampes", id, "E36", "bibliographie", "E13"], True))
# 					t(gravure_biblio_E13, a, crm("E13_Attribute_Assignement"))
# 					t(gravure_biblio_E13, crm("P14_carried_out_by"),
# 					  she("684b4c1a-be76-474c-810e-0f5984b47921"))
# 					t(gravure_biblio_E13, crm("P140_assigned_attribute_to"), gravure)
# 					t(gravure_biblio_E13, crm("P141_assigned"), biblio)
# 					t(gravure_biblio_E13, crm("P177_assigned_property_type"), crm("P70_documents"))
