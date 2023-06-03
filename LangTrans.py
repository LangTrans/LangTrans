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
from os import system, name, path
from os.path import dirname
import os
from sys import argv, exit
from functools import partial
from typing import Any, Match, Pattern, Dict, Union, Optional, List, Tuple
from colorama import init, Fore

# Types------------------------------
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
        Tuple[_UnmatchedPatterns, Tuple[_RegexPattern, ...]],  # untkn  # unpart
        Dict[str, str],  # defaults
        bool,  # once
        Optional[_ErrorDictionary],  # err
    ],
]
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

# -----------------------------------
#  For colored error - Intialiazing colorama
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

    It sanitizes the pattern by replacing spaces with `\s+` and `~` with `\s*` to allow
    for optional whitespace. It then compiles the pattern and returns the compiled.
    """

    regex = regex.replace(" ", r"\s+").replace("~", r"\s*")

    try:
        return compile(regex, 8)  # re.MULTILINE=8
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


def tknoptions(
    sdef: Dict[str, Any], collections: _Collections, variables: _VariablesDict
) -> Tuple[
    _UnmatchedPatterns, Dict[str, str], Tuple[_TokenOptions, Optional[Tuple[str, ...]]]
]:
    """
    This function extracts token options from a yaml file.

    :param sdef: Contains token options.
    :param collections: Dictionary of collections and their names.
    :return: unmatches, default values, translation options, and next call list.
    """
    trans_option: _TokenOptions = {}
    unmatches: _UnmatchedPatterns = {}
    defaults: Dict[str, str] = {}
    tkns: list = sdef["tokens"]
    for tkname, opts in sdef.items():
        if isinstance(opts, Dict):
            opns: _TokenProcessingOptions = {}
            # Token options
            for opn, data in opts.items():
                if opn == "eachline":
                    opns["eachline"] = data
                elif opn == "replace":
                    try:
                        opns["replace"] = tuple(
                            [
                                (sanitize_regex(reprgx[0]), reprgx[1])  # For replacing
                                if len(reprgx) == 2
                                else (sanitize_regex(reprgx[0]), "")  # For removing
                                for reprgx in data
                            ]
                        )
                    except re_error as err:
                        print(f"Location: Replace option for token({tkname})")
                        raise err
                elif opn == "call":
                    opns["call"] = check_collections(data, collections)
                elif opn == "unmatch":
                    if not isinstance(data, list):
                        data = (data,)
                    try:  # Compiling regex
                        unmatches[tkname] = tuple(
                            [
                                sanitize_regex(replace_variables(variables, rgx))
                                for rgx in data
                            ]
                        )
                    except re_error as err:
                        print(f"Location: Unmatch for token({tkname})")
                        raise err
                elif opn == "default":
                    defaults[tkname] = data
            if "," in tkname:  # Spliting Token options
                for tk in tkname.split(","):
                    if tk not in tkns:
                        return print(f"Error: {tk} not found in tokens")  # TypeError
                    trans_option[tk] = opns
                continue
            if tkname not in tkns:
                return print(f"{error_msg} {tkname} not found in tokens")  # TypeError
            trans_option[tkname] = opns
            # Next Options
    return (
        unmatches,
        defaults,
        (
            trans_option,
            (check_collections(sdef["next"], collections) if "next" in sdef else None),
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
            result[error_name]["regex"] = sanitize_regex(
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
                    exit(
                        error_msg
                        + " Number of token names is not equal to number of capture groups"
                    )
            unmatches, defaults, tknopns = tknoptions(sdef, collections, variables)
            if m := var_rgx.search(regex.pattern):
                print(Fore.YELLOW + "Warning:", m.group(), "not found")
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
        exit(f"Part:{part}")
    except KeyError as err:  # For part without regex or tokens
        exit(f"{error_msg} {err} not found in {part}")
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
        exit()

    start_line, line_count, matched_lines = result
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

    exit()


def matching(
    content: str, match_options: _MatchOptions, isrecursion: bool
) -> Dict[str, List[Tuple[str, Dict[str, str]]]]:
    """
    Matches parts of source code.

    :param content: source code.
    :type content: str

    :param match_options: Options for each part in yaml file.
    :type match_options: _MatchOptions

    :param isrecursion: Boolean to find if the convert function is in recursion or not.
    :type isrecursion: bool

    :return: Return matched parts and tokens.
    :rtype: Dict[str, List[Tuple[str, Dict[str, str]]]]
    """
    partmatches = {}
    oncedone = matching.oncedone
    for part, options in match_options.items():
        # Unmatches
        pattern, tknames, global_chk, (untkn, unpart), defaults, once, err = options
        if not isrecursion:
            if not global_chk:
                continue  # For "global: False"
            if once:  # For parts match once
                if part in oncedone:
                    continue
                matching.oncedone.append(part)
        partmatch = []  # Part matching
        for match in pattern.finditer(content):
            matchstr: str = match.group()
            if unpart and any((bool(rgx.search(matchstr)) for rgx in unpart)):
                continue
            match = {  # Assigning default value for None
                tkname: (m if m is not None else defaults.get(tkname, ""))
                for tkname, m in zip(tknames, match.groups())
            }
            if err:  # If error definition exists
                for name, error in err.items():  # Static Code Analysis
                    err_match = error["regex"].search(matchstr)
                    if err_match:
                        report_syntax_error(
                            part,
                            error["msg"],
                            name,
                            err_match,
                            match,
                            content,
                            matchstr,
                        )
                        # Token names and matched tokens
            if untkn and any(
                (  # Checking unmatch on every token
                    bool(rgx.search(match))
                    for match, tkname in match.items()
                    for rgx in untkn.get(tkname, ())
                )
            ):
                continue
            partmatch.append((matchstr, match))
        if partmatch:
            partmatches.update({part: partmatch})
    return partmatches


matching.oncedone = []  # List of "once: True" parts that are already matched


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
                    error_message = error_details.get("msg", "")
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


def convert(
    yaml_details: _ParseYAMLDetails,
    content: str,
    isrecursion: bool = False,
    donly: Union[Tuple[str, ...]] = (),
):
    """
    This is the main function that converts new syntax to original syntax.

    :param content: Code with the new syntax.
    :param yaml_details: Details extracted from yaml files.
    :param isrecursion: A flag to check if there is a recursion call or not.
    :param donly: parts that should only be converted(used during part calling).
    :return: Return code with original syntax.
    """
    (match_options, trans_options, outside), tpattern = yaml_details
    lopcount = 0
    if isrecursion:
        match_options = {part: match_options[part] for part in donly}
    elif outside:  # Outside error checks
        find_outside_errors(outside, content)
    while 1:
        partsmatches = matching(content, match_options, isrecursion)
        if not partsmatches:  # Break when no match found
            break
        elif lopcount > 100:
            print(error_msg + " Loop Limit Exceded")
            print(
                "Bug Locations:\n",
                "\n".join(
                    (f"{part}:{matches}" for part, matches in partsmatches.items())
                ),
            )
            exit()
        lopcount += 1
        for part, partmatches in partsmatches.items():
            pattern = tpattern[part]
            tknopts, next_optns = trans_options[part]
            for partmatch, tknmatch in partmatches:
                temp_pattern = pattern
                for tkname, match in tknmatch.items():
                    if tkname not in tknopts:
                        continue
                    opts = tknopts[tkname]  # Token options
                    for opn in opts:
                        if opn == "replace":  # For replace option
                            replaces = opts["replace"]
                            from re import sub

                            for rgx, replace in replaces:  # data-match and replace
                                match = sub(rgx, replace, match)
                        elif opn == "call":
                            calls = opts["call"]
                            match = re_convert(content=match, donly=calls)
                        elif opn == "eachline":  # For oneachline option
                            line = opts["eachline"]
                            match = "\n".join(
                                [
                                    line.replace("<line>", l)
                                    for l in match.split("\n")
                                    if l.strip() != ""
                                ]
                            )
                    tknmatch[tkname] = match
                    # Replacing token names with its value
                temp_pattern = replace_variables(
                    tknmatch, replace_variables(tknmatch, temp_pattern)
                )
                # Token values added from other tokens
                if next_optns:  # Next Part option
                    temp_pattern = re_convert(content=temp_pattern, donly=next_optns)
                try:
                    content = content.replace(partmatch, temp_pattern)
                except Exception:
                    print(temp_pattern)
    return content


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
        exit()
    except FileNotFoundError:
        exit(f"{error_msg} {file} not found")


def grab(source: str, target: str) -> Tuple[_AfterProcessing, _ParseYAMLDetails]:
    """
    Gets details from source and target yaml files.

    :param argv: Array of arguments.
    :param l: Location of the argument needed.
    :return: The after command and yaml details.
    """
    spattern = load_yaml_file(source)
    tpattern = load_yaml_file(target)
    for part in spattern:  # Template checking
        if not (part in tpattern or part == "settings"):
            if part.startswith("_"):  # For parts with same pattern
                bpart = part[2:]  # Base part
                if bpart in spattern:  # Since template is same, tokens also same
                    spattern[part]["tokens"] = spattern[bpart]["tokens"]
                else:
                    exit(f"{error_msg} {bpart} for {part} not found")
                if bpart in tpattern:  # Template checking
                    tpattern[part] = tpattern[bpart]
                    continue
                part = bpart
            if not spattern[part]["tokens"]:
                tpattern[part] = ""
                continue
            exit(f"{error_msg} Template for {part} not found")
    after, rest = extract(spattern)
    return after, (rest, tpattern)


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
        exit(f"Error: Invalid YAML file: {file_path}\n")
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
        with open(f"{filename}.ltz", "rb") as litzFile:
            return load(litzFile)
    except FileNotFoundError as fnf_error:
        print(f"File {fnf_error.filename} not found.")
        exit()


def doc(file: str):
    """
    Prints documentation of the part in yaml file.
    CommandLine: python langtrans.py -d source.

    :param file: Address of the file.
    """
    yaml = load_yaml_file(file)
    if "settings" in yaml:
        settings = yaml["settings"]
        if "lang" in settings:
            print("Language:", settings["lang"])
        if "author" in settings:
            print("Author:", settings["author"])
        del yaml["settings"]
    docs = []
    p = t = 7
    for part in yaml:
        tkns = str(yaml[part]["tokens"])
        for i in "'[] ":
            tkns = tkns.replace(i, "")
        about = ""
        if "doc" in yaml[part]:
            about += yaml[part]["doc"]
        docs.append((part, tkns, about))
        if len(part) > p:
            p = len(part)
        if len(tkns) > t:
            t = len(tkns)
    print("Part", " " * (p - 5), "Tokens", " " * (t - 7), "About")
    for part, tkns, about in docs:
        print(
            part + " " * (p - len(part)),
            tkns + " " * (t - len(tkns)),
            about.replace("\n", "\n" + " " * (p + t + 2)),
        )


if __name__ == "__main__":
    if len(argv) == 1 or (len(argv) == 2 and argv[1] == "-h"):
        print("Arg usage: <SoureFileName> <OutputFileName> <SyntaxRepr> <PatternRepr>")
        exit("SyntaxRepr,PatternRepr: without extension(.yaml)")
    elif len(argv) < 3:
        exit(error_msg + " Insufficient number of arguments")
    try:
        # Terminal Options-------------------------------------------
        yes = "-y" in argv  # To run after command automatically
        verbose = "-v" in argv  # Verbose Mode - print source code
        no = "-n" in argv  # To exit without executing after command

        if verbose:
            argv.remove("-v")
        if yes:
            argv.remove("-y")
        if no:
            argv.remove("-n")
        # ------------------------------------------------------------
        if "-c" in argv:  # Compile into ltz
            from pickle import dump, HIGHEST_PROTOCOL
            from re import compile, error as re_error

            var_rgx = compile(r"<\w+>")
            argv[-1] += ".ltz"
            with open(argv[-1], "wb") as litzFile:
                dump(grab(argv[2], argv[3]), litzFile, protocol=HIGHEST_PROTOCOL)
            print(Fore.GREEN + "Compiled successfully")
            exit("File saved as " + argv[-1])
        elif "-f" in argv:  # Run compiled ltz
            argv.remove("-f")
            yaml_details = load_compiled_yaml_details(argv[-1])
        elif "-d" in argv:
            doc(argv[-1])
            exit()
        else:
            from re import compile, error as re_error

            var_rgx = compile(r"<\w+>")
            yaml_details = grab(argv[3], argv[4])
        # -------------------------------------------------------------------
        after, yaml_details = yaml_details
        with open(argv[1]) as InputFile:
            content = InputFile.read()
        re_convert = partial(convert, yaml_details=yaml_details, isrecursion=True)
        targetcode = convert(yaml_details, content)
        with open(argv[2], "w") as OutputFile:
            OutputFile.write(targetcode)
        print(Fore.GREEN, "Saved as", argv[2])
        if verbose:
            print(targetcode)
        # For after command in settings
        if not no and after:  # Not None
            if isinstance(after, Dict):  # After command for different OS
                from platform import system as systm

                osname = systm().lower()  # Current os name
                if osname not in after:
                    print(
                        f"{error_msg} No after command for {osname}. OS name eg. linux, windows"
                    )
                    exit()
                after = after[osname]
            if isinstance(after, list):  # For multiple commands
                after = " && ".join(after)
            # To use address of source and target file in 'after' command
            after_var = (
                ("$target", argv[2]),
                ("$source", argv[1]),
                ("$current", dirname(__file__)),
            )
            for var, val in after_var:
                after = after.replace(var, val)
            if yes:
                system(after)
                exit()
            print("\nEnter to run and n to exit\nCommand:", after)
            inp = input()
            if inp.lower() != "n":
                system(after)
    except Exception as err:
        print(Fore.RED + "Program Error:", err)
