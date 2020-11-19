from lxml import etree
import uuid
#import io
#from io import StringIO

#Document turtle
turtle = open('pythonScript_output.ttl', 'w+')

#Document TEI
livraison = 'MG_1681.xml'
tei = etree.parse(livraison)
root = tei.getroot()
for text_tag in root.iter('{http://www.tei-c.org/ns/1.0}text'):
    livraison_titre = text_tag[0][0][0][0].text
    livraison_titre2 = text_tag[0][0][0].text

#Serial_Work
uuid = uuid.uuid1()
triplet = """
<""" + str(uuid) + """> 
    a lrmoo:F18_Serial_Work ; 
    crm:P1_is_identified_by """ + '''"''' + str(livraison_titre) + """ """ + str(livraison_titre2) + '''"'''

print(triplet.strip())

#Ecriture du turtle

turtle.write("""

@prefix crm: <http://www.cidoc-crm.org/cidoc-crm/> .
@prefix crmdig: <http://www.ics.forth.gr/isl/CRMdig/> .
@prefix lrmoo: <http://www.cidoc-crm.org/lrmoo/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sdt: <http://data-iremus.huma-num.fr/datatypes/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

################################################################################
# Le Mercure Galant
################################################################################

"""

+ triplet.strip())

