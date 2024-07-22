"""Entrypoint for the quantities-units package app."""

from utils.file_loader import readSparqlFile
from utils.sparql_query import execQuery


def main():
    """Main entrypoint for the quantities-units app."""
    print("Reading SPARQL Query File...")
    query = readSparqlFile("queries/quantity_units.sparql")
    if query:
        print("Executing SPARQL Query...")
        execQuery(query, debug=True)


if __name__ == "__main__":
    main()
