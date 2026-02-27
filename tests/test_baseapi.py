import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Provide a minimal stub for optional langchain dependency during unit tests.
prompts_mod = types.ModuleType("langchain_core.prompts")


class _PromptTemplate:
    @classmethod
    def from_template(cls, value):
        return value


prompts_mod.SystemMessagePromptTemplate = _PromptTemplate
prompts_mod.HumanMessagePromptTemplate = _PromptTemplate
sys.modules.setdefault("langchain_core.prompts", prompts_mod)

from Lib.baseapi import BaseAPI


class DemoAPI(BaseAPI):
    pass


def test_get_file_path_returns_absolute_file_path(tmp_path):
    absolute_file = tmp_path / "prompt.md"
    absolute_file.write_text("hello", encoding="utf-8")

    api = DemoAPI()
    assert Path(api._get_file_path(str(absolute_file))) == absolute_file


def test_get_file_path_returns_data_root_path_when_file_exists(tmp_path, monkeypatch):
    root_file = tmp_path / "prompt.md"
    root_file.write_text("hello", encoding="utf-8")

    monkeypatch.setattr("Lib.baseapi.DATA_DIR", str(tmp_path))

    api = DemoAPI()
    assert Path(api._get_file_path("prompt.md")) == root_file


def test_get_file_path_returns_module_scoped_path_when_file_exists(tmp_path, monkeypatch):
    module_dir = tmp_path / "test_baseapi"
    module_dir.mkdir()
    expected_file = module_dir / "prompt.md"
    expected_file.write_text("hello", encoding="utf-8")

    monkeypatch.setattr("Lib.baseapi.DATA_DIR", str(tmp_path))

    api = DemoAPI()
    assert Path(api._get_file_path("prompt.md")) == expected_file


def test_get_file_path_raises_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("Lib.baseapi.DATA_DIR", str(tmp_path))

    api = DemoAPI()
    with pytest.raises(FileNotFoundError, match="File not exist"):
        api._get_file_path("missing.md")
