import pytest
import re
import os
from re import error as re_error
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
from LangTrans.LangTrans import convert_syntax
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



# test compile_error_regexes



# test compile_error_regex_in_file



# test extract



# test report_syntax_error



# test match_parts



# test find_outside_errors

# test convert_syntax

# test find_substring_lines

# test load_yaml_file

# test extract_yaml_details

# test load_variables

# test load_compiled_yaml_details

# test print_yaml_documentation
