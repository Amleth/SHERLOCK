# def make_adresse(tdc):

    #     nom_voie = r("adresse_nom_voie") if not tdc else r("adresse_nom_voie_TDC")
    #     type_voie = r("adresse_type_voie") if not tdc else r("adresse_type_voie_TDC")
    #     article_voie = r("adresse_article_voie") if not tdc else r("adresse_article_voie_TDC")
    #     numéro_voie = r("adresse_numero_voie") if not tdc else r("adresse_numero_voie_TDC")
    #     compléments = r("adresse_complements") if not tdc else r("adresse_complements_TDC")
    #     ville = r("adresse_ville") if not tdc else r("adresse_ville_TDC")
    #     ville_ancien_nom = r("adresse_ville_ancien nom") if not tdc else r("adresse_ville_ancien nom_TDC")
    #     pays = r("adresse_pays")
    #     habite_début = r("habite_debut")
    #     habite_fin = r("habite_fin")

    #     adresse_label = ""
    #     if numéro_voie:
    #         adresse_label += str(numéro_voie) + " "
    #     if type_voie:
    #         adresse_label += type_voie + " "
    #     if article_voie:
    #         adresse_label += article_voie
    #         if article_voie[-1] != "'":
    #             adresse_label += " "
    #     if nom_voie:
    #         adresse_label += nom_voie + " "
    #     if compléments:
    #         compléments = str(compléments)
    #         adresse_complements_formatted = compléments
    #         if compléments[-1] == ")" and "(" not in compléments:
    #             adresse_complements_formatted = compléments[:-1]
    #         adresse_label += "(" + adresse_complements_formatted + ")"
    #     adresse_label = adresse_label.strip()

    #     # Villes
    #     if ville and not ville_ancien_nom:
    #         if adresse_label:
    #             adresse_label += ", "
    #         adresse_label += (f"{ville}" if adresse_label else ville)
    #     elif not ville and ville_ancien_nom:
    #         if adresse_label:
    #             adresse_label += ", "
    #         adresse_label += f"<dénomination contemporaine de la ville inconnue> (anciennement {ville_ancien_nom})"
    #     elif ville and ville_ancien_nom:
    #         if adresse_label:
    #             adresse_label += ", "
    #         adresse_label += f"{ville} (anciennement {ville_ancien_nom})"

    #     if not tdc:
    #         # Pays
    #         if pays:
    #             adresse_label += f", {pays}"
    #         # Date
    #         if habite_début and habite_fin:
    #             adresse_label += f" [{habite_début} → {habite_fin}]"
    #         elif habite_début and not habite_fin:
    #             adresse_label += f" [{habite_début} → …]"
    #         if not habite_début and habite_fin:
    #             adresse_label += f" [… → {habite_fin}]"

    #     return adresse_label

    # adresses = eleve["adresses"] if "adresses" in eleve else []
    # adresses_TDC = eleve["adresses_TDC"] if "adresses_TDC" in eleve else []
    # adresse = {}
    # adresse_TDC = {}

    # adresse_label = make_adresse(False)
    # if adresse_label:
    #     adresse["label"] = adresse_label
    # adresse_TDC_label = make_adresse(True)
    # if adresse_TDC_label:
    #     adresse_TDC["label_TDC"] = adresse_TDC_label
    # if r("habite_debut"):
    #     adresse["habite_début"] = r("habite_debut")
    # if r("habite_fin"):
    #     adresse["habite_fin"] = r("habite_fin")
    # if r("adresse_geolocalisation"):
    #     adresse["géolocalisation"] = r("adresse_geolocalisation")

    # # ville
    # ville = {}
    # if r("adresse_ville"):
    #     ville["nom"] = r("adresse_ville")
    # if r("adresse_ville_ancien nom"):
    #     ville["ancien_nom"] = r("adresse_ville_ancien nom")
    # if len(ville) > 0:
    #     adresse["ville"] = ville
    # ville_TDC = {}
    # if r("adresse_ville_TDC"):
    #     ville_TDC["nom_TDC"] = r("adresse_ville_TDC")
    # if r("adresse_ville_ancien nom_TDC"):
    #     ville_TDC["ancien_nom_TDC"] = r("adresse_ville_ancien nom_TDC")
    # if len(ville_TDC) > 0:
    #     adresse_TDC["ville_TDC"] = ville_TDC

    # # pays
    # pays = {}
    # if r("adresse_pays"):
    #     pays["nom"] = r("adresse_pays")
    # if len(pays) > 0:
    #     adresse["pays"] = pays

    # if adresse and adresse not in adresses:
    #     adresses.append(adresse)
    # if adresse_TDC and adresse_TDC not in adresses_TDC:
    #     adresses_TDC.append(adresse_TDC)

    # # dédoublonnage et recensement
    # if "adresses" not in eleve and len(adresses) > 0:
    #     eleve["adresses"] = adresses
    # if "adresses_TDC" not in eleve and len(adresses_TDC) > 0:
    #     eleve["adresses_TDC"] = adresses_TDC