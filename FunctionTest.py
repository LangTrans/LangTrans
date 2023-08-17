import unittest
import LangTrans
import re
import contextlib
import io
import sys

@contextlib.contextmanager
def capture_print_output():
    captured_output = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured_output
    try:
        yield captured_output
    finally:
        sys.stdout = original_stdout
class TransTest(unittest.TestCase):
	invalid_regex = r"[a-z"
	# '\x1b[31m' means red color in terminal (ANSI escape code)
	regex_err_msg = '\x1b[31mError: Invalid regex\nunterminated character set\nRegex: [a-z\n       ^\n' 
	
	def test_sanitize_regex(self):
		# Chcking Compiled Pattern
		result = LangTrans.sanitize_regex(r"\((\s*\w+\s*(?:,\s*\w+\s*)*)\)\s*=>\s*{(\n(?:(?:(?:\t|\s)+)+?).*(?:(?:\n\\3.*)*\n*)*)}")
		self.assertFalse(" " in result.pattern or "~" in result.pattern)
		
		# Checking error msg
		with self.assertRaises(re.error):
			with capture_print_output() as output:
				LangTrans.sanitize_regex(self.invalid_regex)
		self.assertEqual(output.getvalue(),self.regex_err_msg)
		
		# Checking multiline support
		# TODO: Change this string into a custom syntax code 
		multiline_string = """\nstart of line\nsome content here\nend of line\n"""
		rgx = LangTrans.sanitize_regex(r"""^start(.|\n)+end""")
		match = rgx.search(multiline_string)
		self.assertIsNot(match,None)
		self.assertEqual(match.group(0),'start of line\nsome content here\nend')

	def test_check_collections(self):
		#No replacement
		calls = ['part1', 'part2', 'part3']
		collections = {}
		result = LangTrans.check_collections(calls, collections)
		self.assertEqual(result, ('part1', 'part2', 'part3'))

		#Replacement
		calls = ['$collection1', '$collection2', 'part3']
		collections = {'collection1': ['item1', 'item2'], 'collection2': ['item3']}
		result = LangTrans.check_collections(calls, collections)
		self.assertEqual(result, ('item1', 'item2', 'item3', 'part3'))

		#Missing collection
		calls = ['$collection1', 'part2']
		collections = {'collection2': ['item3']}
		with self.assertRaises(KeyError):
		    LangTrans.check_collections(calls, collections)
	def test_replace_variables(self):
		#Replacement
		global_variables = {
		    "var1": "value1",
		    "var2": "value2",
		    "var3": "value3",
		}
		source_string = "This is <var1> and <var2>."
		expected_result = "This is value1 and value2."

		result = LangTrans.replace_variables(global_variables, source_string)
		self.assertEqual(result, expected_result)
		# No Replacement
		global_variables = {
		    "var1": "value1",
		    "var2": "value2",
		}
		source_string = "No replacement needed."
		expected_result = "No replacement needed."

		result = LangTrans.replace_variables(global_variables, source_string)
		self.assertEqual(result, expected_result)

	def test_extract_token_options(self):
		# Basic
		definition = { # TEMPLATE
		    "tokens": ["token1", "token2"],
		    "token1": {
		        "eachline": "line_option",
		        "replace": [("pattern1", "replacement1")],
		        "call": ["collection1"],
		        "unmatch": "unmatch_<p>",
		        "default": "default_value",
		    },
		    "token2": {
		        "eachline": "line_option",
		        "replace": [("pattern2", "replacement2")],
		        "call": ["collection2"],
		    },
		    "next": ["collection3"],
		}
		collections = { # TEMPLATE
		    "collection1": ["value1"],
		    "collection2": ["value2"],
		    "collection3": ["value3"],
		}
		variables = {"p":"pattern"}

		result = LangTrans.extract_token_options(definition, collections, variables)

		expected_conversion_options = {# TEMPLATE
		'token1': {
					'call': ('collection1',),
		            'eachline': 'line_option',
		            'replace': (
		            	(LangTrans.sanitize_regex('pattern1'),'replacement1'),
		            )
		          },
		 'token2': {
		 			'call': ('collection2',),
		            'eachline': 'line_option',
		            'replace': (
		            	(LangTrans.sanitize_regex('pattern2'),'replacement2'),
		            )
		           }
		}
		expected_next_collections = ('collection3',)

		self.assertEqual(result[0],{'token1': (LangTrans.sanitize_regex('unmatch_pattern'),)})
		self.assertEqual(result[1],{"token1": "default_value"})
		self.assertEqual(result[2],(expected_conversion_options, expected_next_collections))
		# Missing collection
		definition = {
		    "tokens": ["token1"],
		    "token1": {
		        "call": ["$missing_collection"],
		    }
		}
		collections = {
		    "collection1": ["value1"],
		}
		with self.assertRaises(KeyError):
			LangTrans.extract_token_options(definition, collections, {})
		# Invalid Regex
		definition = {
		    "tokens": ["token1"],
		    "token1": {
		        "unmatch": self.invalid_regex,
		    }
		}
		with self.assertRaises(re.error):
			with capture_print_output() as output:
				LangTrans.extract_token_options(definition, {}, {})
		self.assertEqual(output.getvalue(),self.regex_err_msg+'Location: Unmatch for token(token1)\n')
	def test_extract(self):
		# Test basic extraction of a pattern with regex, tokens, and replace options
		spattern = {
		    "pattern1": {
		        "regex": r"(\d+)",
		        "tokens": ["number"],
		        "replace": [[r"\d+", "NUM"]],
		    }
		}

		after, extracted_data = LangTrans.extract(spattern)

		expected_after = None

		expected_match_options = {
		'pattern1': (LangTrans.sanitize_regex(r'(\d+)'),
              ('number',),
              True,
              ({}, ()),
              {},
              False,
              None)
		}

		expected_trans_options = {'pattern1': ({}, None)}

		expected_outside_options = None

		# Check if the extracted data matches the expected values
		self.assertEqual(after, expected_after)
		self.assertEqual(extracted_data[0], expected_match_options)
		self.assertEqual(extracted_data[1], expected_trans_options)
		self.assertEqual(extracted_data[2], expected_outside_options)

		spattern = {
		    "pattern2": {
		        "regex": TransTest.invalid_regex,
		        "tokens": ["token"],
		    }
		}
		with self.assertRaises(SystemExit):
			with capture_print_output() as output:
				LangTrans.extract(spattern)
		self.assertEqual(output.getvalue(),self.regex_err_msg+"Part:pattern2\n")
	def test_match_parts(self):
		# Test basic matching of a pattern with regex and token names
		source_content = "123 456 789"
		match_options = {
		    "pattern1": (
		        LangTrans.sanitize_regex(r"(\d+)"),
		        ("number",),
		        True,
		        ({}, ()),
		        {},
		        False,
		        None,
		    )
		}
		is_recursion = False

		result = LangTrans.match_parts(source_content, match_options, is_recursion)

		expected_result = {
		    "pattern1": [
		        ("123", {"number": "123"}),
		        ("456", {"number": "456"}),
		        ("789", {"number": "789"}),
		    ]
		}
		source_content = "123 456 789"
		match_options = {
		    "pattern1": (
		        LangTrans.sanitize_regex(r"(\d+)"),
		        ("number",),
		        True,
		        ({}, (LangTrans.sanitize_regex(r"\b456\b"),)),
		        {},
		        False,
		        None,
		    )
		}
		is_recursion = False

		result = LangTrans.match_parts(source_content, match_options, is_recursion)

		expected_result = {
		    "pattern1": [("123", {"number": "123"}), ("789", {"number": "789"})]
		}
		self.assertEqual(result, expected_result)
	def test_convert_syntax(self):
		# TODO: Thorough check needed for below test implementation
		extracted_yaml_details = (
		    (
		        {
		            "part1": (
		                LangTrans.sanitize_regex(r"(123)"),
		                ("num",),
		                True,
		                ({}, ()),
		                {},
		                False,
		                None,
		            )
		        },
		        {
		            "part1": (
		                {"num": {"replace":[["1","3"]]}},
		                (),
		            ),
		        },
		        {},
		    ),
		    {"part1": "<num>"},  # Replace with the actual pattern template
		)
		original_content = "123"
		is_recursive = False
		conversion_parts = ()

		result = LangTrans.convert_syntax(
		    extracted_yaml_details, original_content, is_recursive, conversion_parts
		)

		expected_result = "323"
		self.assertEqual(result,expected_result)

		#TODO: Test for condition `is_recursive=True`
	def test_find_substring_lines(self):
		code_lines = [
		    "This is a test.",
		    "Here's a multiline target string.",
		    "It spans multiple lines.",
		    "End of the target.",
		    "Some other code line."
		]
		target_string = "Here's a multiline target string.\nIt spans multiple lines.\nEnd of the target."

		result = LangTrans.find_substring_lines(code_lines, target_string)

		expected_result = (
		    1, 3, [
		        "Here's a multiline target string.",
		        "It spans multiple lines.",
		        "End of the target."
		    ]
		)
		self.assertEqual(result, expected_result)
		# No match
		code_lines = [
		    "This is a test.",
		    "Here's some code.",
		    "More code here.",
		    "The end of the code."
		]
		target_string = "Nonexistent target."

		result = LangTrans.find_substring_lines(code_lines, target_string)

		self.assertIsNone(result)
unittest.main()
