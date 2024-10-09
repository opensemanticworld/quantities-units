from utils import sparql_wrapper
from pprint import pprint
import json
import requests

quant_kind_list = json.load(open("ontology/qudt/data/quantitykind.json", "r"))["results"]["bindings"]

pprint(quant_kind_list[5]["applicableUnits"])

def get_prefix_list():


    sidf_prefixes_res_de = requests.get(
        url="https://si-digital-framework.org/SI/prefixes",
        params={"lang": "de"},
    )

    # Convert result to dict
    sidf_prefixes_de = sidf_prefixes_res_de.json()
    print(sidf_prefixes_de)
    prefix_name_list = [item["label"] for item in sidf_prefixes_de]
    print(prefix_name_list)
    return(prefix_name_list)

prefix_name_list = get_prefix_list()

def get_unit_prefix(unit_str):
    for prefix in prefix_name_list:
        if prefix in unit_str.lower():
            return prefix
    return None
def get_non_prefixed_units_from_applicable_units(applicable_units_str):
    non_prefixed_units = []
    prefixed_units = []
    for unit_str in applicable_units_str.split(", "):

        print(unit_str)
        print(get_unit_prefix(unit_str))
        if get_unit_prefix(unit_str) == None:
            print("no prefix: ", unit_str)
            non_prefixed_units.append(unit_str)
        else:
            print("prefix: ", get_unit_prefix(unit_str), "found in ", unit_str)
            prefixed_units.append(unit_str)
    return non_prefixed_units, prefixed_units


all_prefixed_units = []
all_non_prefixed_units = []
for quant_kind in quant_kind_list:
    non_prefixed, prefixed = get_non_prefixed_units_from_applicable_units(quant_kind["applicableUnits"]["value"])
    all_prefixed_units = all_prefixed_units + prefixed
    all_non_prefixed_units = all_non_prefixed_units + non_prefixed

all_prefixed_units = list(set(all_prefixed_units))
all_non_prefixed_units = list(set(all_non_prefixed_units))

print(len(all_prefixed_units))
print(len(all_non_prefixed_units))