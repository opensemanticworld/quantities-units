"""Entrypoint for the quantities-units app."""

from osw.core import OSW
from osw.express import OswExpress
from utils.prefixes import SiPrefixes
from utils.ontology import Ontology
from utils.sparql_wrapper import Sparql


# Initially update the local OSW model with the required schemas
def update_local_osw(osw_obj=None) -> None:
    """Update local OSW with the required schemas."""
    # Check if the OSW object is provided
    if osw_obj is None:
        raise ValueError("OSW object is required for updating the local OSW.")
    # Define the required schemas
    required_schemas = [
        "Category:OSW99e0f46a40ca4129a420b4bb89c4cc45",  # Unit prefix
        "Category:OSWd2520fa016844e01af0097a85bb25b25",  # Quantity Unit
        "Category:OSW00fbd6feecb5408997ca18d4e681a131",  # Quantity Kind
        "Category:OSW268cc84d3dff4a7ba5fd489d53254cb0",  # Composed Quantity Unit with Unit Prefix (Ausreiser)
        "Category:OSWffe74f291d354037b318c422591c5023",  # Characteristic Type
        "Category:OSW4082937906634af992cf9a1b18d772cf",  # Quantity Value
        "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7",  # Meta Fundamental Quantiy Value
    ]
    osw_obj.fetch_schema(
        OSW.FetchSchemaParam(
            schema_title=required_schemas,
            mode="replace",
        )
    )


# I: Exctract Data
def extract_data(debug: bool = False) -> Ontology:
    """Extract unit prefixes from SI Digital Framework."""
    # Initialize Prefixes
    prefixes = SiPrefixes()
    # Initialize Sparql QUDT Units and QuantityKinds
    sparql_qudt_units = Sparql(
        endpoint="https://www.qudt.org/fuseki/qudt/sparql",
        src_filepath="../ontology/qudt/sparql/units.sparql",
        tgt_filepath="../ontology/qudt/data/units.json",
        debug=debug,
    )
    sparql_qudt_quantities = Sparql(
        endpoint="https://www.qudt.org/fuseki/qudt/sparql",
        src_filepath="../ontology/qudt/sparql/quantitykind.sparql",
        tgt_filepath="../ontology/qudt/data/quantitykind.json",
        debug=debug,
    )
    _prefixes = prefixes.get_prefixes_json()
    _prefix_name_list = prefixes.get_prefix_name_list()
    _qudt_units = sparql_qudt_units.execQuery()
    _qudt_quantities = sparql_qudt_quantities.execQuery()
    # Initialize Ontology for transformation
    osw_ontology = Ontology(
        prefixes_json=_prefixes,
        prefix_name_list=_prefix_name_list,
        qudt_units=_qudt_units,
        qudt_quantity_kinds=_qudt_quantities,
        debug=debug,
    )
    return osw_ontology


# II: Transform Data
def transform_data(osw_ontology: Ontology = None):
    """Transform exctracted data into osw compatible format."""
    # Transform Prefixes
    osw_prefix_obj_list = osw_ontology.get_osw_prefix_obj_list()
    # Transform Quantity Units
    osw_quanity_unit_obj_list = osw_ontology.get_osw_quantity_unit_obj_list(
        composed_units=False
    )
    # Transform Composed Quantity Units with Unit Prefixes
    osw_composed_prefix_quantity_unit_obj_list = (
        osw_ontology.get_osw_quantity_unit_obj_list(composed_units=True)
    )
    # Transform QuantityKind and Characteristics
    osw_quantity_kind_obj_list, osw_characteristic_obj_list = (
        osw_ontology.get_osw_quantitykind_characteristics_obj_list()
    )
    # TODO: Define Pydantic Model?
    list_of_osw_obj_lists = [
        osw_prefix_obj_list,
        osw_quanity_unit_obj_list,
        osw_composed_prefix_quantity_unit_obj_list,
        osw_quantity_kind_obj_list,
        osw_characteristic_obj_list,
    ]
    return list_of_osw_obj_lists


# III: Load Data
def load_data(osw_obj=None, list_of_osw_obj_lists: list = None) -> None:
    """Load data into the desired OSW instance."""
    # Check if the list of OSW objects is provided
    if list_of_osw_obj_lists is None or osw_obj is None:
        raise ValueError(
            "OSW object and list of OSW objects is required for loading data."
        )
    # Load data into the OSW instance
    for osw_obj_list in list_of_osw_obj_lists:
        osw_obj.store_entity(
            OSW.StoreEntityParam(
                entities=osw_obj_list,
                overwrite=True,
            )
        )


def main(
    osw_domain="wiki-dev.open-semantic-lab.org",
    auth_upd_osw: bool = False,
    upload: bool = False,
) -> None:
    """Main function."""
    # Authentication and update local OSW model
    if auth_upd_osw:
        osw_obj = OswExpress(
            domain=osw_domain,  # cred_filepath=pwd_file_path
        )
        update_local_osw(osw_obj=osw_obj)

    # I: Exctract Data
    osw_ontology_instance = extract_data(debug=True)
    # II: Transform Data
    list_of_osw_obj_lists = transform_data(osw_ontology=osw_ontology_instance)
    # III: Load Data
    if upload:
        # TODO: To be tested for all sequences
        load_data(list_of_osw_obj_lists)


if __name__ == "__main__":
    main(auth_upd_osw=True, upload=False)
