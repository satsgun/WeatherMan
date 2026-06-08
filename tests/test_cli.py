"""Tests for weatherman.cli — argument parsing and entry point."""

import pytest
from weatherman.cli import parse_args, main


# ---------------------------------------------------------------------------
# parse_args — valid inputs
# ---------------------------------------------------------------------------

class TestParseArgsValidInputs:

    def test_city_only_sets_all_defaults(self):
        ns = parse_args(["--city", "London"])
        assert ns.city == "London"
        assert ns.days == 1
        assert ns.units == "metric"
        assert ns.output == "json"

    def test_city_with_spaces_preserved(self):
        ns = parse_args(["--city", "New York"])
        assert ns.city == "New York"

    def test_days_override(self):
        ns = parse_args(["--city", "Paris", "--days", "7"])
        assert ns.days == 7

    def test_units_imperial(self):
        ns = parse_args(["--city", "Chicago", "--units", "imperial"])
        assert ns.units == "imperial"

    def test_units_metric_explicit(self):
        ns = parse_args(["--city", "Berlin", "--units", "metric"])
        assert ns.units == "metric"

    def test_output_text(self):
        ns = parse_args(["--city", "Tokyo", "--output", "text"])
        assert ns.output == "text"

    def test_output_json_explicit(self):
        ns = parse_args(["--city", "Oslo", "--output", "json"])
        assert ns.output == "json"

    def test_all_args_together(self):
        ns = parse_args([
            "--city", "Sydney",
            "--days", "3",
            "--units", "imperial",
            "--output", "text",
        ])
        assert ns.city == "Sydney"
        assert ns.days == 3
        assert ns.units == "imperial"
        assert ns.output == "text"


# ---------------------------------------------------------------------------
# parse_args — invalid inputs (argparse exits with code 2)
# ---------------------------------------------------------------------------

class TestParseArgsInvalidInputs:

    def test_missing_city_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args([])
        assert exc_info.value.code == 2

    def test_missing_city_error_mentions_city(self, capsys):
        with pytest.raises(SystemExit):
            parse_args([])
        captured = capsys.readouterr()
        assert "city" in captured.err

    def test_days_non_integer_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--city", "London", "--days", "abc"])
        assert exc_info.value.code == 2

    def test_days_float_string_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--city", "London", "--days", "2.5"])
        assert exc_info.value.code == 2

    def test_invalid_units_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--city", "London", "--units", "kelvin"])
        assert exc_info.value.code == 2

    def test_invalid_output_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--city", "London", "--output", "csv"])
        assert exc_info.value.code == 2

    def test_invalid_units_error_mentions_choices(self, capsys):
        with pytest.raises(SystemExit):
            parse_args(["--city", "London", "--units", "kelvin"])
        captured = capsys.readouterr()
        assert "metric" in captured.err or "imperial" in captured.err


# ---------------------------------------------------------------------------
# main — placeholder output
# ---------------------------------------------------------------------------

class TestMain:

    def test_main_prints_placeholder(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["weatherman", "--city", "London"])
        main()
        captured = capsys.readouterr()
        assert "London" in captured.out

    def test_main_includes_days_in_output(self, capsys, monkeypatch):
        monkeypatch.setattr(
            "sys.argv",
            ["weatherman", "--city", "Berlin", "--days", "5"],
        )
        main()
        captured = capsys.readouterr()
        assert "5" in captured.out

    def test_main_includes_units_in_output(self, capsys, monkeypatch):
        monkeypatch.setattr(
            "sys.argv",
            ["weatherman", "--city", "Rome", "--units", "imperial"],
        )
        main()
        captured = capsys.readouterr()
        assert "imperial" in captured.out

    def test_main_exits_nonzero_on_missing_city(self, monkeypatch):
        monkeypatch.setattr("sys.argv", ["weatherman"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code != 0
