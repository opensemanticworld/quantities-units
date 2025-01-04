"""Implementation of Ontology class for handling ontology related operations."""

import os
import uuid
import json
import re
import osw.model.entity as model
from osw.utils.wiki import get_full_title
from osw.utils.strings import pascal_case
from jsonpath_ng.ext import parse


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
        self.all_non_prefixed_units, self.all_prefixed_units = (
            self.get_all_prefixed_non_prefixed_units()
        )

    # Utility Functions
    # -----------------
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

    def sort_label_list(
        self,
        label_list: list[model.Label] = None,
    ) -> list[model.Label]:
        "Function to sort label lists, english first, then other languages."
        # check if elements of label_list are of type model.Label
        if not label_list:
            return []
        if not all(isinstance(label, model.Label) for label in label_list):
            raise ValueError(
                "All elements of label_list must be of type model.Label"
            )
        else:
            return sorted(label_list, key=lambda x: x.lang != "en")

    def get_deterministic_url_uuid(self, prefix="", uri=None) -> uuid.UUID:
        """Function to generate a deterministic UUID from a URI and prefix."""
        return uuid.uuid5(namespace=uuid.NAMESPACE_URL, name=f"{prefix}{uri}")

    def get_osw_uuid_str(self, namespace="", _uuid=None) -> str:
        """Function to get the OSW category by URI."""
        return f"{namespace}OSW{str(_uuid).replace('-', '')}"

    def merge_unify_tuples_to_dict(self, tuple_list=None):
        """Function to merge and unify tuples to a dictionary."""
        if tuple_list is None:
            return {}

        result_dict = {}

        for key, values in tuple_list:
            if key not in result_dict:
                result_dict[key] = set(values) if values else None
            else:
                if result_dict[key] is not None:
                    result_dict[key].update(values if values else [])
                else:
                    result_dict[key] = set(values) if values else None

        # Convert sets back to lists
        for key in result_dict:
            if result_dict[key] is not None:
                result_dict[key] = list(result_dict[key])

        return result_dict

    def check_path_end_in_list(
        self, unit_uri=None, check_unit_list=None, get_bool=True
    ):
        """Function to check if the path end of a unit URI is in another list of units using regex."""
        matched_units = []
        path_end = unit_uri.split("/")[-1]
        for check_unit in check_unit_list:
            # print(f"check_unit: {check_unit}")
            if re.search(path_end, check_unit):
                # print(
                #     f"Path end: {path_end} found in {check_unit} on unit {unit_uri}"
                # )
                if get_bool:
                    return True
                else:
                    matched_units.append(check_unit)
                    # print(f"In check_path_end_in_list: {matched_units}")
        if get_bool:
            return False

        return matched_units

    def has_multiple_prefixes(self, unit_uri_list, prefix_list):
        """
        Check if any unit in the unit URI list has more than one prefix from the given prefix list.

        Parameters:
        unit_uri_list (list of str): List of unit URIs to check.
        prefix_list (list of str): List of prefixes to check against.

        Returns:
        tuple: A tuple containing two lists:
            - units_with_multiple_prefixes: List of units that have more than one prefix.
            - units_with_no_or_single_prefix: List of units that have no or a single prefix.
        """
        units_with_multiple_prefixes = []
        units_with_no_or_single_prefix = []
        prefix_counter = 0

        for unit_uri in unit_uri_list:
            # Detect if the unit has multiple prefixes using regex
            prefix_counter = len(
                re.findall("|".join(prefix_list), unit_uri, re.IGNORECASE)
            )
            if prefix_counter > 1:
                units_with_multiple_prefixes.append(unit_uri)
            else:
                units_with_no_or_single_prefix.append(unit_uri)

        return units_with_multiple_prefixes, units_with_no_or_single_prefix

    def categorize_units(self, unit_uri_list=None, prefix_list=None):
        """
        Categorize the given unit URI list based on the provided prefix list.

        Parameters:
        unit_uri_list (list of str): List of unit URIs to be categorized.
        prefix_list (list of str): List of prefixes to be used for categorization.

        Returns:
        tuple: A tuple containing two lists:
            - compound_prefix_unit_tuple_list: List of tuples with base unit and list of prefixed units.
            - not_determinable_unit_list: List of units that couldn't be categorized.
        """
        compound_prefix_unit_tuple_list = []
        not_determinable_unit_list = []

        # Check if any unit has multiple prefixes
        units_with_multiple_prefixes, units_with_no_or_single_prefix = (
            self.has_multiple_prefixes(unit_uri_list, prefix_list)
        )
        if units_with_no_or_single_prefix != []:
            # Check if any unit in units_with_no_or_single_prefix can be a base compound unit
            for possible_compound_unit in units_with_no_or_single_prefix:
                # Check if possible_compound_unit is part of units_with_multiple_prefixes
                if self.check_path_end_in_list(
                    unit_uri=possible_compound_unit,
                    check_unit_list=units_with_multiple_prefixes,
                ):
                    compound_prefix_unit_tuple_list.append(
                        (
                            possible_compound_unit,
                            self.check_path_end_in_list(
                                possible_compound_unit,
                                units_with_multiple_prefixes,
                                False,
                            ),
                        )
                    )
                else:
                    not_determinable_unit_list.append(
                        (possible_compound_unit, None)
                    )
        else:
            for not_compound_unit in units_with_multiple_prefixes:
                not_determinable_unit_list.append((not_compound_unit, None))

        return compound_prefix_unit_tuple_list, not_determinable_unit_list

    def lookup_existing_non_prefixed_units(
        self, all_non_prefixed_units=None, lookup_list=None
    ):
        """Function to lookup existing non prefixed units in a given list of units."""
        existing_unit_list = []
        for unit in lookup_list:
            if unit in all_non_prefixed_units:
                existing_unit_list.append(unit)
        return existing_unit_list

    def remove_prefix(self, uri=None, debug=False):
        """Function to remove any prefix from a given URI."""
        pattern = re.compile("|".join(self.prefix_name_list), re.IGNORECASE)
        if debug:
            print(pattern.sub("", uri))
        return pattern.sub("", uri)

    def remove_prefix_list(self, uri_list=None, debug=False):
        """Function to remove any prefix from a given list of URIs
        and return the cleaned list with no duplicates."""
        _list = [self.remove_prefix(uri, debug) for uri in uri_list]
        if debug:
            print(_list)
        return list(set(_list))

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

    def get_all_prefixed_non_prefixed_units(self):
        """Function to extract all prefixed and non-prefixed units from quantity kind."""
        all_prefixed_units = []
        all_non_prefixed_units = []
        quant_kind_list = self.qudt_quantity_kinds["results"]["bindings"]
        for quantity in quant_kind_list:
            non_prefixed, prefixed = self.split_prefixed_applicable_units(
                applicable_units_str=quantity["applicableUnits"]["value"],
                prefix_name_list=self.prefix_name_list,
            )
            all_prefixed_units = all_prefixed_units + prefixed
            all_non_prefixed_units = all_non_prefixed_units + non_prefixed

        all_prefixed_units = list(set(all_prefixed_units))
        all_non_prefixed_units = list(set(all_non_prefixed_units))
        return all_non_prefixed_units, all_prefixed_units

    def get_unit_dict(self):
        """Function to extract units as dictionary from quantity kind."""
        # Check that parameters are provided
        if self.qudt_quantity_kinds is None or self.prefix_name_list is None:
            exception_message = "Please provide all the parameters."
            raise Exception(exception_message)
        unit_dict = {}
        all_non_prefixed_units, all_prefixed_units = (
            self.get_all_prefixed_non_prefixed_units()
        )

        unit_dict = self.merge_prefixed_and_non_prefixed_units(
            all_non_prefixed_units, all_prefixed_units, self.prefix_name_list
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
            if prefix in str(unit_str).lower():
                return prefix
        return None

    # Prefixes
    # --------
    def get_osw_prefix_obj_list(self):
        """Get the list of prefixes from OSW."""
        if self.debug:
            print("Transforming ontology data to OSW UnitPrefix objects...")
        unit_prefixes = [
            model.UnitPrefix(
                uuid=uuid.uuid5(
                    namespace=uuid.NAMESPACE_URL,
                    name=prefix["pid"],
                ),
                name=prefix["label"],
                exact_ontology_match=[prefix["pid"]],
                label=[
                    {"text": f"{prefix["label"]} (unit prefix)", "lang": "en"}
                ],
                description=[],
                type=[
                    "Category:OSW99e0f46a40ca4129a420b4bb89c4cc45"
                ],  # Unit prefix
                symbol=prefix["symbol"],
                factor=prefix["scalingFactor"],
            )
            for prefix in self.prefixes_json
        ]
        if self.debug:
            print(
                f"...successfully transformed {len(unit_prefixes)} OSW UnitPrefix objects."
            )
        return unit_prefixes

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

    def get_composed_quantitiy_unit_dict(self):
        """Function to determine all the composed quantity units and their prefixed units."""

        # Inititializations
        aggregated_to_be_uploaded_unit_tuple_list = []
        composed_quantity_unit_dict = {}

        # Iterate over all the quantity kind bindings
        for quantity_binding in self.qudt_quantity_kinds["results"][
            "bindings"
        ]:

            # Get all the prefixed and non prefixed units of the quantity kind
            non_prefixed_units, prefixed_units = (
                self.split_prefixed_applicable_units(
                    applicable_units_str=quantity_binding["applicableUnits"][
                        "value"
                    ],
                    prefix_name_list=self.prefix_name_list,
                )
            )

            # Algorithm to identify uploaded units and construct pattern for to be uploaded units
            uploaded_units = []
            compound_prefix_unit_tuple_list = []
            not_determinable_unit_tuple_list = []
            # Step 1 - Remove prefixes from the applicable units
            removed_prefixes_applicable_units = self.remove_prefix_list(
                uri_list=prefixed_units
            )

            # Step 2 - Lookup existing non prefixed units
            uploaded_units = self.lookup_existing_non_prefixed_units(
                all_non_prefixed_units=self.all_non_prefixed_units,
                lookup_list=non_prefixed_units,
            )

            # Step 3 - Check if any uploaded, referenceable or to be uploaded units are found
            if uploaded_units != []:
                pass
            else:
                referenceable_uploaded_units = []
                referenceable_uploaded_units = (
                    self.lookup_existing_non_prefixed_units(
                        all_non_prefixed_units=self.all_non_prefixed_units,
                        lookup_list=removed_prefixes_applicable_units,
                    )
                )
                if referenceable_uploaded_units != []:
                    uploaded_units = referenceable_uploaded_units
                else:
                    # print(f"Quantity: {quantity_binding['quantity']['value']}")
                    # print(f"To be defined units: {to_be_defined_units}")
                    (
                        compound_prefix_unit_tuple_list,
                        not_determinable_unit_tuple_list,
                    ) = self.categorize_units(
                        unit_uri_list=prefixed_units,
                        prefix_list=self.prefix_name_list,
                    )
                    # Merge compound_prefix_unit_tuple_list with not_determinable_unit_tuple_list
                    aggregated_to_be_uploaded_unit_tuple_list += (
                        compound_prefix_unit_tuple_list
                        + not_determinable_unit_tuple_list
                    )
                    checksum = len(
                        compound_prefix_unit_tuple_list
                        + not_determinable_unit_tuple_list
                    )

        composed_quantity_unit_dict = self.merge_unify_tuples_to_dict(
            aggregated_to_be_uploaded_unit_tuple_list
        )

        return composed_quantity_unit_dict

    def get_osw_quantity_unit_obj_list(self, composed_units=False):
        """Function to extract the QuantityUnit objects from the QUDT API."""

        i = 0
        units = []
        if not composed_units:
            if self.debug:
                print(
                    "Transforming ontology data to OSW QuantityUnit objects..."
                )
            unit_dict = self.get_unit_dict()
        else:
            if self.debug:
                print(
                    "Transforming ontology data to OSW ComposedQuantityUnitWithUnitPrefix objects..."
                )
            unit_dict = self.get_composed_quantitiy_unit_dict()
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
            # clean missing "en"
            if "" in label_dict.keys():
                label_dict["en"] = label_dict[""]
                del label_dict[""]

            # Ensure that the label list is sorted with English first
            osw_label_list = [
                model.Label(text=value, lang=key)
                for key, value in label_dict.items()
            ]
            osw_label_list = self.sort_label_list(label_list=osw_label_list)

            symbol = self.match_json_path_key(
                self.qudt_units,
                identifier=non_prefixed_unit_iri,
                key="symbol",
            )
            _uuid = uuid.uuid5(
                namespace=uuid.NAMESPACE_URL, name=non_prefixed_unit_iri
            )
            if not composed_units:
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
            else:
                if unit_property_dict != None:
                    prefix_unit_list = [
                        self.get_osw_prefix_unit(
                            qudt_units_param_res=self.qudt_units,
                            prefixes_list=self.prefixes_json,
                            url=url,
                            parent_uuid=_uuid,
                            prefix_name_list=self.prefix_name_list,
                        )
                        for url in unit_property_dict
                    ]
                else:
                    prefix_unit_list = None
                unit = model.ComposedQuantityUnitWithUnitPrefix(
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
            if not composed_units:
                print(
                    f"...successfully transformed {len(units)} QuantityUnit objects."
                )
            else:
                print(
                    f"...successfully transformed {len(units)} ComposedQuantityUnitWithUnitPrefix objects."
                )
        return units

    # Quantity Kinds and Characteristics
    # ----------------------------------
    def get_osw_quantitykind_characteristics_obj_list(self):
        osw_quantitiy_list = []
        osw_fundamental_characteristic_list = []
        osw_characteristic_list = []
        is_broader_counter = 0
        has_broader_counter = 0

        if self.debug:
            print(
                "Transforming ontology data to OSW QuantityKind and Characteristic objects..."
            )
        for quantity_binding in self.qudt_quantity_kinds["results"][
            "bindings"
        ]:

            # Close Ontology Match
            quantity_close_ontology_match_list = []
            characteristic_close_ontology_match_list = []
            characteristic_close_ontology_match_list.append(
                quantity_binding["quantity"]["value"]
            )
            if "dbpediaMatch" in quantity_binding:
                quantity_close_ontology_match_list.append(
                    quantity_binding["dbpediaMatch"]["value"]
                )
                characteristic_close_ontology_match_list.append(
                    quantity_binding["dbpediaMatch"]["value"]
                )
            if "siExactMatch" in quantity_binding:
                quantity_close_ontology_match_list.append(
                    quantity_binding["siExactMatch"]["value"]
                )
                characteristic_close_ontology_match_list.append(
                    quantity_binding["siExactMatch"]["value"]
                )

            # Get all the prefixed and non prefixed units of the quantity kind
            non_prefixed_units, prefixed_units = (
                self.split_prefixed_applicable_units(
                    applicable_units_str=quantity_binding["applicableUnits"][
                        "value"
                    ],
                    prefix_name_list=self.prefix_name_list,
                )
            )

            # sequence of "description" before "plainTextDescription" is essential for overwriting
            description_list = None
            if "descriptions" in quantity_binding:
                description_split_list = quantity_binding["descriptions"][
                    "value"
                ].split(" #,# ")
                # if len(description_split_list) > 1:
                #     # This is just one case, set default to use the first description and english
                #     print(description_split_list)
                description_list = [
                    model.Description(
                        text=description_split_list[0].strip(),
                        lang="en",
                    )
                ]
            # Overwrite description if plainTextDescription is present
            if "plainTextDescriptions" in quantity_binding:
                plain_description_split_list = quantity_binding[
                    "plainTextDescriptions"
                ]["value"].split(" #,# ")
                # if len(plain_description_split_list) > 1:
                #     # This is just one case, set default to use the first description and englishSW
                #     print(plain_description_split_list)
                description_list = [
                    model.Description(
                        text=plain_description_split_list[0].strip(),
                        lang="en",
                    )
                ]

            qlabels = quantity_binding["labels"]["value"]
            label_dict = self.dict_from_comma_separated_list(qlabels)
            # print(label_dict)
            clean_label_dict = label_dict.copy()
            for lang, text in label_dict.items():
                # print(lang, text)
                # Remove item if "en-US" and "en" are present
                if lang == "en-US" and "en" in label_dict.keys():
                    del clean_label_dict["en-US"]
                # Rename "en-US" to "en" if "en" is not present
                if lang == "en-US" and "en" not in label_dict.keys():
                    clean_label_dict["en"] = text
                    del clean_label_dict["en-US"]
                # Set default language to "en" if key is empty and "en" is not present
                if lang == "" and "en" not in label_dict.keys():
                    clean_label_dict["en"] = clean_label_dict[""]
                    del clean_label_dict[""]
                # Remove empty item if "en" is present
                if lang == "" and "en" in label_dict.keys():
                    del clean_label_dict[""]

                # print(f"clean_label_dict: {clean_label_dict}")

            # Ensure that the label list is sorted with English first
            osw_label_list = [
                model.Label(text=value[:1].upper() + value[1:], lang=key)
                for key, value in clean_label_dict.items()
            ]
            osw_label_list = self.sort_label_list(label_list=osw_label_list)

            # Differentiate between is_broader and has_broader quantities/characteristics
            if "broader" not in quantity_binding:
                # This quantity is a broader quantity/characteristic
                is_broader_counter += 1
                # Algorithm to identify uploaded, referenceable or composed units
                osw_unit_uuids = []
                uploaded_units = []
                # Step 1 - Remove prefixes from the applicable units
                removed_prefixes_applicable_units = self.remove_prefix_list(
                    uri_list=prefixed_units
                )
                # Step 2 - Lookup existing non prefixed units
                uploaded_units = self.lookup_existing_non_prefixed_units(
                    all_non_prefixed_units=self.all_non_prefixed_units,
                    lookup_list=non_prefixed_units,
                )
                # Step 3 - Check if any uploaded, referenceable or to be uploaded units are found
                if uploaded_units != []:
                    # Set deterministic UUIDs for the non prefixed units
                    osw_unit_uuids = [
                        f"Item:OSW{str(uuid.uuid5(namespace=uuid.NAMESPACE_URL, name=unit)).replace('-', '')}"
                        for unit in non_prefixed_units
                    ]
                else:
                    # Set deterministic UUIDs for the referencable applicable non prefixed units
                    referenceable_uploaded_units = []
                    referenceable_uploaded_units = (
                        self.lookup_existing_non_prefixed_units(
                            all_non_prefixed_units=self.all_non_prefixed_units,
                            lookup_list=removed_prefixes_applicable_units,
                        )
                    )
                    if referenceable_uploaded_units != []:
                        osw_unit_uuids = [
                            f"Item:OSW{str(uuid.uuid5(namespace=uuid.NAMESPACE_URL, name=unit)).replace('-', '')}"
                            for unit in referenceable_uploaded_units
                        ]
                    else:
                        # Set deterministic UUIDs for the composed units
                        composed_quantity_unit_dict = (
                            self.get_composed_quantitiy_unit_dict()
                        )
                        # Step 4 - Get all removed prefixes of the applicable units
                        for unit in composed_quantity_unit_dict.keys():
                            if unit in prefixed_units:
                                osw_unit_uuids.append(
                                    f"Item:OSW{str(uuid.uuid5(namespace=uuid.NAMESPACE_URL, name=unit)).replace('-', '')}"
                                )
                                # print(f"Quantity: {quantity_binding['quantity']['value']}")
                                # print(f"Composed unit: {unit}\n")

                        # osw_unit_uuids = [
                        #     f"Item:OSW{str(uuid.uuid5(namespace=uuid.NAMESPACE_URL, name=unit)).replace('-', '')}"
                        #     for unit in composed_quantity_unit_dict.keys()
                        # ]
                        # print(f"composed_quantity_unit_dict: {composed_quantity_unit_dict}")

                osw_quantity = model.QuantityKind(
                    uuid=self.get_deterministic_url_uuid(
                        uri=quantity_binding["quantity"]["value"]
                    ),
                    label=osw_label_list,
                    description=description_list,
                    exact_ontology_match=[
                        quantity_binding["quantity"]["value"]
                    ],
                    close_ontology_match=quantity_close_ontology_match_list,
                    units=osw_unit_uuids,
                    name=pascal_case(osw_label_list[0].text),
                )

                osw_quantitiy_list.append(osw_quantity)

                characteristic = model.MetaFundamentalQuantityValue(
                    characteristics=None,  # only used for existing references
                    subclass_of=[
                        "Category:OSW4082937906634af992cf9a1b18d772cf"
                    ],  # QuantityValue
                    quantity=get_full_title(osw_quantity),
                    uuid=self.get_deterministic_url_uuid(
                        prefix="characteristic:",
                        uri=quantity_binding["quantity"]["value"],
                    ),
                    description=description_list,
                    name=pascal_case(osw_label_list[0].text),
                    label=osw_label_list,
                    close_ontology_match=characteristic_close_ontology_match_list,
                )

                osw_fundamental_characteristic_list.append(characteristic)

            else:
                # This characteristic has a broader characteristic/quantity
                has_broader_counter += 1
                broader_characteristic = self.get_osw_uuid_str(
                    namespace="Category:",
                    _uuid=self.get_deterministic_url_uuid(
                        prefix="characteristic:",
                        uri=quantity_binding["broader"]["value"],
                    ),
                )
                characteristic = model.MetaFundamentalQuantityValue(
                    characteristics=None,  # only used for existing references
                    subclass_of=[
                        broader_characteristic
                    ],  # Broader Characteristic
                    quantity=get_full_title(osw_quantity),
                    uuid=self.get_deterministic_url_uuid(
                        prefix="characteristic:",
                        uri=quantity_binding["quantity"]["value"],
                    ),
                    description=description_list,
                    name=pascal_case(osw_label_list[0].text),
                    label=osw_label_list,
                    close_ontology_match=characteristic_close_ontology_match_list,
                )

                osw_characteristic_list.append(characteristic)

        if self.debug:
            print(
                f"...transformed {len(osw_quantitiy_list)} OSW QuantityKind objects."
            )
            print(
                f"...transformed {len(osw_fundamental_characteristic_list + osw_characteristic_list)} OSW Characteristic/QuantityUnit objects."
            )
        assert len(osw_quantitiy_list) == is_broader_counter
        assert (
            len(osw_fundamental_characteristic_list + osw_characteristic_list)
            == has_broader_counter + is_broader_counter
        )
        return osw_quantitiy_list, osw_fundamental_characteristic_list, osw_characteristic_list


if __name__ == "__main__":
    from prefixes import SiPrefixes
    from sparql_wrapper import Sparql

    # Fetch data
    debug = True
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
    _prefixes_json = prefixes.get_prefixes_json()
    _prefix_name_list = prefixes.get_prefix_name_list()
    _qudt_units = sparql_qudt_units.execQuery()
    _qudt_quantity_kinds = sparql_qudt_quantities.execQuery()
    # Initialize Ontology for transformation
    osw_ontology = Ontology(
        prefixes_json=_prefixes_json,
        prefix_name_list=_prefix_name_list,
        qudt_quantity_kinds=_qudt_quantity_kinds,
        qudt_units=_qudt_units,
        debug=debug,
    )

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
