curl --data-urlencode "query=
PREFIX meiplus: <http://data-iremus.huma-num.fr/ns/meiplus#>
SELECT ?pitch (COUNT(*) as ?count)
WHERE {
    GRAPH ?g {
        ?s meiplus:element 'note' .
        ?s meiplus:pname ?pitch .
    }
}
GROUP BY ?pitch
" http://localhost:3030/iremus/sparql