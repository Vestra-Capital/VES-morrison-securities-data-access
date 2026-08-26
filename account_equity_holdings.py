"""HTTP client for the Morrison Securities Account Equity Holdings API.

Imports the shared base configuration from ``configuration`` and exposes a
``fetch_account_equity_holdings()`` helper that performs a GET request against the
``equityholdings/v1`` endpoint.  The module is intentionally side-effect-free
on import, so it can be safely reused by tests or other Python modules.
"""

import json
from typing import Any, Dict, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from configuration import (
    BASE_URL,
    HEADERS,
    _raise_for_status,
    fetch_data,
)

# Load environment variables from ``.env`` in the project root.
load_dotenv()

# API endpoint path for account equity holdings.
ENDPOINT_PATH: str = "/equityholdings/v1"

# Full request URL composed from shared base host and endpoint path.
API_URL: str = BASE_URL + ENDPOINT_PATH

# Account Number for testing
#ACCOUNT_NUMBER: Optional[str] = "115047"
ACCOUNT_NUMBER: Optional[str] = None

def _build_url(scope_item: Dict[str, Any]) -> str:
    """Build the account equity holdings API URL from a scoping item."""
    url = API_URL
    params: Dict[str, Any] = {}
    if scope_item.get("organisationCode"):
        params["organisationCode"] = scope_item["organisationCode"]
    if scope_item.get("branchCode"):
        params["branchCode"] = scope_item["branchCode"]
    if scope_item.get("adviserCode"):
        params["adviserCode"] = scope_item["adviserCode"]
    account_number = scope_item.get("accountNumber", ACCOUNT_NUMBER)
    if account_number:
        params["accountNumber"] = account_number
    if "includeZeroHoldings" in scope_item:
        params["includeZeroHoldings"] = "true"

    if params:
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{API_URL}?{query_string}"

    return url


def fetch_account_equity_holdings(scope_item: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch account equity holdings from the Morrison Securities API.

    Args:
        scope_item: Dictionary containing scoping parameters such as
            ``organisationCode``, ``branchCode``, ``adviserCode``,
            ``accountNumber``, and ``includeZeroHoldings``.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        RuntimeError: If the API key is missing, the response is empty,
            the response body is not valid JSON, or the server returns
            an HTTP error.
    """
    if not HEADERS["x-api-key"]:
        raise RuntimeError("MORRISON_ACCESS_KEY is missing. Check your .env file.")

    url = _build_url(scope_item)
    print(f"Requesting: {url}")

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


def _extract_scope_items(config: Any) -> list:
    """Extract a list of scope item dicts from the configuration API response."""
    items: list = []
    if isinstance(config, list):
        items = [item for item in config if isinstance(item, dict)]
    elif isinstance(config, dict):
        for value in config.values():
            if isinstance(value, list):
                items = [item for item in value if isinstance(item, dict)]
                if items:
                    break
        if not items and isinstance(config, dict):
            items = [config]
    return items


if __name__ == "__main__":
    import json as _json

    config = fetch_data()
    scope_items = _extract_scope_items(config)

    seen_adviser_codes = set()
    for item in scope_items:
        adviser_code = item.get("adviserCode")
        if adviser_code in seen_adviser_codes:
            continue
        if adviser_code:
            seen_adviser_codes.add(adviser_code)

        for include_zero_holdings in (True, False):
            call_item = dict(item)
            call_item["includeZeroHoldings"] = include_zero_holdings

            data = fetch_account_equity_holdings(call_item)
            print(f"\n--- Result for adviserCode={adviser_code or 'N/A'} includeZeroHoldings={include_zero_holdings} ---")
            print(_json.dumps(data, indent=2, ensure_ascii=False))
