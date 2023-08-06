"""
LangTrans
---------
To customize/upgrade the syntax of any programming language.
Docs: https://bijinregipanicker.gitbook.io/langtrans/

License
-------
MIT License
Copyright (c) 2021 Bijin Regi Panicker
See LICENSE file for orginal text.
"""
from os import system
from os.path import dirname
import os
from sys import argv, exit as sys_exit
from functools import partial
from typing import Any, Match, Pattern, Dict, Union, Optional, List, Tuple
from colorama import init, Fore


# Types ------------------------------
_RegexPattern = Pattern[str]  # Compiled Regex
_StringMatch = Match[str]  # Matched String
_ErrorDetails = Dict[str, Union[_RegexPattern, str]]
_ErrorDictionary = Dict[str, _ErrorDetails]
_UnmatchedPatterns = Dict[str, Tuple[_RegexPattern, ...]]
_MatchOptions = Dict[
    str,
    Tuple[
        _RegexPattern,  # regex
        Tuple[str, ...],  # tokens
        bool,  # Global
        Tuple[
            _UnmatchedPatterns, Tuple[_RegexPattern, ...]
        ],  # unmatched_tokens  # unmatched_parts
        Dict[str, str],  # defaults
        bool,  # once
        Optional[_ErrorDictionary],  # err
    ],
]
_MatchParts = Dict[str, List[Tuple[str, Dict[str, str]]]]
_OutsideOptions = Optional[Dict[str, _ErrorDictionary]]
_TokenPattern = Optional[Dict[str, str]]
_NextOptions = Optional[Union[Tuple[str, ...]]]
_TokenProcessingOptions = Dict[
    str, Union[Tuple[Tuple[Union[_RegexPattern, str], str], ...], Tuple[str, ...], str]
]
_TokenOptions = Dict[str, _TokenProcessingOptions]
_OperationTuples = Tuple[_TokenOptions, _NextOptions]
_TranslationOptions = Dict[str, _OperationTuples]
_ParseYAMLDetails = Tuple[
    Tuple[_MatchOptions, _TranslationOptions, _OutsideOptions], _TokenPattern
]
_Collections = Optional[Dict[str, Optional[List[str]]]]
_AfterProcessing = Optional[Union[List[str], str, Dict[str, str]]]
_ArbitraryDict = Dict[str, Dict[str, Any]]
_VariablesDict = Dict[str, str]
_ErrorTokensDict = Dict[str, Union[str, int, float, bool]]
_TargetStringLines = Optional[Tuple[int, int, List[str]]]
_CompileErrorTuple = Tuple[Dict[str, _ErrorDictionary], _OutsideOptions]


# Init Colorama -----------------------------------
init(autoreset=True)
error_msg = Fore.RED + "Error:"


def sanitize_regex(regex: str) -> _RegexPattern:
    """
    Sanitizes the regular expression pattern.

    :param regex: The regular expression pattern to compile.
    :type regex: str

    :return: A compiled regular expression pattern object.
    :rtype: _RegexPattern

    :raises re.error: If the regular expression pattern is invalid.

    It sanitizes the pattern by replacing spaces and `~` with regex to allow for optional
    whitespace. It then compiles the pattern and returns the compiled.
    """

    regex = regex.replace(" ", r"\s+").replace("~", r"\s*")

    try:
        return re_compile(regex, 8)  # re.MULTILINE=8
    except re_error as error:
        print(error_msg, "Invalid regex")
        print(error.msg)
        print("Regex:", regex.replace("\n", r"\n").replace("\t", r"\t"))
        if error.pos is not None:
            print(" " * (error.pos + 7) + "^")
        raise error


def check_collections(calls: List[str], collections: _Collections) -> Tuple[str, ...]:
    """
    Adds collections to the call list.

    :param calls: A list of collection names and part names.
    :type calls: List[str]

    :param collections: A dictionary of collections and their names.
    :type collections: _Collections

    :return: A tuple of the collection-replaced call list.
    :rtype: Tuple[str, ...]

    :raises KeyError: If a collection is not found.

    If a collection name starts with '$', the function looks up the collection in the
    collections dictionary and replaces the collection name with the collection values.
    """

    if not collections:
        return tuple(calls)

    new_collections: List[str] = []
    for collection in calls:
        if collection.startswith("$"):
            collection_name = collection[1:]
            try:
                collection_values = collections[collection_name]
                if collection_values is not None:
                    new_collections.extend(collection_values)
            except KeyError as key_error:
                raise KeyError(
                    f"Error: Collection ${collection_name} not found"
                ) from key_error
        else:
            new_collections.append(collection)

    return tuple(new_collections)


def extract_token_options(
    definition: Dict[str, Any], collections: _Collections, variables: _VariablesDict
) -> Optional[
    Tuple[
        _UnmatchedPatterns,
        Dict[str, str],
        Tuple[_TokenOptions, Optional[Tuple[str, ...]]],
    ]
]:
    """
    Extracts token options from the definition.

    :param definition: Contains token options.
    :type definition: Dict[str, Any]

    :param collections: Dictionary of collections and their names.
    :type collections: _Collections

    :return: unmatched_patterns, default values, translation options, and next call list.
    :rtype: Tuple[_UnmatchedPatterns, Dict[str, str], Tuple[_TokenOptions,
            Optional[Tuple[str, ...]]]]

    :raises KeyError: If a collection is not found.

    It extracts the token options from the definition and returns the unmatched patterns,
    default values, translation options, and next call list.
    """

    translation_options: _TokenOptions = {}
    unmatched_patterns: _UnmatchedPatterns = {}
    defaults: Dict[str, str] = {}
    tokens: list = definition.get("tokens", [])

    for token_name, options in definition.items():
        if isinstance(options, Dict):
            processing_options: _TokenProcessingOptions = {}
            # Token options
            for option, value in options.items():
                if option == "eachline":
                    processing_options["eachline"] = value
                elif option == "replace":
                    try:
                        processing_options["replace"] = tuple(
                            [
                                (sanitize_regex(reprgx[0]), reprgx[1])  # For replacing
                                if len(reprgx) == 2
                                else (sanitize_regex(reprgx[0]), "")  # For removing
                                for reprgx in value
                            ]
                        )
                    except re_error as error:
                        print(f"Location: Replace option for token({token_name})")
                        raise error
                elif option == "call":
                    processing_options["call"] = check_collections(value, collections)
                elif option == "unmatch":
                    if not isinstance(value, list):
                        value = (value,)
                    try:  # Compiling regex
                        unmatched_patterns[token_name] = tuple(
                            [
                                sanitize_regex(replace_variables(variables, rgx))
                                for rgx in value
                            ]
                        )
                    except re_error as error:
                        print(f"Location: Unmatch for token({token_name})")
                        raise error
                elif option == "default":
                    defaults[token_name] = value
            if "," in token_name:  # Splitting Token options
                for token in token_name.split(","):
                    if token not in tokens:
                        return print(f"Error: {token} not found in tokens")  # TypeError
                    translation_options[token] = processing_options
                continue
            if token_name not in tokens:
                return print(
                    f"{error_msg} {token_name} not found in tokens"
                )  # TypeError
            translation_options[token_name] = processing_options

    # Next Options
    next_value = definition.get("next", None)
    next_collections = (
        check_collections(next_value, collections) if next_value else None
    )

    return (
        unmatched_patterns,
        defaults,
        (
            translation_options,
            next_collections,
        ),
    )


def replace_variables(
    global_variables: _VariablesDict,
    source_string: str,
) -> str:
    """
    Replaces variable_name with its variable_value.

    :param global_vars: A dictionary of global variables.
    :type global_vars: _VariablesDict

    :param source_string: A string containing <var_name>.
    :type source_string: str

    :return: A variable-replaced string.
    :rtype: str

    This function replaces all occurrences of variable_name in the `source_string` string
    with their corresponding values in the `global_variables` dictionary. The replacement
    is done in reverse order of the items to ensure that longer variable names are
    replaced before shorter ones.
    """
    for variable_name, variable_value in reversed(global_variables.items()):
        source_string = source_string.replace(f"<{variable_name}>", variable_value)
    return source_string


def compile_error_regexes(
    error_definitions: _ArbitraryDict, global_variables: _VariablesDict
) -> _ArbitraryDict:
    """
    Compiles regex patterns for each error in the errors dictionary.

    :param error_definitions: A dictionary of errors and their properties.
    :type error_definitions: _ArbitraryDict

    :param global_variables: A dictionary of global variables.
    :type global_variables: _VariablesDict

    :return: The `errors` dictionary with compiled regex patterns.
    :rtype: _ArbitraryDict
    """
    result = {}

    for error_name, error in error_definitions.items():
        if error_name == "outside":
            result[error_name] = compile_error_regexes(error, global_variables)
        else:
            result[error_name] = error.copy()
            result[error_name]["regex"]["pattern"] = sanitize_regex(
                replace_variables(global_variables, error["regex"])
            )

    return result


def compile_error_regex_in_file(
    file_name: str, global_variables: _VariablesDict
) -> _CompileErrorTuple:
    """
    Compiles regexes in an error file.

    :param file_name: Name of errfile.
    :type file_name: str

    :param global_variables: Global variables.
    :type global_variables: _VariablesDict

    :return: Tuple of dictionaries, one compiled error inside and one for outside part.
    :rtype: _CompileErrorTuple

    Loads an error definitions file, compiles the regular expressions in the error
    definitions, and separates 'outside' errors.
    """
    error_definitions = load_yaml_file(file_name)
    outside_errors = {}

    for error_part, errors in error_definitions.items():
        compiled_errors = compile_error_regexes(errors, global_variables)
        if "outside" in compiled_errors:
            outside_errors[error_part] = compiled_errors.pop("outside")

    if "outside" in error_definitions:  # Outside errors not related to any part
        outside_errors[""] = error_definitions.pop("outside")

    return error_definitions, outside_errors


def extract(
    spattern: _ArbitraryDict,
) -> Tuple[
    _AfterProcessing, Tuple[_MatchOptions, _TranslationOptions, _OutsideOptions]
]:
    """
    This function extracts contents needed from yaml file with regex.

    :param spattern: Dictionary with yaml file details.
    :return: after command and (match options, token options).
    """
    # Importing builtin variables
    variables = load_variables(os.path.join(dirname(__file__), "builtin"))
    # Settings-------------------------------------------------------
    after = errfile = outside = collections = None
    if "settings" in spattern:
        setting = spattern.pop("settings")
        after = setting.get("after")
        if "varfile" in setting:  # Importing variables from varfile
            variables.update(load_variables(setting["varfile"]))
        if "variables" in setting:  # Adding variables in settings
            variables.update(setting["variables"])
        if "errfile" in setting:
            errfile, outside = compile_error_regex_in_file(
                os.path.join(dirname(__file__), setting["errfile"]), variables
            )
        collections = setting.get("collections")
    # ----------------------------------------------------------------
    trans_options: _TranslationOptions = {}
    match_options: _MatchOptions = {}
    try:
        for part, sdef in spattern.items():
            for opt in sdef.values():
                if isinstance(opt, Dict) and "replace" in opt:
                    for replace in opt[
                        "replace"
                    ]:  # Replacing variables in replace option
                        replace[0] = replace_variables(variables, replace[0])
            regex = sanitize_regex(
                replace_variables(variables, sdef["regex"])
            )  # Compiled regex without variables
            tokens = tuple(sdef["tokens"])  # Token_names
            if regex.groups != len(tokens):
                if regex.groups == 0 and len(tokens) < 2:
                    regex = sanitize_regex(f"({regex.pattern})")
                else:
                    print("Part:", part)
                    print("Token Names:", len(tokens), "Capture Groups:", regex.groups)
                    sys_exit(
                        error_msg
                        + " Number of token names is not equal to number of capture groups"
                    )
            result = extract_token_options(sdef, collections, variables)
            if result is None:
                print(f"Error: failed to extract token options for part: {part}")
                continue

            unmatches, defaults, tknopns = result

            if match_var := var_rgx.search(regex.pattern):
                print(Fore.YELLOW + "Warning:", match_var.group(), "not found")
            match_options[part] = (
                regex,
                tokens,
                "global" not in sdef or sdef["global"],  # Checking Global
                (  # Unmatch regexs for tokens
                    unmatches,
                    (  # Unmatch regexs for part
                        tuple(
                            [
                                sanitize_regex(replace_variables(variables, unmatch))
                                for unmatch in sdef["unmatch"]
                            ]
                        )
                        if "unmatch" in sdef
                        else ()
                    ),
                ),
                defaults,
                "once" in sdef and sdef["once"],
                (errfile[part] if errfile and part in errfile else None),
            )
            trans_options[part] = tknopns

    except (re_error, TypeError):  # Regex and unknown token option error
        sys_exit(f"Part:{part}")
    except KeyError as key_error:  # For part without regex or tokens
        sys_exit(f"{error_msg} {key_error} not found in {part}")
    return after, (match_options, trans_options, (outside if errfile else None))


def report_syntax_error(
    error_part: str,
    error_message: str,
    error_name: str,
    match: _StringMatch,
    tokens: dict,
    source_content: str,
    matched_string: str,
) -> None:
    """
    Reports syntax error messages in a colored format.

    :param error_part: Name of the part where error occurred.
    :type error_part: str

    :param error_message: The error message.
    :type error_message: str

    :param error_name: The name of the error.
    :type error_name: str

    :param match: The string match object of the error.
    :type match: _StringMatch

    :param tokens: Dictionary of variables for replacement in the error message.
    :type tokens: _VariablesDict

    :param source_content: The source code content.
    :type source_content: str

    :param matched_string: The string in the source content that matched the error pattern.
    :type matched_string: str

    :return: None

    This function takes in error details and source content, finds the line of error
    in the source content, and prints out an error report in a colored format. It
    terminates the program after printing the error.
    """
    result = find_substring_lines(source_content.splitlines(), matched_string)

    if result is None:
        print("Error: Cannot find the error in the source content.")
        sys_exit()

    start_line, _, matched_lines = result
    highlighted_part = match.group()

    if error_part:  # Print part name
        print(f"[{Fore.MAGENTA + error_part + Fore.RESET}]")

    first_line = matched_lines[0].lstrip()
    line_number = str(start_line + 1) + " |"

    # Print error line with error part highlighted
    print(
        Fore.CYAN + line_number,
        first_line.replace(highlighted_part, Fore.RED + highlighted_part + Fore.RESET),
    )

    replaced_message = replace_variables(
        {
            "$" + str(idx): token for idx, token in enumerate(match.groups(), start=1)
        },  # Error variables
        replace_variables(tokens, error_message),  # Main variables
    )

    # Print error name
    print(
        " " * (first_line.index(highlighted_part) + len(line_number)),
        Fore.RED + error_name.replace("_", " "),
    )

    # Print error message
    print(Fore.YELLOW + replaced_message)

    sys_exit()


# List of "once: True" parts that are already matched
once_complete = []


def match_parts(
    source_content: str, match_options: _MatchOptions, is_recursion: bool
) -> _MatchParts:
    """
    Matches parts of source code.

    :param source_code: source code.
    :type source_code: str

    :param match_options: Options for each part in yaml file.
    :type match_options: _MatchOptions

    :param is_recursive: Boolean to find if the convert function is in recursion or not.
    :type is_recursive: bool

    :return: Return matched parts and tokens.
    :rtype: _MatchParts

    This function takes in source code and match options for each part and returns
    matched parts and tokens. It also checks for errors in the source code and
    terminates the program if any error is found.
    """

    part_matches = {}
    for part, options in match_options.items():
        (
            part_pattern,
            token_names,
            is_global,
            (unmatched_tokens, unmatched_parts),
            defaults,
            once,
            err,
        ) = options
        if not is_recursion:
            if not is_global:
                continue
            if once:
                if part in once_complete:
                    continue
                once_complete.append(part)
        part_match = []  # Part matches
        for match in part_pattern.finditer(source_content):
            match_string: str = match.group()
            if unmatched_parts and any(
                (bool(rgx.search(match_string)) for rgx in unmatched_parts)
            ):
                continue
            token_match = {
                token_match_name: (
                    match_variable
                    if match_variable is not None
                    else defaults.get(token_match_name, "")
                )
                for token_match_name, match_variable in zip(token_names, match.groups())
            }
            if err:  # If error definition exists
                from re import search as re_search

                for name, error in err.items():  # Static Code Analysis
                    regex = (
                        error["regex"]
                        if isinstance(error["regex"], Pattern)
                        else re_error(error["regex"])
                    )
                    if isinstance(regex, (str, Pattern)):
                        err_match = re_search(regex, match_string)

                    error_message = error["msg"]
                    if error_message is None or not isinstance(error_message, str):
                        error_message = ""

                    if err_match:
                        report_syntax_error(
                            part,
                            error_message,
                            name,
                            err_match,
                            token_match,
                            source_content,
                            match_string,
                        )
            if unmatched_tokens and any(
                (  # Checking unmatch on every token
                    bool(rgx.search(match_string))
                    for token_match_name, match_string in token_match.items()
                    for rgx in unmatched_tokens.get(token_match_name, ())
                )
            ):
                continue
            part_match.append((match_string, token_match))
        if part_match:
            part_matches.update({part: part_match})
    return part_matches


def find_outside_errors(outside_options: _OutsideOptions, source_code: str) -> None:
    """
    Finds syntax errors in the source code and shows error messages.

    :param outside_options: A dictionary mapping parts of the outside options
    :type outside_options: _OutsideOptions

    :param source_code: The source code content to check for errors.
    :type source_code: str

    :return: None

    This function checks for matches of the regular expression patterns associated
    with each error in the outside options, in the provided source_code. If a match
    is found, an error report is generated.
    """

    if not outside_options:
        return

    for part, errors in outside_options.items():
        for error_name, error_details in errors.items():
            regex_pattern = error_details.get("regex")
            if isinstance(regex_pattern, Pattern):
                error_match = regex_pattern.search(source_code)
                if error_match:
                    error_message = error_details.get("msg")
                    if error_message is None or not isinstance(error_message, str):
                        error_message = ""
                    matched_text = error_match.group()

                    report_syntax_error(
                        part,
                        error_message,
                        error_name,
                        error_match,
                        {},
                        source_code,
                        matched_text,
                    )


def convert_syntax(
    extracted_yaml_details: _ParseYAMLDetails,
    original_content: str,
    is_recursive: bool = False,
    conversion_parts: Union[Tuple[str, ...]] = (),
) -> str:
    """
    This function converts new syntax to original syntax as described in extracted_yaml_details.

    :param extracted_yaml_details: Extracted from yaml includes match_parts patterns
    :type extracted_yaml_details: _ParseYAMLDetails

    :param original_content: Original content in the new syntax that needs to be converted.
    :type original_content: str

    :param is_recursive: Boolean flag indicating if the conversion should be recursive.
    :type is_recursive: bool

    :param conversion_parts: Specific parts that need to be converted.
    :type conversion_parts: Union[Tuple[str, ...]]

    :return: The converted content in the original syntax.
    :rtype: str

    This function first matches the original content with the match_parts patterns in the
    extracted_yaml_details. If a match is found, the corresponding transformation is applied to
    the matched part. This process is repeated until no more matches are found.
    """
    (
        match_rules,
        transform_rules,
        outside_errors,
    ), pattern_templates = extracted_yaml_details
    iteration_count = 0

    if is_recursive:
        match_rules = {part: match_rules[part] for part in conversion_parts}
    elif outside_errors:  # Outside error checks
        find_outside_errors(outside_errors, original_content)

    while True:
        matched_parts = match_parts(original_content, match_rules, is_recursive)
        if not matched_parts:  # Break when no match found
            break
        elif iteration_count > 100:
            print(error_msg + " Loop Limit Exceeded")
            print(
                "Bug Locations:\n",
                "\n".join(
                    (f"{part}:{matches}" for part, matches in matched_parts.items())
                ),
            )
            sys_exit()
        iteration_count += 1

        for part, matches in matched_parts.items():
            if pattern_templates is not None:
                pattern = pattern_templates[part]
            token_options, next_options = transform_rules[part]
            for part_match, token_match in matches:
                temp_pattern = pattern
                for token_name, match in token_match.items():
                    if token_name not in token_options:
                        continue
                    opts = token_options[token_name]  # Token options
                    for option in opts:
                        if option == "replace":  # For replace option
                            replacements = opts["replace"]
                            from re import sub

                            replacements_tuple = (*replacements,)
                            for (
                                rgx,
                                replacement,
                            ) in replacements_tuple:  # pattern-match and replace
                                match = sub(rgx, replacement, match)
                        elif option == "call":
                            calls = opts["call"]
                            match = re_convert(
                                original_content=match, conversion_parts=calls
                            )
                        elif option == "eachline":  # For eachline option
                            line = opts["eachline"]
                            line_string = str(line)
                            match = "\n".join(
                                [
                                    line_string.replace("<line>", l)
                                    for l in match.split("\n")
                                    if l.strip() != ""
                                ]
                            )
                    token_match[token_name] = match
                temp_pattern = replace_variables(
                    token_match, replace_variables(token_match, temp_pattern)
                )
                if next_options:  # Next Part option
                    temp_pattern = re_convert(
                        original_content=temp_pattern, conversion_parts=next_options
                    )
                try:
                    original_content = original_content.replace(
                        part_match, temp_pattern
                    )
                except ValueError:
                    print(temp_pattern)
    return original_content


def find_substring_lines(
    code_lines: List[str], target_string: str
) -> _TargetStringLines:
    """
    Finds the lines in which the target string is located.

    :param code_lines: A list of lines of code being checked for the target string.
    :type code_lines: List[str]

    :param target_string: The string to be found in the lines.
    :type target_string: str

    :return: Tuple with starting position, length, and a list of the target string lines.
    :rtype: Optional[Tuple[int, int, List[str]]]
    """

    target_lines = target_string.splitlines()
    target_length = len(target_lines)
    possible_start_indices = len(code_lines) - target_length + 1

    for target_index in range(possible_start_indices):
        if target_lines[0] in code_lines[target_index]:  # If first target_line matched
            matched_lines = code_lines[
                target_index : target_index + target_length
            ]  # rest of target_line
            if all(
                subline in line_part
                for subline, line_part in zip(target_lines[1:], matched_lines)
            ):
                return target_index, target_length, matched_lines
    return None


def load_yaml_file(file: str) -> Dict[str, Any]:
    """
    Adds .yaml file extension and extracts dictionary of YAML data in file.

    :param file_path: The path to the YAML file.
    :type file_path: str

    :return: A dictionary containing the YAML data.
    :rtype: Dict[str, Any]
    """
    from yaml import load, SafeLoader
    from yaml.scanner import ScannerError
    from yaml.parser import ParserError

    file += ".yaml"
    try:
        with open(file, encoding="utf-8") as yaml_file:
            return load(yaml_file.read(), Loader=SafeLoader)
    except (
        ScannerError,
        ParserError,
    ) as invalid_file:  # Error message for Invalid Yaml File
        print(error_msg, file, "is invalid")
        print(invalid_file.problem, invalid_file.context)
        if invalid_file.problem_mark is not None:
            print(invalid_file.problem_mark.get_snippet())
        sys_exit()
    except FileNotFoundError:
        sys_exit(f"{error_msg} {file} not found")


def extract_yaml_details(
    source_path: str, target_path: str
) -> Tuple[_AfterProcessing, _ParseYAMLDetails]:
    """
    Extracts details from source and target YAML files.

    :param source_path: The path to the source YAML file.
    :type source_path: str

    :param target_path: The path to the target YAML file.
    :type target_path: str

    :return: A tuple containing the after command and YAML details.
    :rtype: Tuple[_AfterProcessing, _ParseYAMLDetails]

    :raises ValueError: If the source YAML file is invalid.
    """
    source_yaml = load_yaml_file(source_path)
    target_yaml = load_yaml_file(target_path)

    # Check if all parts in source YAML file have a corresponding part in target YAML file
    for part in source_yaml:
        if not (part in target_yaml or part == "settings"):
            if part.startswith("_"):
                base_part = part[2:]
                if base_part in source_yaml:
                    source_yaml[part]["tokens"] = source_yaml[base_part]["tokens"]
                else:
                    raise ValueError(f"{error_msg} {base_part} for {part} not found")
                if base_part in target_yaml:
                    target_yaml[part] = target_yaml[base_part]
                    continue
                part = base_part
            if not source_yaml[part]["tokens"]:
                target_yaml[part] = ""
                continue
            raise ValueError(f"{error_msg} Template for {part} not found")

    after_command, extracted_source_yaml = extract(source_yaml)
    return after_command, (extracted_source_yaml, target_yaml)


def load_variables(file_path: str) -> _VariablesDict:
    """
    Loads variables from a YAMP file.

    :param file: Path of the YAML file.
    :type file: str

    :return: Dictionary of variables.
    :rtype: Dict[str, Any]
    """
    variables = {}
    try:
        loaded_variables = load_yaml_file(file_path)
        if loaded_variables is not None:
            variables.update(loaded_variables)
    except ValueError:
        sys_exit(f"Error: Invalid YAML file: {file_path}\n")
    return variables


def load_compiled_yaml_details(
    filename: str,
) -> Tuple[_AfterProcessing, _ParseYAMLDetails]:
    """
    Loads compiled yaml_details from .ltz file.

    :param filename: Name of the file.
    :type filename: str

    :return: yaml_details from .ltz file.
    :rtype: Tuple[_AfterProcessing, _ParseYAMLDetails]
    """
    from pickle import load

    try:
        with open(f"{filename}.ltz", "rb") as compiled_yaml:
            return load(compiled_yaml)
    except FileNotFoundError as fnf_error:
        print(f"File {fnf_error.filename} not found.")
        sys_exit()


def print_yaml_documentation(source_file: str) -> None:
    """
    Prints documentation of the part in yaml file.

    :example: python langtrans.py -d source.

    :param file: Path of the file.
    :type file: str

    :return: None
    """
    yaml_content = load_yaml_file(source_file)

    if "settings" in yaml_content:
        settings = yaml_content["settings"]
        if "lang" in settings:
            print("Language:", settings["lang"])
        if "author" in settings:
            print("Author:", settings["author"])
        del yaml_content["settings"]

    documentation_list = []
    longest_part_length = longest_tokens_length = 7

    for part, details in yaml_content.items():
        tokens_str = (
            str(details.get("tokens", ""))
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace(" ", "")
        )
        about = details.get("doc", "")

        documentation_list.append((part, tokens_str, about))

        if len(part) > longest_part_length:
            longest_part_length = len(part)
        if len(tokens_str) > longest_tokens_length:
            longest_tokens_length = len(tokens_str)

    print(f"{'Part':<{longest_part_length}} {'Tokens':<{longest_tokens_length}} About")

    for part, tokens_str, about in documentation_list:
        about_with_indentation = about.replace(
            "\n", "\n" + " " * (longest_part_length + longest_tokens_length + 2)
        )
        print(f"{part:<{longest_part_length}}")
        print(f"{tokens_str:<{longest_tokens_length}}")
        print(f"{about_with_indentation}")


if __name__ == "__main__":
    if len(argv) == 1 or (len(argv) == 2 and argv[1] == "-h"):
        print("Arg usage: <SoureFileName> <OutputFileName> <SyntaxRepr> <PatternRepr>")
        sys_exit("SyntaxRepr,PatternRepr: without extension(.yaml)")
    elif len(argv) < 3:
        sys_exit(error_msg + " Insufficient number of arguments")

    try:
        YAML_DETAILS = None

        # Terminal Options-------------------------------------------
        YES = "-y" in argv  # To run after command automatically
        VERBOSE = "-v" in argv  # Verbose Mode - print source code
        NO = "-n" in argv  # To exit without executing after command

        if VERBOSE:
            argv.remove("-v")
        if YES:
            argv.remove("-y")
        if NO:
            argv.remove("-n")
        # ------------------------------------------------------------
        if "-c" in argv:  # Compile into ltz
            from pickle import dump, HIGHEST_PROTOCOL
            from re import error as re_error
            from re import compile as re_compile

            var_rgx = re_compile(r"<\w+>")
            argv[-1] += ".ltz"
            with open(argv[-1], "wb") as litz_file:
                dump(
                    extract_yaml_details(argv[2], argv[3]),
                    litz_file,
                    protocol=HIGHEST_PROTOCOL,
                )
            print(Fore.GREEN + "Compiled successfully")
            sys_exit("File saved as " + argv[-1])
        elif "-f" in argv:  # Run compiled ltz
            argv.remove("-f")
            YAML_DETAILS = load_compiled_yaml_details(argv[-1])
        elif "-d" in argv:
            print_yaml_documentation(argv[-1])
            sys_exit()
        else:
            from re import error as re_error
            from re import compile as re_compile

            var_rgx = re_compile(r"<\w+>")
            YAML_DETAILS = extract_yaml_details(argv[3], argv[4])
        # -------------------------------------------------------------------
        AFTER_COMMAND, YAML_DETAILS = YAML_DETAILS
        with open(argv[1], encoding="utf-8") as InputFile:
            content = InputFile.read()
        re_convert = partial(
            convert_syntax, extracted_yaml_details=YAML_DETAILS, is_recursive=True
        )
        targetcode = convert_syntax(YAML_DETAILS, content)
        with open(argv[2], "w", encoding="utf-8") as OutputFile:
            OutputFile.write(targetcode)
        print(Fore.GREEN, "Saved as", argv[2])
        if VERBOSE:
            print(targetcode)
        # For after command in settings
        if not NO and AFTER_COMMAND:  # Not None
            if isinstance(AFTER_COMMAND, Dict):  # After command for different OS
                from platform import system as systm

                osname = systm().lower()  # Current os name
                if osname not in AFTER_COMMAND:
                    print(
                        f"{error_msg} No after command for {osname}. OS name eg. linux, windows"
                    )
                    sys_exit()
                AFTER_COMMAND = AFTER_COMMAND[osname]
            if isinstance(AFTER_COMMAND, list):  # For multiple commands
                AFTER_COMMAND = " && ".join(AFTER_COMMAND)
            # To use address of source and target file in 'AFTER_COMMAND' command
            after_var = (
                ("$target", argv[2]),
                ("$source", argv[1]),
                ("$current", dirname(__file__)),
            )
            for var, val in after_var:
                AFTER_COMMAND = AFTER_COMMAND.replace(var, val)
            if YES:
                system(AFTER_COMMAND)
                sys_exit()
            print("\nEnter to run and n to exit\nCommand:", AFTER_COMMAND)
            inp = input()
            if inp.lower() != "n":
                system(AFTER_COMMAND)
    except Exception as exception_error:
        print(Fore.RED + "Program Error:", exception_error)
