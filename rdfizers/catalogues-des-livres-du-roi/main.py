import argparse
import json
import re
from sherlockcachemanagement import Cache
from iremusdocutils import Ikselesix

#
# PREP
#

parser = argparse.ArgumentParser()
parser.add_argument('--xlsx1')
parser.add_argument('--xlsx2')
parser.add_argument('--photos')
parser.add_argument('--cache')
parser.add_argument('--json')
args = parser.parse_args()

cache = Cache(args.cache)

data = {'livrets': {}, 'motets': {}, 'compositeurs': {}, 'auteurs': {}}

#
# HELPERS
#


def replace_pairs(_, a, b1, b2):
    __ = _.split(a)
    res = []
    next = b1
    for ___ in __:
        res.append(___)
        res.append(next)
        if next == b1:
            next = b2
        elif next == b2:
            next = b1
    res = res[:-1]
    res = ''.join(res)
    return res


def superscriptize_number(_):
    _ = _.replace('1', '¹')
    _ = _.replace('2', '²')
    _ = _.replace('3', '³')
    _ = _.replace('4', '⁴')
    _ = _.replace('5', '⁵')
    _ = _.replace('6', '⁶')
    _ = _.replace('7', '⁷')
    _ = _.replace('8', '⁸')
    _ = _.replace('9', '⁹')
    return _


def format_value(_):
    if not _:
        return None
    if type(_) == int:
        return _
    _ = _.replace('^e^', 'ᵉ')
    _ = _.replace('^v^', 'ᵛ')
    _ = _.replace('^0^', '⁰')
    _ = _.replace('^1^', '¹')
    _ = _.replace('^2^', '²')
    _ = _.replace('^3^', '³')
    _ = _.replace('^4^', '⁴')
    _ = _.replace('^5^', '⁵')
    _ = _.replace('^6^', '⁶')
    _ = _.replace('^7^', '⁷')
    _ = _.replace('^8^', '⁸')
    _ = _.replace('^9^', '⁹')
    _ = _.replace('^re^', 'ʳᵉ')
    _ = _.replace(' :', ' :')
    _ = _.replace('« ', '« ')
    _ = _.replace(' »', ' »')
    _ = re.sub(r'([0-9]{4})–([a-zA-Z])', r'\1–\2', _)
    if '$' in _:
        _ = replace_pairs(_, '$', '<em>', '</em>')
    return _


def format_description_matérielle(_):
    __ = _.split('Sig.')
    if len(__) >= 2:
        __[1] = re.sub(r'([0-9])', lambda m: superscriptize_number(m.group()), __[1])
    return 'Sig.'.join(__)


# TODO
def make_titre_forgé(titre, identifiant, compositeurs):
    compositeurs_patronymes = list(sorted(map(lambda c: data['compositeurs'][c]['patronyme'], compositeurs)))

    tf = ' '.join([_.strip() for _ in titre.split('/')])
    tf = tf.replace(', Imprimés par Ordre de Sa Majesté', '')
    tf = tf.replace(', Imprimez par l\'ordre de sa Majesté.', '')
    tf = tf.replace(', Imprimez par Ordre de Sa Majesté', '')
    tf = tf.replace(', Imprimés par Ordre de Sa Majésté [sic].', '')
    tf = tf.replace(', imprimez par ordre de Sa Majesté.', '')
    tf = tf.replace(', imprimés par Ordre de Sa Majesté.', '')
    tf = tf.replace(', par ordre de Sa Majesté.', '')
    tf = tf.replace('. Imprimez par l’ordre de Sa Majesté.', '')
    tf = tf.replace(' ; Imprimés par Ordre de Sa Majesté.', '')
    tf = tf.replace(' ; Imprimez par Ordre de Sa Majesté.', '')
    tf = tf.replace('MOTETS POUR LA CHAPELLE DU ROY', 'Motets pour la Chapelle du Roy',)
    tf = tf.replace('MOTETS POUR LA CHAPELLE DU ROI', 'Motets pour la Chapelle du Roi',)
    tf = tf.replace('MOTETS ET ELEVATIONS POUR LA CHAPELLE DU ROY', 'Motets et élévations pour la Chapelle du Roy')
    tf = tf.replace('Motets pour la chapelle du Roy', 'Motets pour la Chapelle du Roy')
    tf = tf.replace('MOTETS, ET ELEVATIONS DE M. DU MONT', 'Motets, et élévations de M. Du Mont')
    tf = tf.replace('MOTETS ET ELEVATIONS DE M. DU MONT', 'Motets et élévations de M. Du Mont')
    tf = tf.replace('MOTETS, ET ELEVATIONS DE M. ROBERT', 'Motets, et élévations de M. Robert')
    tf = tf.replace('MOTETS, ET ELEVATIONS DE M. DV MONT.', 'Motets, et élévations de M. Dv Mont.')
    tf = tf.replace('MOTETS, ET ELEVATIONS DE M. EXPILLY', 'Motets, et élévations de M. Expilly')
    tf = tf.strip()
    while '  ' in tf:
        tf = tf.replace('  ', ' ')
    tf = tf.replace(' .', '.')
    if tf[-1] == '.':
        tf = tf[:-1]
    tf = tf.replace('. Q', ', q')
    tf = tf.replace('Roy Quartier', 'roy, quartier')
    tf = tf.replace('Roy QUARTIER', 'roy, quartier')
    tf = tf.replace('qUARTIER', 'quartier')
    tf = tf.replace('. Pour le quartier', ', quartier')
    tf = tf.replace('. Pour le Quartier', ', quartier')
    tf = tf.replace(' pour le quartier', ', quartier')
    tf = tf.replace(',,', ',')
    tf = identifiant + ' — ' + tf
    tf = tf.replace('[', '')
    tf = tf.replace(']', '')
    tf = tf + ' (' + ', '.join(compositeurs_patronymes) + ')'
    return tf


def process_livret(_):
    global data

    id = _['Identifiant']
    sherlock_uuid = cache.get_uuid(['livrets', id, 'uuid'], True)

    d = {
        'sherlock_uuid': sherlock_uuid,
        'compositeurs': [],
        'parties': {}
    }

    for k, v in _.items():
        if k == 'Identifiant':
            d['identifiant'] = v.replace('-', '–')
        elif k == 'Description matérielle':
            v = format_description_matérielle(v)
            v = format_value(v)
            d[k] = v
        elif k == 'Compositeur 1' or k == 'Compositeur 2' or k == 'Compositeur 3':
            comp = process_dude(v, 'compositeurs')
            if comp:
                d['compositeurs'].append(comp)
        else:
            d[k] = format_value(v)

    data['livrets'][id] = d


def process_partie(_):
    global data

    id = _['ID partie']
    sherlock_uuid = cache.get_uuid(['livrets', _['ID livret'], 'parties', id, 'uuid'], True)

    d = {
        'sherlock_uuid': sherlock_uuid,
        'instanciations': []
    }

    for k, v in _.items():
        if k == 'ID livret':
            pass
        elif k == 'ID partie':
            d['id'] = v
        else:
            d[k] = format_value(v)

    data['livrets'][_['ID livret']]['parties'][id] = d


def process_instanciation(_):
    global data

    d = {
        'motet_sherlock_uuid': cache.get_uuid(['motets', _['ID motet'], 'uuid'], True)
    }

    for k, v in _.items():
        if k == 'ID livret':
            pass
        elif k == 'ID partie':
            pass
        else:
            d[k] = format_value(v)

    compositeur = data['motets'][d['ID motet']]['Compositeur']
    if compositeur not in data['livrets'][_['ID livret']]['compositeurs']:
        data['livrets'][_['ID livret']]['compositeurs'].append(compositeur)

    data['livrets'][_['ID livret']]['parties'][_['ID partie']]['instanciations'].append(d)


def process_motet(_):
    global data

    id = _['ID']
    sherlock_uuid = cache.get_uuid(['motets', id, 'uuid'], True)

    d = {
        'sherlock_uuid': sherlock_uuid,
    }

    for k, v in _.items():
        if k == 'ID':
            d['id'] = v
        elif k == 'Compositeur':
            d[k] = process_dude(v, 'compositeurs')
        elif k == 'Auteur du texte':
            d[k] = process_dude(v, 'auteurs')
        else:
            d[k] = format_value(v)

    data['motets'][id] = d


def process_dude(_, branch):
    global data

    if not _:
        return None

    __ = _.split(' (')
    année_naissance = None
    année_mort = None
    if '(' in _:
        dates = __[1].replace(')', '')
        année_naissance = dates.split('-')[0]
        année_mort = dates.split('-')[1]
    nom = __[0]
    nom = nom.strip()
    patronyme = nom.split(',')[0]
    prénom = nom.split(', ')[1].split(' de')[0]
    particule = 'de' if ' de' in _ else None
    sherlock_uuid = cache.get_uuid([branch, nom, 'uuid'], True)

    data[branch][sherlock_uuid] = {
        'patronyme': patronyme,
        'prénom': prénom,
        'particule': particule,
        'année_naissance': année_naissance,
        'année_mort': année_mort,
        'sherlock_uuid': sherlock_uuid
    }

    return sherlock_uuid

#
# EXPLORE
#


xlsx1 = Ikselesix(args.xlsx1)
xlsx2 = Ikselesix(args.xlsx2)

for motet in xlsx1['Motets']:
    process_motet(motet)
for motet in xlsx2['Motets']:
    process_motet(motet)
for livret in xlsx1['Livrets']:
    process_livret(livret)
for livret in xlsx2['Livrets']:
    process_livret(livret)
for partie in xlsx1['Parties']:
    process_partie(partie)
for partie in xlsx2['Parties']:
    process_partie(partie)
for instanciation in xlsx1['Instanciations']:
    process_instanciation(instanciation)
for instanciation in xlsx2['Instanciations']:
    process_instanciation(instanciation),

# titres forgés

for id_livret, livret in data['livrets'].items():
    tf = make_titre_forgé(livret['Titre'], livret['identifiant'], livret['compositeurs'])
    livret['titre_forgé'] = tf

#
# THAT'S ALL FOLKS!
#

with open(args.json, 'w', encoding='utf8') as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=4)

cache.bye()
