"""Regression tests for the separately packaged legacy CLI."""
import csv
from hypertensive_crisis_agent.cli import main, parse_boolean


def test_parse_boolean_false_is_false():
    assert parse_boolean("false") is False
    assert parse_boolean("0") is False
    assert parse_boolean("True") is True


def test_batch_false_does_not_escalate(tmp_path):
    source = tmp_path / "cases.csv"
    output = tmp_path / "results.csv"
    source.write_text(
        "case_id,primary_metric,secondary_metric,is_stat,status_flag\n"
        "CASE-1,10,5,false,NORMAL\n", encoding="utf-8"
    )
    assert main(["batch", "-i", str(source), "-o", str(output)]) == 0
    with output.open(newline="", encoding="utf-8") as f:
        row = next(csv.DictReader(f))
    assert row["overall_status"] == "CONCORDANT_NORMAL"
    assert row["stat_critical_alerts"] == "0"
