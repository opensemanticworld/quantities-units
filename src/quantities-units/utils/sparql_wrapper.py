"""SPAQRL Wrapper for different SPARQL Endpoints."""

import os
import pathlib
from SPARQLWrapper import SPARQLWrapper, GET, POST, JSON


class Sparql:
    """Custom SPARQL Wrapper Class for different SPARQL Endpoints."""

    def __init__(
        self,
        method=POST,
        return_format=JSON,
        endpoint="https://www.qudt.org/fuseki/qudt/sparql",
        filepath="",
        debug=False,
        query="",
    ):
        """Constructor to initialize the SPARQL Wrapper."""
        self.sparql_method = method
        self.sparql_return_format = return_format
        self.sparql_endpoint = endpoint
        self.filepath = filepath
        self.debug = debug
        # Read the SPARQL query from a file if a file path is provided
        if self.filepath:
            self.sparql_query = self.readFile()
        else:
            print("Using the provided SPARQL Query...")
            self.sparql_query = query

    def execQuery(self):
        """Execute SPARQL query and return the result."""
        sparql = SPARQLWrapper(self.sparql_endpoint)
        sparql.setMethod(self.sparql_method)
        sparql.setQuery(self.sparql_query)
        sparql.setReturnFormat(self.sparql_return_format)
        result = sparql.query().convert()
        if self.debug:
            print("\nEndpoint: ", self.sparql_endpoint)
            print("\nSPARQL Query: ", self.sparql_query)
            print("Counted JSON Objects: ", len(result["results"]["bindings"]))
            print("\n")
        return result

    def readFile(self):
        """
        Reads the content of a .sparql file in an OS-independent manner.

        Returns:
        str: The content of the file if successful, or None if an error occurs.
        """
        try:
            # Check if path is a relative or absolute path
            if not os.path.isabs(self.filepath):
                basedir = pathlib.Path(__file__).parent
                filepath = os.path.join(basedir, self.filepath)

            # Ensure the path is OS independent
            print(f"Reading SPARQL Query from {filepath}")
            normalizedPath = os.path.normpath(filepath)

            # Check if the file has a .sparql suffix
            if not normalizedPath.endswith(".sparql"):
                raise ValueError("File does not have a .sparql suffix")

            # Read the file
            with open(normalizedPath, "r") as file:
                content = file.read()
            if self.debug:
                print(f"File content:\n{content}")
            return content

        except Exception as e:
            print(f"An error occurred: {e}")
            return None


if __name__ == "__main__":
    from pprint import pprint

    # Qudt instance
    sparql_qudt = Sparql(
        endpoint="https://www.qudt.org/fuseki/qudt/sparql",
        filepath="../ontology/qudt/sparql/quantitykind.sparql",
        debug=False,
    )
    qudt_qk = sparql_qudt.execQuery()
    # pprint(qudt_qk)

    # Wikidata instance
    sparql_wikidata = Sparql(
        endpoint="https://query.wikidata.org/sparql",
        filepath="../ontology/wikidata/sparql/quantitykind.sparql",
        debug=False,
    )
    wikidata_qk = sparql_wikidata.execQuery()
    # pprint(wikidata_qk)

    # OM2 instance
    sparql_om2 = Sparql(
        method=POST,
        # endpoint="http://www.ontology-of-units-of-measure.org/resource/om-2/",
        endpoint="https://fuseki.sysmon.digital.isc.fraunhofer.de/om2/sparql",
        filepath="../ontology/om2/sparql/dimension.sparql",
        debug=True,
    )
    om2_qk = sparql_om2.execQuery()
    pprint(om2_qk)
