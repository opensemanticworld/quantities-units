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

    def get_prefixes_json(self):
        """Fetch prefixes from si-digital-framework."""
        try:
            sidf_prefixes_res_en = requests.get(
                url=self.sidf_prefixes_url,
                params={"lang": "en"},
            )
            return sidf_prefixes_res_en.json()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_prefix_name_list(self):
        """Get the list of prefix labels."""
        return [prefix["label"] for prefix in self.get_prefixes_json()]


if __name__ == "__main__":
    prefixes = SiPrefixes()
    print(prefixes.get_prefixes_json())
    print(prefixes.get_prefix_name_list())
