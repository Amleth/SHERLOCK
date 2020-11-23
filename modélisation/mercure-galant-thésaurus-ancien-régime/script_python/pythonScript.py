from lxml import etree
import uuid
import os

# Document turtle
turtle = open("pythonScript_output.ttl", "w+")

##################################################################
#### ECRITURE DU TURTLE
###################################################################

# Prefixes

turtle.write(
    """
@base <http://data-iremus.huma-num.fr/id/> .

@prefix crm: <http://www.cidoc-crm.org/cidoc-crm/> .
@prefix crmdig: <http://www.ics.forth.gr/isl/CRMdig/> .
@prefix lrmoo: <http://www.cidoc-crm.org/lrmoo/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sdt: <http://data-iremus.huma-num.fr/datatypes/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""
)

# Serial Work

turtle.write(
    """
################################################################################
# Le Mercure Galant
################################################################################

<4997648d-7ba3-4092-858e-b1c3bebe206b> 
    a lrmoo:F18_Serial_Work ; 
    crm:P1_is_identified_by "Mercure Galant" ;
    lrmoo:R10_has_member """
)

# Livraisons

dir = "c://Users/rebecca/Documents/GitHub/SHERLOCK/modélisation/mercure-galant-thésaurus-ancien-régime/script_python/livraisons"
for file in os.listdir(dir):
    livraison_work_uuid = uuid.uuid4()
    livraison_expression_uuid = uuid.uuid4()
    with open(os.path.join(dir, file), "r", encoding="utf-8") as livraison:
        xml = etree.parse(livraison)
        root = xml.getroot()
        for text_tag in root.iter("{http://www.tei-c.org/ns/1.0}text"):
            livraison_titre = text_tag[0][0][0][0].text
            livraison_titre2 = text_tag[0][0][0].text
    turtle.write("<" + str(livraison_work_uuid) + ">, ")

turtle.write(
    """ ;
    .
    
<0520c87e-8f8c-4bbf-b205-4631242a8cd6>
    a crm:E21_Person ;
    crm:p1_is_identified_by "Jean Donneau de Visé" ;
    .
    
<d66f5afc-0e6a-41f8-88cb-ed8960634ca8>
    a lrmoo:F27_Work_Conception ;
    crm:P14_carried_out_by <0520c87e-8f8c-4bbf-b205-4631242a8cd6> ;
    .
"""
)

turtle.write(
    """
################################################################################
# Une livraison
################################################################################
             
             """
)

for file in os.listdir(dir):
    turtle.write(
        "<"
        + str(livraison_work_uuid)
        + '''>
        a lrmoo:F1_Work ;
        crm:P1_is_identified_by "'''
        + str(livraison_titre)
        + " "
        + str(livraison_titre2)
        + """"
        lrmoo:R3_is_realised_in ;
        lrmoo:R10_has_member ;
        
        .
        """
    )
