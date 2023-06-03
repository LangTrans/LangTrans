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
from sys import argv, exit
from functools import partial
from typing import (
    Any,
    Match,
    Pattern,
    TypedDict,
    Union,
    Optional,
    List,
    Tuple,
    Dict,
    Callable,
)
from colorama import init, Fore

# Types------------------------------
Pattern = Pattern[str]  # Compiled Regex
Match = Match[str]  # Matched String
err_details = TypedDict("err_details", regex=Pattern, msg=str)
err_dict = dict[str, err_details]
_unmatches = dict[str, tuple[Pattern, ...]]
_match_options = dict[
    str,
    tuple[
        Pattern,  # regex
        tuple[str, ...],  # tokens
        bool,  # Global
        tuple[_unmatches, tuple[Pattern, ...]],  # untkn  # unpart
        dict[str, str],  # defaults
        bool,  # once
        Optional[err_dict],  # err
    ],
]
_outside = Optional[dict[str, err_dict]]
_tpattern = Optional[dict[str, str]]
_next_optns = Optional[Union[tuple[str, ...]]]
_opts = TypedDict(
    "_opts",
    replace=tuple[tuple[Union[Pattern, str], str], ...],
    call=tuple[str, ...],
    eachline=str,
)
_tknopts = dict[str, _opts]
_opns = tuple[_tknopts, _next_optns]
_trans_options = dict[str, _opns]
_yaml_details = tuple[tuple[_match_options, _trans_options, _outside], _tpattern]
_collections = Optional[dict[str, Optional[list[str]]]]
_after = Optional[Union[list[str], str, dict[str, str]]]
_any = dict[str, dict[str, Any]]
_var = dict[str, str]
_HandlerType = Callable[[Any, str, _collections, _var], Any]

# -----------------------------------
#  For colored error - Intialiazing colorama
init(autoreset=True)
error_msg = Fore.RED + "Error:"


def comp(regex: str) -> Pattern:
    """
    Compiles regular expression to emulate tokens(in parsers)

    :param regex: Regular expression.
    :return: Compiled regular expression.
    """

    regex = regex.replace(" ", r"\s+").replace("~", r"\s*")

    try:  # re.MULTILINE=8
        return compile(regex, 8)
    except rerror as err:
        print(error_msg, "Invalid regex")
        print(err.msg)
        print("Regex:", regex.replace("\n", r"\n").replace("\t", r"\t"))
        print(" " * (err.pos + 7) + "^")
        raise err


def check_collections(calls: list[str], collections: _collections) -> tuple[str, ...]:
    """
    This function adds collections to the call list.

    :param calls: List with collection names and part names.
    :param collections: Dictionary of collections and its names.
    :return: Collection replaced call list.
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
            except KeyError as exc:
                raise KeyError(
                    f"Error: Collection ${collection_name} not found"
                ) from exc
        else:
            new_collections.append(collection)

    return tuple(new_collections)


def handle_eachline(option_data: Any) -> Any:
    return option_data


def handle_replace(option_data: list, token_name: str) -> tuple:
    try:
        return tuple(
            (comp(replace_option[0]), replace_option[1])
            if len(replace_option) == 2
            else (comp(replace_option[0]), "")
            for replace_option in option_data
        )
    except Exception as replace_error:
        print(f"Location: Replace option for token({token_name})")
        raise replace_error


def handle_call(option_data: list, collections: _collections) -> tuple:
    return check_collections(option_data, collections)


def handle_unmatch(
    option_data: Union[list, str], token_name: str, variables: _var
) -> tuple:
    if not isinstance(option_data, list):
        option_data = [option_data]
    try:
        return tuple([comp(addvar(variables, regex)) for regex in option_data])
    except Exception as unmatch_error:
        print(f"Location: Unmatch for token({token_name})")
        raise unmatch_error


def handle_default(option_data: Any) -> Any:
    return option_data


OPTION_HANDLERS = {
    "eachline": handle_eachline,
    "replace": handle_replace,
    "call": handle_call,
    "unmatch": handle_unmatch,
    "default": handle_default,
}


def extract_token_options(
    specification: dict[str, Any], collections: _collections, variables: _var
) -> Dict[str, Any]:
    token_names = specification["tokens"]
    token_options: Dict[str, Dict[str, Any]] = {}

    for token_name, options in specification.items():
        if isinstance(options, dict):
            current_token_options: Dict[str, Any] = {}
            for option_name, option_data in options.items():
                handler = OPTION_HANDLERS.get(option_name)
                if handler:
                    current_token_options[option_name] = handler(
                        option_data, token_name, collections, variables
                    )  # type: ignore
            token_options[token_name] = current_token_options

        if "," in token_name:
            for split_token_name in token_name.split(","):
                if split_token_name not in token_names:
                    raise ValueError(f"Error: {split_token_name} not found in tokens")
                token_options[split_token_name] = token_options[token_name]

        if token_name not in token_names:
            raise ValueError(f"{error_msg} {token_name} not found in tokens")
    return token_options


def process_token_definitions(
    specification: dict[str, Any], collections: _collections, variables: _var
) -> Tuple[
    Dict[str, Any], Dict[str, str], Tuple[Dict[str, Any], Optional[Tuple[str, ...]]]
]:
    """
    This function extracts token options from a yaml file.

    :param specification: Contains token options.
    :param collections: Dictionary of collections and their names.
    :return: unmatches, default values, translation options, and next call list.
    """
    token_options = extract_token_options(specification, collections, variables)

    return (
        token_options.get("unmatch", {}),
        token_options.get("default", {}),
        (
            token_options,
            check_collections(specification.get("next", []), collections),
        ),
    )


def addvar(variables: _var, rv: str):
    """
    This function replaces <varname> with its value.

    :param variables: Global variables.
    :param rv: String containing <varname>.
    :return: variable replaced string.
    """
    for varname, value in reversed(variables.items()):
        rv = rv.replace(f"<{varname}>", value)
    return rv


def compile_rgx(errors: _any, var: _var):
    for name, error in errors.items():
        if name == "outside":
            errors = compile_rgx(error, var)
            continue
        error["regex"] = comp(addvar(var, error["regex"]))
    return errors


def comp_err(name: str, variables: _var) -> tuple[dict[str, err_dict], _outside]:
    """
    Compiles regexes in an error file.

    :param name: Name of errfile.
    :param variables: Global variables.
    :return: compiled error inside and outside part.
    """
    errors_def = load_yaml(name)
    outside = {}
    for part, errors in errors_def.items():
        errors = compile_rgx(errors, variables)
        if "outside" in errors:
            outside[part] = errors.pop("outside")
    if "outside" in errors_def:  # Outside not related to part
        outside[""] = errors_def.pop("outside")
    return errors_def, outside


def extract(
    spattern: _any,
) -> tuple[_after, tuple[_match_options, _trans_options, _outside]]:
    """
    This function extracts contents needed from yaml file with regex.

    :param spattern: Dictionary with yaml file details.
    :return: after command and (match options, token options).
    """
    # Importing builtin variables
    variables = grab_var(dirname(__file__) + "\\builtin")
    # Settings-------------------------------------------------------
    after = errfile = outside = collections = None
    if "settings" in spattern:
        setting = spattern.pop("settings")
        after = setting.get("after")
        if "varfile" in setting:  # Importing variables from varfile
            variables.update(grab_var(setting["varfile"]))
        if "variables" in setting:  # Adding variables in settings
            variables.update(setting["variables"])
        if "errfile" in setting:
            errfile, outside = comp_err(setting["errfile"], variables)
        collections = setting.get("collections")
    # ----------------------------------------------------------------
    trans_options: _trans_options = {}
    match_options: _match_options = {}
    try:
        for part, specification in spattern.items():
            for opt in specification.values():
                if isinstance(opt, dict) and "replace" in opt:
                    for replace in opt[
                        "replace"
                    ]:  # Replacing variables in replace option
                        replace[0] = addvar(variables, replace[0])
            regex = comp(
                addvar(variables, specification["regex"])
            )  # Compiled regex without variables
            tokens = tuple(specification["tokens"])  # Token_names
            if regex.groups != len(tokens):
                if regex.groups == 0 and len(tokens) < 2:
                    regex = comp(f"({regex.pattern})")
                else:
                    print("Part:", part)
                    print("Token Names:", len(tokens), "Capture Groups:", regex.groups)
                    exit(
                        error_msg
                        + " Number of token names is not equal to number of capture groups"
                    )
            unmatches, defaults, tknopns = process_token_definitions(
                specification, collections, variables
            )
            if m := var_rgx.search(regex.pattern):
                print(Fore.YELLOW + "Warning:", m.group(), "not found")
            match_options[part] = (
                regex,
                tokens,
                "global" not in specification
                or specification["global"],  # Checking Global
                (  # Unmatch regexs for tokens
                    unmatches,
                    (  # Unmatch regexs for part
                        tuple(
                            [
                                comp(addvar(variables, unmatch))
                                for unmatch in specification["unmatch"]
                            ]
                        )
                        if "unmatch" in specification
                        else ()
                    ),
                ),
                defaults,
                "once" in specification and specification["once"],
                (errfile[part] if errfile and part in errfile else None),
            )
            trans_options[part] = tknopns

    except (rerror, TypeError):  # Regex and unknown token option error
        exit(f"Part:{part}")
    except KeyError as err:  # For part without regex or tokens
        exit(f"{error_msg} {err} not found in {part}")
    return after, (match_options, trans_options, (outside if errfile else None))


def err_report(
    part: str,
    msg: str,
    name: str,
    match: Match,
    tkns: dict,
    content: str,
    matchstr: str,
):
    """Shows error messages for syntax errors."""
    pos, l, indexed = getotalines(content.splitlines(), matchstr)
    err_part = match.group()
    if part:  # Part Name
        print(f"[{Fore.MAGENTA + part + Fore.RESET}]")
    line = indexed[0].lstrip()
    lineno = str(pos + 1) + " |"
    # error Line
    print(Fore.CYAN + lineno, line.replace(err_part, Fore.RED + err_part + Fore.RESET))
    total_msg = addvar(  # Replacing variables in main and err match
        {"$" + str(l): tkn for l, tkn in enumerate(match.groups(), start=1)},  # Err
        addvar(tkns, msg),  # Main
    )
    # Error Name
    print(" " * (line.index(err_part) + len(lineno)), Fore.RED + name.replace("_", " "))
    print(Fore.YELLOW + total_msg)  # Error Info
    exit()


def matching(
    content: str, match_options: _match_options, isrecursion: bool
) -> dict[str, list[tuple[str, dict[str, str]]]]:
    """
    Matches parts of source code.

    :param content: source code.
    :param match_options: Options for each part in yaml file.
    :param isrecursion: Boolean to find if the convert function is in recursion or not.
    :return: Return matched parts and tokens.
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
                        err_report(
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


def outside_err(outside: _outside, content: str):
    """Finds syntax errors in the source code and shows error messages."""
    for part, errors in outside.items():
        for name, error in errors.items():
            err_match = error["regex"].search(content)
            if err_match:
                err_report(
                    part,
                    error.get("msg", ""),
                    name,
                    err_match,
                    {},
                    content,
                    err_match.group(),
                )


def convert(
    yaml_details: _yaml_details,
    content: str,
    isrecursion: bool = False,
    donly: Union[tuple[str, ...]] = (),
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
        outside_err(outside, content)
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
                temp_pattern = addvar(tknmatch, addvar(tknmatch, temp_pattern))
                # Token values added from other tokens
                if next_optns:  # Next Part option
                    temp_pattern = re_convert(content=temp_pattern, donly=next_optns)
                try:
                    content = content.replace(partmatch, temp_pattern)
                except Exception:
                    print(temp_pattern)
    return content


def getotalines(lines: list[str], substring: str):
    """
    Finds line in which the substring is located.

    :param lines: List with lines of code being checked for substring.
    :param substring: Substring to be found in lines.
    :return: Lines where the substring is located or nothing if no match is found.
    """
    sublines = substring.splitlines()
    sublen = len(sublines)
    for pos, line in enumerate(lines):
        if sublines[0] in line:  # If first line matched
            if pos >= (len(lines) - sublen):  # If reached end of string
                return
            indexed = lines[pos : pos + sublen]  # rest of line
            for linepart, subline in zip(indexed, sublines[1:]):  # Check rest of line
                if subline not in linepart:  # Break if subline not matched
                    break
            else:  # Break if sublines are matched
                break
    else:  # Return if sublines are not matched in lines
        return  # No match Found
    return pos, sublen, indexed  # dict(zip(sublines,indexed))


def load_yaml(file: str) -> dict[str, Any]:
    """
    Loads yaml files.

    :param file: The base filename.
    :return: Yaml Details.
    """
    from yaml import load, SafeLoader
    from yaml.scanner import ScannerError
    from yaml.parser import ParserError

    file += ".yaml"
    try:
        with open(file) as yamlFile:
            return load(yamlFile.read(), Loader=SafeLoader)
    except (ScannerError, ParserError) as err:  # Error message for Invalid Yaml File
        print(error_msg, file, "is invalid")
        print(err.problem, err.context)
        print(err.problem_mark.get_snippet())
        exit()
    except FileNotFoundError:
        exit(f"{error_msg} {file} not found")


def grab(source: str, target: str) -> tuple[_after, _yaml_details]:
    """
    Gets details from source and target yaml files.

    :param argv: Array of arguments.
    :param l: Location of the argument needed.
    :return: The after command and yaml details.
    """
    spattern = load_yaml(source)
    tpattern = load_yaml(target)
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


def grab_var(file: str) -> _var:
    """
    Loads variables from an external file.

    :param file: Address of the external file.
    :return: Dictionary of variables.
    """
    variables = {}
    try:
        v = load_yaml(file)
        if v is not None:
            variables.update(v)
    except ValueError:
        exit(f"{error_msg} Invalid varfile({file}.yaml)\n")
    return variables


def get_ltz(filename: str) -> tuple[_after, _yaml_details]:
    """
    Loads compiled yaml_details from .ltz file.

    :param filename: Name of the file.
    :return: yaml_details from .ltz file.
    """
    from pickle import load

    try:
        with open(filename + ".ltz", "rb") as litzFile:
            return load(litzFile)
    except FileNotFoundError as err:
        exit(f"{error_msg} {err.filename} not found")


def doc(file: str):
    """
    Prints documentation of the part in yaml file.
    CommandLine: python langtrans.py -d source.

    :param file: Address of the file.
    """
    yaml = load_yaml(file)
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
            from re import compile, error as rerror

            var_rgx = compile(r"<\w+>")
            argv[-1] += ".ltz"
            with open(argv[-1], "wb") as litzFile:
                dump(grab(argv[2], argv[3]), litzFile, protocol=HIGHEST_PROTOCOL)
            print(Fore.GREEN + "Compiled successfully")
            exit("File saved as " + argv[-1])
        elif "-f" in argv:  # Run compiled ltz
            argv.remove("-f")
            yaml_details = get_ltz(argv[-1])
        elif "-d" in argv:
            doc(argv[-1])
            exit()
        else:
            from re import compile, error as rerror

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
            if isinstance(after, dict):  # After command for different OS
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
