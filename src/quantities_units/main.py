"""Entrypoint for the quantities_units app."""

from osw.core import OSW
from osw.express import OswExpress
from quantities_units.utils.prefixes import SiPrefixes
from quantities_units.utils.ontology import Ontology
from quantities_units.utils.sparql_wrapper import Sparql


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
        "Category:OSW268cc84d3dff4a7ba5fd489d53254cb0",  # Composed Quantity Unit with Unit Prefix (Outliers)
        "Category:OSWffe74f291d354037b318c422591c5023",  # Characteristic Type
        "Category:OSW4082937906634af992cf9a1b18d772cf",  # Quantity Value
        "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7",  # Fundamental Quantiy Value Type
        "Category:OSWac07a46c2cf14f3daec503136861f5ab",  # Quantiy Value Type
        "Category:OSW1b15ddcf042c4599bd9d431cbfdf3430",  # Main Quantity Property
        "Category:OSW69f251a900944602a08d1cca830249b5",  # Sub Quantity Property 
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
    # Initialize Ontology for transformation
    osw_ontology = Ontology(
        prefixes_json=prefixes.get_prefixes_json(),
        prefix_name_list=prefixes.get_prefix_name_list(),
        qudt_units=sparql_qudt_units.execQuery(),
        qudt_quantity_kinds=sparql_qudt_quantities.execQuery(),
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
    osw_quantity_kind_obj_list, osw_fundamental_characteristic_list, osw_characteristic_obj_list = (
        osw_ontology.get_osw_quantitykind_characteristics_obj_list()
    )
    list_of_osw_obj_dict = {
        "prefixes": osw_prefix_obj_list,
        "quanity_units": osw_quanity_unit_obj_list,
        "composed_prefix_quantity_units": osw_composed_prefix_quantity_unit_obj_list,
        "quantity_kinds": osw_quantity_kind_obj_list,
        "fundamental_characteristics": osw_fundamental_characteristic_list,
        "characteristics": osw_characteristic_obj_list,
    }
    
    osw_ontology.create_smw_quantity_properties(list_of_osw_obj_dict=list_of_osw_obj_dict)
    
    return list_of_osw_obj_dict


# III: Load Data
def load_data(osw_obj=None, list_of_osw_obj_dict: dict = None, change_id=None) -> None:
    """Load data into the desired OSW instance."""
    # Check if the list of OSW objects is provided
    if list_of_osw_obj_dict is None or osw_obj is None:
        raise ValueError(
            "OSW object and list of OSW objects is required for loading data."
        )
    
    # Load data into the OSW instance
    # re-defining the list_of_osw_obj_dict for a selective include
    list_of_osw_obj_dict = {
        "prefixes": list_of_osw_obj_dict["prefixes"],
        "quanity_units": list_of_osw_obj_dict["quanity_units"],
        "composed_prefix_quantity_units": list_of_osw_obj_dict["composed_prefix_quantity_units"],
        "quantity_kinds": list_of_osw_obj_dict["quantity_kinds"],
        "fundamental_characteristics": list_of_osw_obj_dict["fundamental_characteristics"],
        "characteristics": list_of_osw_obj_dict["characteristics"],
    }
    for key, osw_obj_list in list_of_osw_obj_dict.items():
        # Define the namespace
        namespace = None
        meta_category_title = None
        if key == "fundamental_characteristics": 
            namespace = "Category"
            # FundamentalQuantityValueType
            meta_category_title = "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7"
        if key == "characteristics": 
            namespace = "Category"
            # QuantityValueType
            meta_category_title = "Category:OSWac07a46c2cf14f3daec503136861f5ab"
        osw_obj.store_entity(
            OSW.StoreEntityParam(
                entities=osw_obj_list,
                overwrite=True,
                change_id=change_id,
                namespace=namespace,
                meta_category_title=meta_category_title
            )
        )

def create_smw_quantity_properties(list_of_osw_obj_dict):
    return Ontology.create_smw_quantity_properties(list_of_osw_obj_dict=list_of_osw_obj_dict)

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
    list_of_osw_obj_dict = transform_data(osw_ontology=osw_ontology_instance)
    # III: Load Data
    if upload:
        load_data(
            osw_obj=osw_obj,
            list_of_osw_obj_dict=list_of_osw_obj_dict,
            change_id="50d1ad0b-8d58-4751-aab5-584d1741e98d", # Random generated change_id
        )


if __name__ == "__main__":
    main(auth_upd_osw=True, upload=True)
