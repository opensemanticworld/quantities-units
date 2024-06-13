from SPARQLWrapper import SPARQLWrapper, POST, JSON


class Quantities:
    def __init__(self):
        """Constructor"""
        self.sparql_method = POST
        self.sparql_return_format = JSON
        self.sparql_endpoint = "https://www.qudt.org/fuseki/qudt/sparql"
        self.sparql_query = """
            PREFIX qudt: <http://qudt.org/schema/qudt/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX sou: <http://qudt.org/vocab/sou/>

            SELECT 	?quantity
                (GROUP_CONCAT(DISTINCT CONCAT(?qlabel, "@", LANG(?qlabel)); separator=", ") AS ?qlabels)
                (GROUP_CONCAT(DISTINCT ?applicableUnit; separator=", ") AS ?applicableUnits)
                    (GROUP_CONCAT(DISTINCT ?ucumCode; separator=", ") AS ?ucumCodes)
            WHERE {
                ?quantity rdf:type qudt:QuantityKind .
                ?quantity rdfs:label ?qlabel .
                ?quantity qudt:applicableUnit ?applicableUnit .
                ?applicableUnit qudt:applicableSystem sou:SI .
                ?applicableUnit qudt:ucumCode ?ucumCode .
            }
            GROUP BY ?quantity
            """

    def sparqlQuery(self, debug=False):
        """Execute SPARQL query"""
        sparql = SPARQLWrapper(self.sparql_endpoint)
        sparql.setMethod(self.sparql_method)
        sparql.setQuery(self.sparql_query)
        sparql.setReturnFormat(self.sparql_return_format)
        result = sparql.query().convert()
        if debug:
            print("\nEndpoint: ", self.sparql_endpoint)
            print("\nSPARQL Query: ", self.sparql_query)
            print("Counted JSON Objects: ", len(result["results"]["bindings"]))
            print("\n")
        return result


if __name__ == "__main__":
    q = Quantities()
    q.sparqlQuery(debug=True)
