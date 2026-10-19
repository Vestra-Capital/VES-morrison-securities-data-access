"""Integration tests for all Morrison Securities Data Access API endpoints.

Uses Python's built-in ``unittest`` framework (no external test dependencies
required).  The tests exercise every endpoint client module in the project:

- configuration.py            -> /dataaccess/v1
- trading_account.py          -> /tradingaccounts/v2
- trading_account_detail.py   -> /tradingaccountdetail/v1
- equity_contract_notes.py    -> /equitycontractnotes/v1
- account_equity_holdings.py  -> /equityholdings/v1
- cash_balances.py            -> /cashbalances/v1
- chess_registration.py       -> /chessregistrationdetails/v1
- equity_holding_transactions.py -> /equityholdingtransactions/v1
- account_cash_ledgers.py     -> /accountcashledgers/v1

Run with::

    python -m unittest test.test_all_endpoints -v
"""

import os
import sys
import unittest

# Ensure the project root (parent of the ``test`` package) is on ``sys.path``
# so that the top-level modules can be imported when running via unittest.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from configuration import API_URL, BASE_URL, HEADERS, fetch_data
from trading_account import ENDPOINT_PATH as TA_PATH, fetch_trading_accounts
from trading_account_detail import ENDPOINT_PATH as TAD_PATH, fetch_trading_account_detail
from equity_contract_notes import ENDPOINT_PATH as ECN_PATH, fetch_equity_contract_notes
from account_equity_holdings import ENDPOINT_PATH as AEH_PATH, fetch_account_equity_holdings
from cash_balances import ENDPOINT_PATH as CB_PATH, fetch_cash_balances
from chess_registration import ENDPOINT_PATH as CR_PATH, fetch_chess_registration_details
from equity_holding_transactions import ENDPOINT_PATH as EHT_PATH, fetch_equity_holding_transactions
from account_cash_ledgers import ENDPOINT_PATH as ACL_PATH, fetch_account_cash_ledgers


def _extract_scope_items(config):
    """Extract a list of scope item dicts from the configuration API response."""
    items = []
    if isinstance(config, list):
        items = [item for item in config if isinstance(item, dict)]
    elif isinstance(config, dict):
        for value in config.values():
            if isinstance(value, list):
                items = [item for item in value if isinstance(item, dict)]
                if items:
                    break
        if not items:
            items = [config]
    return items


class TestConfigurationEndpoint(unittest.TestCase):
    """Tests for configuration.py -> /dataaccess/v1."""

    def test_fetch_data_returns_dict(self):
        """fetch_data() should return a JSON-decoded dictionary (or list of dicts)."""
        data = fetch_data()
        self.assertIsNotNone(data, "fetch_data() returned None")
        self.assertIsInstance(data, (dict, list), f"Expected dict or list, got {type(data)}")
        print(f"\n[dataaccess/v1] Response keys: {list(data.keys()) if isinstance(data, dict) else f'{len(data)} items'}")

    def test_api_key_present(self):
        """HEADERS must contain a non-empty x-api-key."""
        self.assertTrue(HEADERS["x-api-key"], "MORRISON_ACCESS_KEY is missing or empty")


class TestTradingAccountsEndpoint(unittest.TestCase):
    """Tests for trading_account.py -> /tradingaccounts/v2."""

    def test_endpoint_path(self):
        self.assertEqual(TA_PATH, "/tradingaccounts/v2")

    def test_fetch_with_scope_items(self):
        data = fetch_data()
        scope_items = _extract_scope_items(data)
        self.assertTrue(scope_items, "No scope items extracted from configuration")

        seen = set()
        for item in scope_items:
            adviser_code = item.get("adviserCode")
            if adviser_code in seen:
                continue
            if adviser_code:
                seen.add(adviser_code)

            for include_inactive in (True, False):
                call_item = dict(item)
                call_item["includeInactive"] = include_inactive
                result = fetch_trading_accounts(call_item)
                self.assertIsNotNone(result, f"No data for adviserCode={adviser_code} includeInactive={include_inactive}")
                self.assertIsInstance(result, (dict, list))
                print(f"\n[tradingaccounts/v2] adviserCode={adviser_code} includeInactive={include_inactive} -> {type(result).__name__}")


class TestTradingAccountDetailEndpoint(unittest.TestCase):
    """Tests for trading_account_detail.py -> /tradingaccountdetail/v1."""

    def test_endpoint_path(self):
        self.assertEqual(TAD_PATH, "/tradingaccountdetail/v1")

    def test_fetch_account_detail(self):
        result = fetch_trading_account_detail()
        self.assertIsNotNone(result, "fetch_trading_account_detail() returned None")
        self.assertIsInstance(result, (dict, list))
        print(f"\n[tradingaccountdetail/v1] Response type: {type(result).__name__}")


class TestEquityContractNotesEndpoint(unittest.TestCase):
    """Tests for equity_contract_notes.py -> /equitycontractnotes/v1."""

    def test_endpoint_path(self):
        self.assertEqual(ECN_PATH, "/equitycontractnotes/v1")

    def test_fetch_with_scope_items(self):
        data = fetch_data()
        scope_items = _extract_scope_items(data)
        self.assertTrue(scope_items, "No scope items extracted from configuration")

        seen = set()
        for item in scope_items:
            adviser_code = item.get("adviserCode")
            if adviser_code in seen:
                continue
            if adviser_code:
                seen.add(adviser_code)

            result = fetch_equity_contract_notes(item)
            self.assertIsNotNone(result, f"No data for adviserCode={adviser_code}")
            self.assertIsInstance(result, (dict, list))
            print(f"\n[equitycontractnotes/v1] adviserCode={adviser_code} -> {type(result).__name__}")


class TestAccountEquityHoldingsEndpoint(unittest.TestCase):
    """Tests for account_equity_holdings.py -> /equityholdings/v1."""

    def test_endpoint_path(self):
        self.assertEqual(AEH_PATH, "/equityholdings/v1")

    def test_fetch_with_scope_items(self):
        data = fetch_data()
        scope_items = _extract_scope_items(data)
        self.assertTrue(scope_items, "No scope items extracted from configuration")

        seen = set()
        for item in scope_items:
            adviser_code = item.get("adviserCode")
            if adviser_code in seen:
                continue
            if adviser_code:
                seen.add(adviser_code)

            for include_zero in (True, False):
                call_item = dict(item)
                call_item["includeZeroHoldings"] = include_zero
                result = fetch_account_equity_holdings(call_item)
                self.assertIsNotNone(result, f"No data for adviserCode={adviser_code} includeZeroHoldings={include_zero}")
                self.assertIsInstance(result, (dict, list))
                print(f"\n[equityholdings/v1] adviserCode={adviser_code} includeZeroHoldings={include_zero} -> {type(result).__name__}")


class TestCashBalancesEndpoint(unittest.TestCase):
    """Tests for cash_balances.py -> /cashbalances/v1."""

    def test_endpoint_path(self):
        self.assertEqual(CB_PATH, "/cashbalances/v1")

    def test_fetch_with_scope_items(self):
        data = fetch_data()
        scope_items = _extract_scope_items(data)
        self.assertTrue(scope_items, "No scope items extracted from configuration")

        seen = set()
        for item in scope_items:
            adviser_code = item.get("adviserCode")
            if adviser_code in seen:
                continue
            if adviser_code:
                seen.add(adviser_code)

            result = fetch_cash_balances(item)
            self.assertIsNotNone(result, f"No data for adviserCode={adviser_code}")
            self.assertIsInstance(result, (dict, list))
            print(f"\n[cashbalances/v1] adviserCode={adviser_code} -> {type(result).__name__}")


class TestChessRegistrationEndpoint(unittest.TestCase):
    """Tests for chess_registration.py -> /chessregistrationdetails/v1."""

    def test_endpoint_path(self):
        self.assertEqual(CR_PATH, "/chessregistrationdetails/v1")

    def test_fetch_with_scope_items(self):
        data = fetch_data()
        scope_items = _extract_scope_items(data)
        self.assertTrue(scope_items, "No scope items extracted from configuration")

        seen = set()
        for item in scope_items:
            adviser_code = item.get("adviserCode")
            if adviser_code in seen:
                continue
            if adviser_code:
                seen.add(adviser_code)

            result = fetch_chess_registration_details(item)
            self.assertIsNotNone(result, f"No data for adviserCode={adviser_code}")
            self.assertIsInstance(result, (dict, list))
            print(f"\n[chessregistrationdetails/v1] adviserCode={adviser_code} -> {type(result).__name__}")


class TestEquityHoldingTransactionsEndpoint(unittest.TestCase):
    """Tests for equity_holding_transactions.py -> /equityholdingtransactions/v1."""

    def test_endpoint_path(self):
        self.assertEqual(EHT_PATH, "/equityholdingtransactions/v1")

    def test_fetch_with_scope_items(self):
        data = fetch_data()
        scope_items = _extract_scope_items(data)
        self.assertTrue(scope_items, "No scope items extracted from configuration")

        seen = set()
        for item in scope_items:
            adviser_code = item.get("adviserCode")
            if adviser_code in seen:
                continue
            if adviser_code:
                seen.add(adviser_code)

            call_item = dict(item)
            call_item["startDate"] = "2024-01-01"
            call_item["endDate"] = "2024-12-31"

            result = fetch_equity_holding_transactions(call_item)
            self.assertIsNotNone(result, f"No data for adviserCode={adviser_code}")
            self.assertIsInstance(result, (dict, list))
            print(f"\n[equityholdingtransactions/v1] adviserCode={adviser_code} -> {type(result).__name__}")


class TestAccountCashLedgersEndpoint(unittest.TestCase):
    """Tests for account_cash_ledgers.py -> /accountcashledgers/v1."""

    def test_endpoint_path(self):
        self.assertEqual(ACL_PATH, "/accountcashledgers/v1")

    def test_fetch_with_scope_items(self):
        data = fetch_data()
        scope_items = _extract_scope_items(data)
        self.assertTrue(scope_items, "No scope items extracted from configuration")

        seen = set()
        for item in scope_items:
            adviser_code = item.get("adviserCode")
            if adviser_code in seen:
                continue
            if adviser_code:
                seen.add(adviser_code)

            result = fetch_account_cash_ledgers(item)
            self.assertIsNotNone(result, f"No data for adviserCode={adviser_code}")
            self.assertIsInstance(result, (dict, list))
            print(f"\n[accountcashledgers/v1] adviserCode={adviser_code} -> {type(result).__name__}")


class TestEndpointUrlComposition(unittest.TestCase):
    """Verify that each module builds its API URL from the shared BASE_URL."""

    def test_base_url_is_valid(self):
        self.assertTrue(BASE_URL.startswith("http"), f"BASE_URL does not look like a URL: {BASE_URL}")

    def test_dataaccess_url(self):
        expected = BASE_URL + "/dataaccess/v1"
        self.assertEqual(API_URL, expected)

    def test_trading_account_url(self):
        expected = BASE_URL + TA_PATH
        from trading_account import API_URL as TA_API_URL
        self.assertEqual(TA_API_URL, expected)

    def test_trading_account_detail_url(self):
        from trading_account_detail import API_URL as TAD_API_URL
        expected = BASE_URL + TAD_PATH
        self.assertEqual(TAD_API_URL, expected)

    def test_equity_contract_notes_url(self):
        from equity_contract_notes import API_URL as ECN_API_URL
        expected = BASE_URL + ECN_PATH
        self.assertEqual(ECN_API_URL, expected)

    def test_account_equity_holdings_url(self):
        from account_equity_holdings import API_URL as AEH_API_URL
        expected = BASE_URL + AEH_PATH
        self.assertEqual(AEH_API_URL, expected)

    def test_cash_balances_url(self):
        from cash_balances import API_URL as CB_API_URL
        expected = BASE_URL + CB_PATH
        self.assertEqual(CB_API_URL, expected)

    def test_chess_registration_url(self):
        from chess_registration import API_URL as CR_API_URL
        expected = BASE_URL + CR_PATH
        self.assertEqual(CR_API_URL, expected)

    def test_equity_holding_transactions_url(self):
        from equity_holding_transactions import API_URL as EHT_API_URL
        expected = BASE_URL + EHT_PATH
        self.assertEqual(EHT_API_URL, expected)

    def test_account_cash_ledgers_url(self):
        from account_cash_ledgers import API_URL as ACL_API_URL
        expected = BASE_URL + ACL_PATH
        self.assertEqual(ACL_API_URL, expected)


class EndpointTestResult(unittest.TextTestResult):
    """Custom test result that tracks pass/fail/error per test method."""

    _GREEN = "\033[92m"
    _RED = "\033[91m"
    _YELLOW = "\033[93m"
    _RESET = "\033[0m"

    _ENDPOINT_MAP = {
        "TestConfigurationEndpoint": "/dataaccess/v1",
        "TestTradingAccountsEndpoint": "/tradingaccounts/v2",
        "TestTradingAccountDetailEndpoint": "/tradingaccountdetail/v1",
        "TestEquityContractNotesEndpoint": "/equitycontractnotes/v1",
        "TestAccountEquityHoldingsEndpoint": "/equityholdings/v1",
        "TestCashBalancesEndpoint": "/cashbalances/v1",
        "TestChessRegistrationEndpoint": "/chessregistrationdetails/v1",
        "TestEquityHoldingTransactionsEndpoint": "/equityholdingtransactions/v1",
        "TestAccountCashLedgersEndpoint": "/accountcashledgers/v1",
        "TestEndpointUrlComposition": "(URL composition)",
    }

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self._endpoint_results = []
        self._use_color = sys.stdout.isatty()

    def _colorize(self, status):
        if not self._use_color:
            return status
        colors = {
            "OK": self._GREEN + status + self._RESET,
            "ERROR": self._RED + status + self._RESET,
            "FAIL": self._YELLOW + status + self._RESET,
        }
        return colors.get(status, status)

    def addSuccess(self, test):
        super().addSuccess(test)
        self._endpoint_results.append((test._testMethodName, test.__class__.__name__, "OK", ""))

    def addError(self, test, err):
        super().addError(test, err)
        self._endpoint_results.append(
            (test._testMethodName, test.__class__.__name__, "ERROR",
             self._exc_info_to_string(err, test)[:200])
        )

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._endpoint_results.append(
            (test._testMethodName, test.__class__.__name__, "FAIL",
             self._exc_info_to_string(err, test)[:200])
        )

    def _endpoint_for_class(self, cls_name):
        return self._ENDPOINT_MAP.get(cls_name, "unknown")

    def print_summary(self):
        print("\n" + "=" * 72)
        print("ENDPOINT TEST SUMMARY")
        print("=" * 72)

        endpoint_overall = {}
        for _, cls, status, _ in self._endpoint_results:
            ep = self._endpoint_for_class(cls)
            if ep not in endpoint_overall:
                endpoint_overall[ep] = {"OK": 0, "FAIL": 0, "ERROR": 0}
            endpoint_overall[ep][status] += 1

        for ep, counts in endpoint_overall.items():
            total = counts["OK"] + counts["FAIL"] + counts["ERROR"]
            if counts["ERROR"] > 0:
                ep_status = self._colorize("ERROR")
            elif counts["FAIL"] > 0:
                ep_status = self._colorize("FAIL")
            else:
                ep_status = self._colorize("OK")
            print(f"  {ep:<38s} {ep_status:<16s}  ({counts['OK']} ok / {counts['FAIL']} fail / {counts['ERROR']} err of {total})")

        print("-" * 72)
        print("  Per-test results:")
        for method, cls, status, detail in self._endpoint_results:
            display = f"    {cls}.{method}"
            colored = self._colorize(status)
            print(f"  {display:<55s} ... {colored}")
            if detail:
                print(f"    -> {detail}")

        print("=" * 72)
        total = len(self._endpoint_results)
        passed = sum(1 for _, _, s, _ in self._endpoint_results if s == "OK")
        failed = sum(1 for _, _, s, _ in self._endpoint_results if s == "FAIL")
        errored = sum(1 for _, _, s, _ in self._endpoint_results if s == "ERROR")
        print(f"  Total: {total}  Passed: {passed}  Failed: {failed}  Errors: {errored}")
        overall = "FAIL" if (errored > 0 or failed > 0) else "PASS"
        print(f"  Overall result: {self._colorize(overall)}")
        print("=" * 72 + "\n")


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2, resultclass=EndpointTestResult)
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    result = runner.run(suite)
    if isinstance(result, EndpointTestResult):
        result.print_summary()
    sys.exit(0 if result.wasSuccessful() else 1)
