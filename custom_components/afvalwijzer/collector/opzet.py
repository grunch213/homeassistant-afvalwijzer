from datetime import datetime

import requests

from ..common.main_functions import _waste_type_rename
from ..const.const import _LOGGER, SENSOR_COLLECTORS_OPZET


def get_waste_data_raw(
    provider,
    postal_code,
    street_number,
    suffix,
):
    if provider not in SENSOR_COLLECTORS_OPZET.keys():
        raise ValueError(f"Invalid provider: {provider}, please verify")

    try:
        bag_id = None
        _verify = provider != "suez"
        url = f"{SENSOR_COLLECTORS_OPZET[provider]}/rest/adressen/{postal_code}-{street_number}"
        raw_response = requests.get(url, verify=_verify)
    except requests.exceptions.RequestException as err:
        raise ValueError(err) from err

    try:
        response = raw_response.json()
    except ValueError as e:
        raise ValueError(f"Invalid and/or no data received from {url}") from e

    if not response:
        _LOGGER.error("No waste data found!")
        return

    try:
        if len(response) > 1 and suffix:
            for item in response:
                if (
                    item["huisletter"] == suffix
                    or item["huisnummerToevoeging"] == suffix
                ):
                    bag_id = item["bagId"]
                    break
        else:
            bag_id = response[0]["bagId"]

        url = f"{SENSOR_COLLECTORS_OPZET[provider]}/rest/adressen/{bag_id}/afvalstromen"
        waste_data_raw_temp = requests.get(url, verify=_verify).json()
        waste_data_raw = []

        for item in waste_data_raw_temp:
            if not item["ophaaldatum"]:
                continue
            waste_type = item["menu_title"]
            if not waste_type:
                continue
            temp = {"type": _waste_type_rename(item["menu_title"].strip().lower())}
            temp["date"] = datetime.strptime(item["ophaaldatum"], "%Y-%m-%d").strftime(
                "%Y-%m-%d"
            )
            waste_data_raw.append(temp)
    except ValueError as exc:
        raise ValueError(f"Invalid and/or no data received from {url}") from exc

    return waste_data_raw


if __name__ == "__main__":
    print("Yell something at a mountain!")
