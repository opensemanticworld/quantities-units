import requests
import uuid
import osw.model.entity as model


class SiPrefixes:
    """Class for fetching prefixes from si-digital-framework."""

    def __init__(self):
        self.sidf_api_host = "https://si-digital-framework.org"
        self.sidf_prefixes_endpoint = "/SI/prefixes"
        self.sidf_prefixes_url = (
            self.sidf_api_host + self.sidf_prefixes_endpoint
        )

    def get_sidf_prefixes_json(self):
        """Fetch prefixes from si-digital-framework."""
        try:
            sidf_prefixes_res_en = requests.get(
                url=self.sidf_prefixes_url,
                params={"lang": "en"},
            )
            return sidf_prefixes_res_en.json()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_osw_prefix_obj_list(self):
        """Get the list of prefixes from OSW."""
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
            for prefix in self.get_sidf_prefixes_json()
        ]
        return unit_prefixes

    def get_prefix_list(self):
        """Get the list of prefix labels."""
        return [prefix["label"] for prefix in self.get_sidf_prefixes_json()]


if __name__ == "__main__":
    prefixes = SiPrefixes()
    print(prefixes.get_sidf_prefixes_json())
    print(prefixes.get_osw_prefix_obj_list())
    print(prefixes.get_prefix_list())
