""" Load SPARQL Query Files """

import os


def load_query_file(file_name):
    """Load SPARQL query file"""
    with open(file_name, "r") as file:
        return file.read()
