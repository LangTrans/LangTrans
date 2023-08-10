import pytest
import re
import os
from re import error as re_error
from re import compile as re_compile
from unittest.mock import patch

from LangTrans.LangTrans import sanitize_regex
from LangTrans.LangTrans import check_collections
from LangTrans.LangTrans import extract_token_options
from LangTrans.LangTrans import replace_variables
from LangTrans.LangTrans import compile_error_regexes
from LangTrans.LangTrans import compile_error_regex_in_file
from LangTrans.LangTrans import extract
from LangTrans.LangTrans import report_syntax_error
from LangTrans.LangTrans import match_parts
from LangTrans.LangTrans import find_outside_errors
from LangTrans.LangTrans import convert_syntax, _ParseYAMLDetails
from LangTrans.LangTrans import find_substring_lines
from LangTrans.LangTrans import load_yaml_file
from LangTrans.LangTrans import extract_yaml_details
from LangTrans.LangTrans import load_variables
from LangTrans.LangTrans import load_compiled_yaml_details
from LangTrans.LangTrans import print_yaml_documentation



# test sanitize_regex



# test check_collections
class TestCheckCollections:
    @staticmethod
    def test_empty_collections():
        calls = ["a", "b", "c"]
        collections = {}
        result = check_collections(calls, collections)
        assert result == ("a", "b", "c")

    @staticmethod
    def test_non_replacement():
        calls = ["a", "b", "c"]
        collections = {"x": ["1", "2", "3"]}
        result = check_collections(calls, collections)
        assert result == ("a", "b", "c")

    @staticmethod
    def test_replacement():
        calls = ["a", "$x", "c"]
        collections = {"x": ["1", "2", "3"]}
        result = check_collections(calls, collections)
        assert result == ("a", "1", "2", "3", "c")

    @staticmethod
    def test_missing_collection():
        calls = ["a", "$x", "c"]
        collections = {"y": ["1", "2", "3"]}
        with pytest.raises(KeyError, match=r"Collection \$x not found"):
            check_collections(calls, collections)

    @staticmethod
    def test_none_values_in_collection():
        calls = ["a", "$x", "c"]
        collections = {"x": None}
        result = check_collections(calls, collections)
        assert result == ("a", "c")



# test extract_token_options



# test replace_variables
@pytest.fixture
def global_variables():
    return {
        "var1": "Value1",
        "var2": "Value2",
        "longer_var": "LongerValue",
    }

def test_replace_variables_single(global_variables):
    source_string = "This is a test with <var1>."
    expected_result = "This is a test with Value1."
    result = replace_variables(global_variables, source_string)
    assert result == expected_result

def test_replace_variables_multiple(global_variables):
    source_string = "Replace <var1> and <var2>."
    expected_result = "Replace Value1 and Value2."
    result = replace_variables(global_variables, source_string)
    assert result == expected_result

def test_replace_variables_longer(global_variables):
    source_string = "Replace <longer_var> before <var2>."
    expected_result = "Replace LongerValue before Value2."
    result = replace_variables(global_variables, source_string)
    assert result == expected_result

def test_replace_variables_not_found(global_variables):
    source_string = "No variables here."
    expected_result = "No variables here."
    result = replace_variables(global_variables, source_string)
    assert result == expected_result

def test_replace_variables_empty(global_variables):
    source_string = ""
    expected_result = ""
    result = replace_variables(global_variables, source_string)
    assert result == expected_result


class TestReplaceVariables:
    global_vars = {
        "var1": "value1",
        "var2": "value2",
        "longer_variable": "longer_value"
    }

    def test_single_variable_replace(self):
        source_string = "This is a test with <var1>."
        expected_result = "This is a test with value1."
        assert replace_variables(self.global_vars, source_string) == expected_result

    def test_multiple_variable_replace(self):
        source_string = "Replace <var1> and <var2>."
        expected_result = "Replace value1 and value2."
        assert replace_variables(self.global_vars, source_string) == expected_result

    def test_longer_variable_name(self):
        source_string = "Replace <longer_variable> first and then <var1>."
        expected_result = "Replace longer_value first and then value1."
        assert replace_variables(self.global_vars, source_string) == expected_result

    def test_no_variable_to_replace(self):
        source_string = "No variables here."
        expected_result = "No variables here."
        assert replace_variables(self.global_vars, source_string) == expected_result
# test compile_error_regexes



# test compile_error_regex_in_file



# test extract



# test report_syntax_error



# test match_parts



# test find_outside_errors
class TestCodeChecker:
    @staticmethod
    def test_no_errors():
        outside_options = {}
        source_code = "valid source code without errors"
        find_outside_errors(outside_options, source_code)


# test convert_syntax
@pytest.fixture
def example_yaml_details():
    match_rules = {
        'part1': 'pattern1',
        'part2': 'pattern2'
    }
    transform_rules = {
        'part1': ({"token1": {"replace": [("pattern", "replacement")]}}, None),
        'part2': ({"token2": {"eachline": "<line>"}}, None)
    }
    outside_errors = None
    pattern_templates = {'part1': '<pattern1>', 'part2': '<pattern2>'}

    return (
        (match_rules, transform_rules, outside_errors),
        pattern_templates
    )


# test find_substring_lines
def test_find_substring_lines_multi_line_match():
    code_lines = [
        "def find_substring_lines(",
        "    code_lines: List[str], target_string: str",
        ") -> _TargetStringLines:",
        "    target_lines = target_string.splitlines()",
        "    target_length = len(target_lines)",
        "    possible_start_indices = len(code_lines) - target_length + 1",
    ]
    target_string = "target_length = len(target_lines)"

    result = find_substring_lines(code_lines, target_string)

    assert result == (4, 1, [code_lines[4]])

def test_find_substring_lines_no_match():
    code_lines = [
        "def find_substring_lines(",
        "    code_lines: List[str], target_string: str",
        ") -> _TargetStringLines:",
    ]
    target_string = "target_length = len(target_lines)"

    result = find_substring_lines(code_lines, target_string)

    assert result is None


# test load_yaml_file
class MockFile:
    def __init__(self, content):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def read(self):
        return self.content

def mock_open(file, *args, **kwargs):
    if file.endswith(".yaml"):
        return MockFile("data: example")
    else:
        raise FileNotFoundError

# Apply the mock_open function to the built-in open function
@pytest.fixture(autouse=True)
def mock_builtin_open(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open)



# test extract_yaml_details



# test load_variables



# test load_compiled_yaml_details



# test print_yaml_documentation
