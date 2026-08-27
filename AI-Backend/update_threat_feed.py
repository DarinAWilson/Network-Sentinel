import os
import requests


DROP_URL = "https://www.spamhaus.org/drop/drop.txt"

OUTPUT_PATH = os.getenv(
    "THREAT_LIST_PATH",
    "/app/data/spamhaus_drop.txt"
)


def update_feed():
    response = requests.get(
        DROP_URL,
        timeout=30
    )

    response.raise_for_status()

    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(response.text)

    print(
        f"Threat feed updated: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    update_feed()