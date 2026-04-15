"""Tests for the patchwork_env CLI."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from patchwork_env.cli import build_parser, main


@pytest.fixture
def base_env_file(tmp_path: Path) -> Path:
    f = tmp_path / "base.env"
    f.write_text("APP_NAME=myapp\nDEBUG=false\nDB_HOST=localhost\n")
    return f


@pytest.fixture
def target_env_file(tmp_path: Path) -> Path:
    f = tmp_path / "target.env"
    f.write_text("APP_NAME=myapp\nDEBUG=true\nDB_PORT=5432\n")
    return f


class TestBuildParser:
    def test_diff_subcommand_registered(self):
        parser = build_parser()
        args = parser.parse_args(["diff", "base.env", "target.env"])
        assert args.command == "diff"

    def test_merge_subcommand_registered(self):
        parser = build_parser()
        args = parser.parse_args(["merge", "base.env", "target.env"])
        assert args.command == "merge"

    def test_diff_summary_flag(self):
        parser = build_parser()
        args = parser.parse_args(["diff", "base.env", "target.env", "--summary"])
        assert args.summary is True

    def test_merge_default_strategy(self):
        parser = build_parser()
        args = parser.parse_args(["merge", "base.env", "target.env"])
        assert args.strategy == "use_target"

    def test_merge_strategy_use_base(self):
        parser = build_parser()
        args = parser.parse_args(["merge", "base.env", "target.env", "--strategy", "use_base"])
        assert args.strategy == "use_base"


class TestCmdDiff:
    def test_diff_output_printed(self, base_env_file, target_env_file, capsys):
        ret = main(["diff", str(base_env_file), str(target_env_file)])
        assert ret == 0
        captured = capsys.readouterr()
        assert "DEBUG" in captured.out

    def test_diff_summary_output(self, base_env_file, target_env_file, capsys):
        ret = main(["diff", str(base_env_file), str(target_env_file), "--summary"])
        assert ret == 0
        captured = capsys.readouterr()
        assert captured.out.strip() != ""


class TestCmdMerge:
    def test_merge_prints_to_stdout(self, base_env_file, target_env_file, capsys):
        ret = main(["merge", str(base_env_file), str(target_env_file)])
        assert ret == 0
        captured = capsys.readouterr()
        assert "APP_NAME" in captured.out

    def test_merge_writes_output_file(self, base_env_file, target_env_file, tmp_path):
        out_file = tmp_path / "merged.env"
        ret = main(["merge", str(base_env_file), str(target_env_file), "-o", str(out_file)])
        assert ret == 0
        assert out_file.exists()
        content = out_file.read_text()
        assert "APP_NAME" in content

    def test_merge_use_base_strategy(self, base_env_file, target_env_file, capsys):
        ret = main(["merge", str(base_env_file), str(target_env_file), "--strategy", "use_base"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "false" in captured.out  # DEBUG=false from base
