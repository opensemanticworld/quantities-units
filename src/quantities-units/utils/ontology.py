"""Implementation of Ontology class for handling ontology related operations."""

import os
import uuid
import json
import osw.model.entity as model
from jsonpath_ng.ext import parse
from prefixes import SiPrefixes
from sparql_wrapper import Sparql


class Ontology:
    """
    Ontology class for handling ontology related operations
    about prefixes, units, quantities, and characteristics.
    """

    def __init__(
        self,
        prefixes_json=None,
        prefix_name_list=None,
        qudt_quantity_kinds=None,
        qudt_units=None,
        debug=False,
    ):
        """Initialize the Ontology class."""
        # Check if all the parameters are provided
        if (
            prefixes_json is None
            or prefix_name_list is None
            or qudt_quantity_kinds is None
            or qudt_units is None
        ):
            exception_message = "Please provide all the parameters."
            raise Exception(exception_message)
        self.prefixes_json = prefixes_json
        self.prefix_name_list = prefix_name_list
        self.qudt_quantity_kinds = qudt_quantity_kinds
        self.qudt_units = qudt_units
        self.debug = debug

    def export_osw_obj_json(
        self, osw_obj_list=None, ontology_name=None, file_name=None
    ):
        """Function to export a list of OSW objects to a JSON file."""
        # Check if all the parameters are provided
        if osw_obj_list is None or ontology_name is None or file_name is None:
            exception_message = "Please provide all the parameters."
            raise Exception(exception_message)
        else:
            # Convert the OSW objects to JSON serializable format
            osw_obj_json_dumpable = [
                json.loads(osw_obj.json()) for osw_obj in osw_obj_list
            ]
            # Convert the JSON serializable format to JSON
            osw_obj_json_dump = json.dumps(osw_obj_json_dumpable, indent=4)
            # Write the JSON to a file
            if not file_name.endswith(".json"):
                file_name += ".json"
            with open(
                os.path.join(
                    os.path.abspath(
                        ""
                    ),  # https://stackoverflow.com/a/54376484
                    "ontology",
                    ontology_name,
                    "data",
                    file_name,
                ),
                "w",
            ) as f:
                f.write(osw_obj_json_dump)

    def split_prefixed_applicable_units(
        self, applicable_units_str=None, prefix_name_list=None, debug=False
    ):
        """Function to split the applicable units into prefixed and non-prefixed units."""
        # Check that parameters are provided
        if applicable_units_str is None or prefix_name_list is None:
            exception_message = "Please provide all the parameters."
            raise Exception(exception_message)
        non_prefixed_units = []
        prefixed_units = []
        for unit_str in applicable_units_str.split(", "):

            if debug:
                print(unit_str)
                print(
                    self.get_unit_prefix(
                        unit_str=unit_str, prefix_name_list=prefix_name_list
                    )
                )
            if (
                self.get_unit_prefix(
                    unit_str=unit_str, prefix_name_list=prefix_name_list
                )
                == None
            ):
                if debug:
                    print("no prefix: ", unit_str)
                non_prefixed_units.append(unit_str)
            else:
                if debug:
                    print(
                        "prefix: ",
                        self.get_unit_prefix(
                            unit_str=unit_str,
                            prefix_name_list=prefix_name_list,
                        ),
                        "found in ",
                        unit_str,
                    )
                prefixed_units.append(unit_str)
        return non_prefixed_units, prefixed_units

    def get_unit_dict(self, quantity_kinds=None, prefix_name_list=None):
        """Function to extract units as dictionary from quantity kind."""
        # Check that parameters are provided
        if quantity_kinds is None or prefix_name_list is None:
            exception_message = "Please provide all the parameters."
            raise Exception(exception_message)
        unit_dict = {}
        all_prefixed_units = []
        all_non_prefixed_units = []
        quant_kind_list = quantity_kinds["results"]["bindings"]
        all_non_prefixed_units = []
        for quantity in quant_kind_list:
            non_prefixed, prefixed = self.split_prefixed_applicable_units(
                applicable_units_str=quantity["applicableUnits"]["value"],
                prefix_name_list=prefix_name_list,
            )
            all_prefixed_units = all_prefixed_units + prefixed
            all_non_prefixed_units = all_non_prefixed_units + non_prefixed

        all_prefixed_units = list(set(all_prefixed_units))
        all_non_prefixed_units = list(set(all_non_prefixed_units))
        unit_dict = self.merge_prefixed_and_non_prefixed_units(
            all_non_prefixed_units, all_prefixed_units, prefix_name_list
        )
        return unit_dict

    def get_path(self, url):
        """Function to extract the path from a URL."""
        return url.split("/")[-1]

    def get_main_string(self, unit_str=None, prefix_name_list=None):
        # Check that parameters are provided
        if unit_str is None or prefix_name_list is None:
            exception_message = "Please provide all the parameters."
            raise Exception(exception_message)
        for prefix in prefix_name_list:
            capitalized_prefix = prefix.capitalize()
            if capitalized_prefix in unit_str:
                return unit_str.replace(capitalized_prefix, "")
        return unit_str

    def merge_prefixed_and_non_prefixed_units(
        self, all_non_prefixed_units, all_prefixed_units, prefix_name_list
    ):
        """Function to merge prefixed and non-prefixed units."""
        unit_dict = {}
        for non_prefixed_unit in all_non_prefixed_units:
            prefixed_units = []
            # Match the non prefixed unit with all the prefixed units
            for prefixed_unit in all_prefixed_units:
                if self.get_path(non_prefixed_unit) == self.get_main_string(
                    self.get_path(prefixed_unit), prefix_name_list
                ):
                    prefixed_units.append(prefixed_unit)
            unit_dict[non_prefixed_unit] = {"prefixed_units": prefixed_units}

        return unit_dict

    def match_json_path_key(self, qudt_units_param_res, identifier="", key=""):
        """Function to match the JSON key path."""
        jsonpath_expr = parse(
            f'$.results.bindings[?(@.applicableUnit.value = "{identifier}")].{key}.value'
        )
        return jsonpath_expr.find(qudt_units_param_res)[0].value

    def match_object_json_path(self, qudt_units_param_res=None, identifier=""):
        """Function to match the JSON object path."""
        jsonpath_expr = parse(
            f'$.results.bindings[?(@.applicableUnit.value = "{identifier}")]'
        )
        return jsonpath_expr.find(qudt_units_param_res)[0].value

    def dict_from_comma_separated_list(self, qlabel):
        """Function to convert a comma separated list to a dictionary."""
        parts = qlabel.split(", ")
        ret = {}
        for part in parts:
            value, key = part.split("@")
            ret[key] = value
        return ret

    def get_prefix_uuid(self, data=[], prefix=""):
        """Function to get the prefix UUID."""
        jsonpath_expr = parse(f'$[?(@.label = "{prefix}")].pid')
        return uuid.uuid5(
            namespace=uuid.NAMESPACE_URL,
            name=jsonpath_expr.find(data)[0].value,
        )

    def get_unit_prefix(self, unit_str=None, prefix_name_list=None):
        """Function to extract the prefix from a unit string."""
        # Check that parameters are provided
        if unit_str is None or prefix_name_list is None:
            exception_message = "Please provide all the parameters."
            raise Exception(exception_message)
        for prefix in prefix_name_list:
            if prefix in unit_str.lower():
                return prefix
        return None

    # Quantity Units
    # --------------
    def get_osw_prefix_unit(
        self,
        qudt_units_param_res=None,
        prefixes_list=None,
        url=None,
        parent_uuid=None,
        prefix_name_list=None,
    ):

        prefix_unit_dict = self.match_object_json_path(
            qudt_units_param_res=qudt_units_param_res,
            identifier=url,
        )
        # print(prefix_unit_dict)
        ontology_match_list = [prefix_unit_dict["applicableUnit"]["value"]]
        # print("dbpediaMatch" in prefix_unit_dict.keys())
        # print(prefix_unit_dict.keys())
        if "dbpediaMatch" in prefix_unit_dict.keys():
            ontology_match_list.append(
                prefix_unit_dict["dbpediaMatch"]["value"]
            )
            # print(prefix_unit_dict["dbpediaMatch"]["value"])
        if "siExactMatch" in prefix_unit_dict:
            ontology_match_list.append(
                prefix_unit_dict["siExactMatch"]["value"]
            )
        conversion_multiplier = None
        if "conversionMultiplierSN" in prefix_unit_dict:

            conversion_multiplier = prefix_unit_dict["conversionMultiplierSN"][
                "value"
            ]
            # print(conversion_multiplier)

        _uuid = str(uuid.uuid5(namespace=uuid.NAMESPACE_URL, name=url))
        # print(_uuid)
        prefix_unit = model.PrefixUnit(
            uuid=_uuid,
            osw_id="Item:OSW"
            + str(parent_uuid).replace("-", "")
            + "#OSW"
            + _uuid.replace("-", ""),
            prefix="Item:OSW"
            + str(
                self.get_prefix_uuid(
                    prefixes_list,
                    self.get_unit_prefix(
                        unit_str=url, prefix_name_list=prefix_name_list
                    ),
                )
            ).replace("-", ""),
            # prefix_symbol="",  # Causes edge case error
            main_symbol=self.match_json_path_key(
                qudt_units_param_res,
                identifier=url,
                key="symbol",
            ),
            exact_ontology_match=ontology_match_list,
            conversion_factor_from_si=conversion_multiplier,
            description=[{"text": "Description", "lang": "en"}],
        )

        return prefix_unit

    def get_osw_quantity_unit_obj_list(self):
        """Function to extract the QuantityUnit objects from the QUDT API."""
        if self.debug:
            print("Transforming ontology data to OSW QuantityUnit objects...")
        i = 0
        units = []
        unit_dict = self.get_unit_dict(
            quantity_kinds=self.qudt_quantity_kinds,
            prefix_name_list=self.prefix_name_list,
        )
        # Iteration over the unit_dict to create the QuantityUnit objects
        for non_prefixed_unit_iri, unit_property_dict in unit_dict.items():
            name = non_prefixed_unit_iri.split("/")[-1]

            match_unit_dict = self.match_object_json_path(
                qudt_units_param_res=self.qudt_units,
                identifier=non_prefixed_unit_iri,
            )
            ontology_match_list = [match_unit_dict["applicableUnit"]["value"]]
            if "dbpediaMatch" in match_unit_dict.keys():
                ontology_match_list.append(
                    match_unit_dict["dbpediaMatch"]["value"]
                )
            if "siExactMatch" in match_unit_dict:
                ontology_match_list.append(
                    match_unit_dict["siExactMatch"]["value"]
                )
            conversion_multiplier = None
            if "conversionMultiplierSN" in match_unit_dict:
                conversion_multiplier = match_unit_dict[
                    "conversionMultiplierSN"
                ]["value"]
            # sequence of description before plainTextDescription is essential for overwriting
            description_list = None
            plainTextDescription = None
            if "description" in match_unit_dict:
                plainTextDescription = match_unit_dict["description"]["value"]
                description_list = [
                    model.Description(
                        text=plainTextDescription,
                        lang="en",
                    )
                ]
                # print(description_list)
            # overwrite description if plainTextDescription is present
            if "plainTextDescription" in match_unit_dict:
                plainTextDescription = match_unit_dict["plainTextDescription"][
                    "value"
                ]
                description_list = [
                    model.Description(
                        text=plainTextDescription,
                        lang="en",
                    )
                ]
                # print(description_list)
            if description_list == None:
                i += 1
                # print("No description found for ", name)

            qlabels = self.match_json_path_key(
                self.qudt_units,
                identifier=non_prefixed_unit_iri,
                key="qlabels",
            )

            label_dict = self.dict_from_comma_separated_list(qlabels)
            ### clean missing "en"
            if "" in label_dict.keys():
                label_dict["en"] = label_dict[""]
                del label_dict[""]

            osw_label_list = [
                model.Label(text=value, lang=key)
                for key, value in label_dict.items()
            ]
            symbol = self.match_json_path_key(
                self.qudt_units,
                identifier=non_prefixed_unit_iri,
                key="symbol",
            )
            _uuid = uuid.uuid5(
                namespace=uuid.NAMESPACE_URL, name=non_prefixed_unit_iri
            )
            # print(_uuid)
            prefix_unit_list = [
                self.get_osw_prefix_unit(
                    qudt_units_param_res=self.qudt_units,
                    prefixes_list=self.prefixes_json,
                    url=url,
                    parent_uuid=_uuid,
                    prefix_name_list=self.prefix_name_list,
                )
                for url in unit_property_dict["prefixed_units"]
            ]

            unit = model.QuantityUnit(
                uuid=_uuid,
                exact_ontology_match=ontology_match_list,
                name=name,
                label=osw_label_list,
                main_symbol=symbol,
                prefix_units=prefix_unit_list,
                description=description_list,
                conversion_factor_from_si=conversion_multiplier,
            )
            units.append(unit)

        if self.debug:
            print(
                f"Successfully transformed {len(units)} QuantityUnit objects."
            )
        return units


if __name__ == "__main__":
    # Fetch data
    debug = True
    prefixes = SiPrefixes()
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
    _prefixes_json = prefixes.get_prefixes_json()
    _prefix_name_list = prefixes.get_prefix_name_list()
    _qudt_units = sparql_qudt_units.execQuery()
    _qudt_quantity_kinds = sparql_qudt_quantities.execQuery()

    # Transform units
    osw_ontology = Ontology(
        prefixes_json=_prefixes_json,
        prefix_name_list=_prefix_name_list,
        qudt_quantity_kinds=_qudt_quantity_kinds,
        qudt_units=_qudt_units,
        debug=debug,
    )
    osw_quanity_unit_obj_list = osw_ontology.get_osw_quantity_unit_obj_list()

    # Transform
