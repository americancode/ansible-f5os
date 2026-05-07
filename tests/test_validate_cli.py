"""Unit tests for the validate entrypoint."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from tools.f5os_tools.cli import main


class ValidateCliTests(unittest.TestCase):
    """Validate CLI dispatch for repo helper tools."""

    def test_validate_vars_command_dispatches_runtime(self) -> None:
        with patch("tools.f5os_tools.cli.run_validate", return_value=7) as mocked:
            result = main(["validate-vars"])

        self.assertEqual(result, 7)
        mocked.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
