"""SPAQRL Wrapper for different SPARQL Endpoints."""

import os
import pathlib
import json
from SPARQLWrapper import SPARQLWrapper, GET, POST, JSON  # noqa


class Sparql:
    """Custom SPARQL Wrapper Class for different SPARQL Endpoints."""

    def __init__(
        self,
        method=GET,
        return_format=JSON,
        endpoint="https://www.qudt.org/fuseki/qudt/sparql",
        src_filepath="",
        tgt_filepath="",
        debug=False,
        query="",
    ):
        """Constructor to initialize the SPARQL Wrapper."""
        self.sparql_method = method
        self.sparql_return_format = return_format
        self.sparql_endpoint = endpoint
        self.src_filepath = src_filepath
        self.tgt_filepath = tgt_filepath
        self.debug = debug
        # Read the SPARQL query from a file if a file path is provided
        if self.src_filepath:
            self.sparql_query = self.readSparqlFile()
        else:
            print("Using the provided SPARQL Query...")
            self.sparql_query = query

    def execQuery(self):
        """Execute SPARQL query and return the result."""
        if self.debug:
            print(
                f"Executing SPARQL query {os.path.abspath(self.src_filepath)}"
            )
            print(f"on endpoint {self.sparql_endpoint} ...")
        sparql = SPARQLWrapper(self.sparql_endpoint)
        sparql.setMethod(self.sparql_method)
        sparql.setQuery(self.sparql_query)
        sparql.setReturnFormat(self.sparql_return_format)
        result = sparql.query().convert()
        if self.debug:
            print(
                f'...fetched {len(result["results"]["bindings"])} JSON objects.'
            )

        return result

    def readSparqlFile(self):
        """
        Reads the content of a .sparql file in an OS-independent manner.

        Returns:
        str: The content of the file if successful, or None if an error occurs.
        """
        try:
            # Check if path is a relative or absolute path
            if not os.path.isabs(self.src_filepath):
                basedir = pathlib.Path(__file__).parent
                src_filepath = os.path.join(basedir, self.src_filepath)

            # Ensure the path is OS independent
            # print(f"Reading SPARQL Query from {src_filepath}")
            normalizedPath = os.path.normpath(src_filepath)

            # Check if the file has a .sparql suffix
            if not normalizedPath.endswith(".sparql"):
                raise ValueError("File does not have a .sparql suffix")

            # Read the file
            with open(normalizedPath, "r") as file:
                content = file.read()
            # if self.debug:
            #     print(f"File content:\n{content}")
            return content

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def writeJsonFile(self, data={}):
        """
        Writes the given data to a .json file in an OS-independent manner.

        Parameters:
        data (dict): The data to write to the file.
        """
        try:
            # Check if path is a relative or absolute path
            if not os.path.isabs(self.tgt_filepath):
                basedir = pathlib.Path(__file__).parent
                tgt_filepath = os.path.join(basedir, self.tgt_filepath)
            else:
                tgt_filepath = self.tgt_filepath

            # Ensure the path is OS independent
            print(f"Writing JSON data to {tgt_filepath}")
            normalizedPath = os.path.normpath(tgt_filepath)

            # Check if the file has a .json suffix
            if not normalizedPath.endswith(".json"):
                raise ValueError("File does not have a .json suffix")

            # Write the file
            with open(normalizedPath, "w") as file:
                json.dump(data, file, indent=4)

            if self.debug:
                print(f"Data successfully written to {normalizedPath}")

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    from pprint import pprint

    # Qudt instance
    sparql_qudt = Sparql(
        endpoint="https://www.qudt.org/fuseki/qudt/sparql",
        src_filepath="../ontology/qudt/sparql/quantitykind.sparql",
        debug=False,
    )
    qudt_qk = sparql_qudt.execQuery()
    # pprint(qudt_qk)

    # Wikidata instance
    sparql_wikidata = Sparql(
        endpoint="https://query.wikidata.org/sparql",
        src_filepath="../ontology/wikidata/sparql/quantitykind.sparql",
        debug=False,
    )
    wikidata_qk = sparql_wikidata.execQuery()
    # pprint(wikidata_qk)

    # OM2 instance
    sparql_om2 = Sparql(
        method=POST,
        # endpoint="http://www.ontology-of-units-of-measure.org/resource/om-2/",
        endpoint="https://fuseki.sysmon.digital.isc.fraunhofer.de/om2/sparql",
        src_filepath="../ontology/om2/sparql/dimension.sparql",
        debug=True,
    )
    om2_qk = sparql_om2.execQuery()

    pprint(om2_qk)
