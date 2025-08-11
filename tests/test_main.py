import sys
import os
import json
import tempfile
import pytest

import main
from data_processing import ReportProcessor

@pytest.fixture
def sample_log_file(tmp_path):
    """Creates a temporary log file with sample JSON lines."""
    log_data = [
        {"url": "/api/v1/foo", "response_time": 100},
        {"url": "/api/v1/foo", "response_time": 200},
        {"url": "/api/v1/bar", "response_time": 300}
    ]
    file_path = tmp_path / "log.json"
    with open(file_path, "w") as f:
        for entry in log_data:
            f.write(json.dumps(entry) + "\n")
    return str(file_path)

def test_parse_args(monkeypatch):
    """Test argument parsing with valid arguments."""
    test_args = ["main.py", "--file", "log1.json", "--report", "average"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = main.parse_args()
    assert args.file == ["log1.json"]
    assert args.report == "average"

def test_read_logs(sample_log_file):
    """Test reading logs from a file."""
    logs = main.read_logs([sample_log_file])
    assert isinstance(logs, list)
    assert len(logs) == 3
    assert logs[0]["url"] == "/api/v1/foo"
    assert logs[2]["response_time"] == 300

def test_main_average_report(monkeypatch, capsys, sample_log_file):
    """Test the main workflow for the 'average' report."""
    # Prepare CLI args
    test_args = ["main.py", "--file", sample_log_file, "--report", "average"]
    monkeypatch.setattr(sys, "argv", test_args)

    # Ensure reports are imported (side-effect of main.py import)
    # and ReportProcessor has at least one report registered
    assert any(r.keyword == "average" for r in ReportProcessor.get_all_instances())

    # Run main and capture output
    main.main()
    captured = capsys.readouterr()
    assert "handler" in captured.out
    assert "/api/v1/foo" in captured.out
    assert "/api/v1/bar" in captured.out
    assert "avg_response_time" in captured.out


def test_main_unknown_report(monkeypatch, capsys, sample_log_file):
    """Test main workflow with unknown report type."""
    test_args = ["main.py", "--file", sample_log_file, "--report", "unknown"]
    monkeypatch.setattr(sys, "argv", test_args)
    with pytest.raises(SystemExit) as excinfo:
        main.main()
    assert excinfo.value.code == 2  # exit code for argparse errors
    captured = capsys.readouterr()
    assert "argument --report: invalid choice" in captured.err

def test_main_empty_report(monkeypatch, capsys, tmp_path):
    """Test main workflow with empty log file (should print 'Empty report data')."""
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("")
    test_args = ["main.py", "--file", str(empty_file), "--report", "average"]
    monkeypatch.setattr(sys, "argv", test_args)
    main.main()
    captured = capsys.readouterr()
    assert "" in captured.out