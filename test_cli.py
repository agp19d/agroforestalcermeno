#!/usr/bin/env python3
"""Tests for the CLI tool's --dangerously-skip-permissions flag."""

import unittest
from unittest.mock import patch
from io import StringIO

from cli import main, check_permissions, create_parser


class TestDangerouslySkipPermissions(unittest.TestCase):
    """Tests for the --dangerously-skip-permissions flag."""

    def test_flag_defaults_to_false(self):
        parser = create_parser()
        args = parser.parse_args(["run", "plant"])
        self.assertFalse(args.dangerously_skip_permissions)

    def test_flag_can_be_set(self):
        parser = create_parser()
        args = parser.parse_args(["--dangerously-skip-permissions", "run", "plant"])
        self.assertTrue(args.dangerously_skip_permissions)

    def test_restricted_operation_denied_without_flag(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            result = main(["run", "delete"])
        self.assertEqual(result, 1)
        self.assertIn("Permission denied", mock_err.getvalue())

    def test_restricted_operation_allowed_with_flag(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                result = main(["--dangerously-skip-permissions", "run", "delete"])
        self.assertEqual(result, 0)
        self.assertIn("Skipping permission checks", mock_err.getvalue())
        self.assertIn("Executing operation: delete", mock_out.getvalue())

    def test_unrestricted_operation_works_without_flag(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            result = main(["run", "plant"])
        self.assertEqual(result, 0)
        self.assertIn("Executing operation: plant", mock_out.getvalue())

    def test_config_show_reflects_permissions_enabled(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            result = main(["config", "--show"])
        self.assertEqual(result, 0)
        self.assertIn("permissions_enabled: True", mock_out.getvalue())

    def test_config_show_reflects_permissions_disabled(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            result = main(["--dangerously-skip-permissions", "config", "--show"])
        self.assertEqual(result, 0)
        self.assertIn("permissions_enabled: False", mock_out.getvalue())


class TestCheckPermissions(unittest.TestCase):
    """Tests for the permission checking logic."""

    def test_restricted_operations_are_denied(self):
        for op in ("delete", "reset", "migrate"):
            self.assertFalse(check_permissions(op))

    def test_normal_operations_are_allowed(self):
        for op in ("plant", "harvest", "inspect"):
            self.assertTrue(check_permissions(op))


if __name__ == "__main__":
    unittest.main()
