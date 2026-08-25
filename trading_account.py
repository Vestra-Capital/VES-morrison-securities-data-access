"""HTTP client for the Morrison Securities Trading Accounts API.

Imports the shared base configuration from ``configuration`` and exposes a
``fetch_trading_accounts()`` helper that performs a GET request against the
``tradingaccounts/v2`` endpoint.  The module is intentionally side-effect-free
on import, so it can be safely reused by tests or other Python modules.
"""

import json
from typing import Any, Dict, NoReturn
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from configuration import BASE_URL, HEADERS, _raise_for_status

# Load environment variables from ``.env`` in the project root.
load_dotenv()

# API endpoint path for trading accounts.
ENDPOINT_PATH: str = "/tradingaccounts/v2"

# Full request URL composed from shared base host and endpoint path.
API_URL: str = BASE_URL + ENDPOINT_PATH


def fetch_trading_accounts() -> Dict[str, Any]:
    """Fetch trading accounts from the Morrison Securities API.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        RuntimeError: If the API key is missing, the response is empty,
            the response body is not valid JSON, or the server returns
            an HTTP error.
    """
    if not HEADERS["x-api-key"]:
        raise RuntimeError("MORRISON_ACCESS_KEY is missing. Check your .env file.")

    url = API_URL
    request = Request(url, headers=HEADERS, method="GET")

    try:
        with urlopen(request) as response:
            raw = response.read().decode("utf-8", errors="replace")

            if not raw.strip():
                raise RuntimeError("API returned an empty response.")

            try:
                return json.loads(raw)
            except json.JSONDecodeError as e:
                content_type = response.headers.get("Content-Type", "unknown")
                status = getattr(response, "status", "unknown")
                raise RuntimeError(
                    f"API returned non-JSON content (status={status}, "
                    f"Content-Type={content_type}). URL: {url} "
                    f"Response preview: {raw[:200]}"
                ) from e
    except HTTPError as e:
        _raise_for_status(e)

    raise RuntimeError("Unexpected state: request completed without returning data.")


if __name__ == "__main__":
    import json as _json

    data = fetch_trading_accounts()
    print(_json.dumps(data, indent=2, ensure_ascii=False))
