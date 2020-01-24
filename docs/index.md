[VIEW](https://amleth.github.io/SHERLOCK/) <br/>
[EDIT](https://github.com/Amleth/SHERLOCK/blob/master/docs/index.md)

# Terminologie générale

> IRI IReMus

Une IRI IReMus est associé à chaque objet existant dans le Triplestore, et prend la forme : `http://data-iremus.huma-num.fr/id/<UUID>` (exemple : `http://data-iremus.huma-num.fr/id/ba2968d7-1a4a-4aea-8ca5-19f1648121f7`). Le prefix est donc : `http://data-iremus.huma-num.fr/id/`.

# Scénarios d'usage

## Production & correction collaborative d'annotations analytiques sur des partitions

### Terminologie

> Annotation

Sur le plan technique, une annotation est un ensemble de triplets RDF associés à une cible (voir infra), qui en constitue le sujet.

> Cible (d'une annotation)