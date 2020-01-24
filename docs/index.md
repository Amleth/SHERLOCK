# 📔 Terminologie générale

> IRI IReMus

Une IRI IReMus est associé à chaque objet existant dans le Triplestore, et prend la forme : `http://data-iremus.huma-num.fr/id/<UUID>` (exemple : `http://data-iremus.huma-num.fr/id/ba2968d7-1a4a-4aea-8ca5-19f1648121f7`). Le prefix est donc : `http://data-iremus.huma-num.fr/id/`.

# 🌆 Scénarios d'usage

## 🎼 Production & correction collaborative d'annotations analytiques sur des partitions MEI

### 📔 Terminologie

> Cible (d'une annotation)

Une cible est identifiée par une IRI IReMus, et est associée à un document MEI ainsi qu'à un nombre arbitraire d'`xml:id`

🤔 *Quelle ontologie pour exprimer en RDF les faits suivants : 1) Une ressource est une partition MEI. 2) Une partition MEI contient un certain nombre d'`xml:id`, et réciproquement, qu'un `xml:id` appartient à une partition MEI.*

> Annotation

Sur le plan technique, une annotation est un ensemble de triplets RDF associés à une **cible**, qui en constitue le sujet.

<hr/>

🗿 [VIEW](https://amleth.github.io/SHERLOCK/)
🏮 [EDIT](https://github.com/Amleth/SHERLOCK/blob/master/docs/index.md)

<style type="text/css" rel="stylesheet">
@import url("https://indestructibletype.com/fonts/Jost.css");
body {
    font-family: Jost !important;
}
</style>