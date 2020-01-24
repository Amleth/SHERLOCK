# 📔 Terminologie générale

> IRI IReMus

Une IRI IReMus est associé à chaque objet existant dans le Triplestore, et prend la forme : `http://data-iremus.huma-num.fr/id/<UUID>` (exemple : `http://data-iremus.huma-num.fr/id/ba2968d7-1a4a-4aea-8ca5-19f1648121f7`). Le prefix est donc : `http://data-iremus.huma-num.fr/id/`.

# 🕵️‍♀️ Scénarios d'usage

## 🎼 Production & correction collaborative d'annotations analytiques sur des partitions MEI

### 📔 Terminologie

> Cible (d'une annotation)

Une cible est identifiée par une IRI IReMus, et est associée à un document MEI ainsi qu'à un nombre arbitraire d'`xml:id`

<div class="todo">

Quelle ontologie pour exprimer en RDF les faits suivants :
- Une ressource est une partition MEI.
- Une partition MEI contient un certain nombre d'`xml:id`, et réciproquement, qu'un `xml:id` appartient à une partition MEI.
</div>

> Annotation

Sur le plan technique, une annotation est un ensemble de triplets RDF associés à une **cible**, qui en constitue le sujet.

<hr/>

🏮 [VIEW](https://amleth.github.io/SHERLOCK/)
⛩ [EDIT](https://github.com/Amleth/SHERLOCK/blob/master/docs/index.md)

<style type="text/css" rel="stylesheet">
@import url("https://indestructibletype.com/fonts/Jost.css");
:root {
    --todo-color-b: #035;
    --todo-color-f: aquamarine;
}
html {
    font-family: Jost;
}
.todo {
    background-color: var(--todo-color-b);
    border-left: 10px solid var(--todo-color-f);
    color: var(--todo-color-f);
    margin: 2em;
    padding: 0.5em 0.5em 0.1em 1em;
}
.todo:before {
    color: white;
    content: 'TODO';
    font-family: monospace;
    font-size: 150%;
    font-weight: bold;
    letter-spacing: 3px;
}
</style>