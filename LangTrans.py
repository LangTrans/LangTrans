from re import compile as comp, MULTILINE, sub
from functools import partial
"""
LangTrans
---------
To customize syntax of any programming language.
"""

def check_collections(calls, collections):
    """
    This add collections into call list

    :param calls: List with collection names and part names
    :type calls: list
    :param collections: Dictionary of collections and its names
    :type collections: dic
    :return: Collection replaced call list
    """
    if not collections:  # len(collection)==0
        return calls
    narr = []
    for collection in calls:
        if collection.startswith("$"):
            narr += collections[collection[1:]]
        else:
            narr.append(collection)
    return narr

def tknoptions(sdef, collections):
    """
    This function extract token options from yaml file

    :param sdef: Contains token options
    :type spattern: dic
    :param collections: Dictionary of collections and its names
    :return: translation options and next call list
    :rtype: dic,list
    """
    trans_options = dict()
    nsdef = dict()
    for tkns, opts in sdef.items():  # Spliting Token options
        if "," in tkns:
            for tkn in tkns.split(","):
                nsdef[tkn] = opts
        else:
            nsdef[tkns] = opts
    sdef = nsdef
    del nsdef
    for tkname in sdef["tokens"]:
        if tkname in sdef:
            opns = dict()
            # Token options
            for opn, data in sdef[tkname].items():
                if opn == "eachline":
                    opns.update({"eachline": data})
                elif opn == "replace":
                    opns.update(
                        {
                            "replace": [
                                (comp(repregex[0]), repregex[1])
                                if 1 < len(repregex)
                                else (comp(repregex[0]), "")
                                for repregex in data
                            ]
                        }
                    )
                elif opn == "call":
                    opns.update({"call": check_collections(data, collections)})
            trans_options[tkname] = opns
    return trans_options, (check_collections(sdef["next"], collections) if "next" in sdef else [])

def addvar(variables, rv):
    """
    To Replace <varname> with its value
    :param variable: Dictionary of variables
    :param rv: String containing <varname>
    :type variable: dict
    :type rv: str
    :return: variable replaced string
    :rtype: str
    """
    for varname, value in reversed(variables.items()):
        rv = rv.replace(f"<{varname}>", value)
    return rv

def extract(spattern):
    """
    This function extract contents needed from yaml file with regex

    :param spattern: Dictionary with yaml file details
    :type spattern: dic
    :return: after command and (match options, token options)
    :rtype: (None|str|list|dic),tuple(dic,dic)
    """
    # Settings---------------------------------------------------
    for part in spattern:  # For two regex extract with one pattern
        if part[0] == "_":
            spattern[part]["tokens"] = spattern[part[2:]]["tokens"]
    after = None
    if "settings" in spattern:
        setting = spattern["settings"]
        del spattern["settings"]
        after = setting.get("after")
        from os.path import dirname
        # Importing builtin variables
        variables = grab_var(dirname(__file__) + "\\builtin")
        if "varfile" in setting: # Importing variables from varfile
            variables.update(grab_var(setting["varfile"]))
        if "variables" in setting: # Adding variables in settings
            variables.update(setting["variables"])
        if variables: # Replacing variable name with its value
            for part, sdef in spattern.items():  # For regex in part
                spattern[part]["regex"] = addvar(variables, sdef["regex"])
                for tkn in sdef["tokens"]: # For replace option in token options
                    if tkn in sdef and "replace" in sdef[tkn]:
                        for p, replaces in enumerate(sdef[tkn]["replace"]):
                            spattern[part][tkn]["replace"][p][0] = addvar(variables, replaces[0])
        del variables
        collections = setting["collections"] if "collections" in setting else dict()
    # ------------------------------------------------------------
    trans_options = dict()
    match_options = dict()
    for part, sdef in spattern.items():
        match_options.update(
            {
                part: (
                    comp(sdef["regex"], MULTILINE), # Compiled regex
                    sdef["tokens"], # Token_names
                    ("global" not in sdef or sdef["global"]), # Checking Global
                )
            }
        )
        trans_options.update({part: tknoptions(sdef, collections)})
    return after, (match_options, trans_options)

def matching(content, match_options, isrecursion):
    """
    To match parts of source code
    :param match_options: Options for each part in yaml file
    :param isrecursion: Boolean to find main function is in recursion or not
    :type match_options: dict
    :type isrecursion: bool
    :return: Return matched parts and tokens
    :rtype: bool,dict,dict
    """
    tknmatches = dict()
    partmatches = dict()
    empty = True
    for part, (pattern, tknames, global_chk) in match_options.items():
        if not (isrecursion or global_chk): # (not isrecursion) and (not global_chk)
            continue
        # Part matching
        partmatches[part] = [i.group() for i in pattern.finditer(content)]
        if empty:
            if not partmatches[part]:  # len(partmatches[part]) == 0
                continue
            empty = False
        # Token matching
        if len(tknames) == 1:
            tknmatches[part] = [
                {tkname: matches}
                for matched in partmatches[part]
                for matches, tkname in zip(pattern.findall(matched), tknames)
            ]
        else:
	        tknmatches[part] = [
	            {tkname: match for match, tkname in zip(matches, tknames)}
	            for matched in partmatches[part]
	            for matches in pattern.findall(matched)
	        ]
    return empty, partmatches, tknmatches

def main(yaml_details, content, isrecursion=False, donly=[]):
    """
    This is main function convert new syntax to orginal syntax

    :param content: Code with new syntax
    :param spattern: Dictionary containing regular expression for new syntax
    :param tpattern: Dictionary containing pattern of original syntax
    :type content: str
    :type spattern: dic
    :type tpattern: dic
    :return: Return code with original syntax
    :rtype: str
    """
    (match_options, trans_options), tpattern = yaml_details
    lopcount = 0
    while 1:
        if isrecursion:
        	match_options = {part:match_options[part] for part in donly}
        empty, partmatches, tknmatches = matching(content, match_options, isrecursion)
        if empty:  # Break when no match found
            break
        elif lopcount > 100:
            content += (
                "\n\nError:\tLoop Limit Exceded!\n\t"
                + f"Bug Locations: {list(part for part,matches in partmatches.items() if matches)}"
            )
            break
        lopcount += 1
        # ---------------------------------------------------------------
        for part, tknmatchez in tknmatches.items():  # Translation
            # For two regex extract with one pattern
            pattern = tpattern[part[2:]] if part[0] == "_" else tpattern[part]
            tknopts, next_optns = trans_options[part]
            for tknmatch, partmatch in zip(tknmatchez, partmatches[part]):
                temp_pattern = pattern
                for tkname, match in tknmatch.items():
                    if tkname not in tknopts:
                        continue
                    for opn, data in tknopts[tkname].items():
                        # Token optionss
	                    if opn == "replace":
	                        # For replace option
	                        for rgx in data:  # List of replace
	                            match = sub(*rgx, match)
	                    elif opn == "call":
	                    	match = re_main(content=match, donly=data)  # call list
	                    elif opn == "eachline":  # For oneachline option
	                        match = "\n".join(
	                            [
	                                data.replace("<line>", l)
	                                for l in match.split("\n")
	                                if l.strip() != ""
	                            ]
	                        )
                    tknmatch[tkname] = match
                    # Replacing token names with its value
                temp_pattern = addvar(tknmatch, addvar(tknmatch, temp_pattern))
                # Token values added from other tokens
                if next_optns:  # Next Part option
                    temp_pattern = re_main(content=temp_pattern, donly=next_optns)
                content = content.replace(partmatch, temp_pattern)
    return content

def grab(argv, l):
    """
    To get details from yaml files
    :param argv: array of arguments
    :param l: location of argument need
    :type argv: list
    :type l: int
    :return: after command and yaml details
    :rtype:  (str or list or dic or None), tuple(dic,dic)
    """
    from yaml import load, SafeLoader

    spattern = load(open(argv[l] + ".yaml").read(), Loader=SafeLoader)  # Source
    tpattern = load(open(argv[l + 1] + ".yaml").read(), Loader=SafeLoader)  # Target
    after, rest = extract(spattern)
    return after, (rest, tpattern)

def grab_var(file):
    """
    To variables from external file
    :param file: Address of external file
    :type file: str
    :return: Dictionary of variables
    :rtype: dic
    """
    from yaml import load, SafeLoader

    variables = dict()
    try:
        v = load(open(file + ".yaml").read(), Loader=SafeLoader)
        if v != None:
            variables.update(v)
    except FileNotFoundError:
        print(f"varfile({file}.yaml) not found\n")
    except ValueError:
        print(f"Invalid varfile({file}.yaml)\n")
    return variables

def save(argv, l):
    """
    To save yaml details into single file
    :param argv: array of arguments
    :param l: location of argument need
    :type argv: list
    :type l: int
    :return: yaml details
    :rtype: tuple
    """
    from pickle import dump, HIGHEST_PROTOCOL
    argv[-1] += ".ltz"
    yaml_details = grab(argv, l)
    dump(yaml_details, open(argv[-1], "wb"), protocol=HIGHEST_PROTOCOL)
    print("File saved as", argv[-1])
    return yaml_details

def doc(file):
    """
    To print documentation of part in yaml file
    CommandLine: python langtrans.py -d source
    :param file: Addres of file
    :type file: str
    """
    from yaml import load, SafeLoader
    yaml = load(open(file + ".yaml").read(), Loader=SafeLoader)
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
        print(part + " " * (p - len(part)), tkns + " " * (t - len(tkns)), about)

if __name__ == "__main__":
    from sys import argv, exit

    if len(argv) == 1 or (len(argv) == 2 and argv[1] == "-h"):
        print("Arg usage: <SoureFileName> <OutputFileName> <SyntaxRepr> <PatternRepr>")
        print("SyntaxRepr,PatternRepr: without extension(.yaml) ")
        exit()
    elif len(argv) < 3:
        print("Error: Insufficient number of arguments")
        exit()
    try:
	    if "-c" in argv:  # Combine into ltz
	        save(argv, 2)
	        exit()
	    if "-f" in argv:  # Use ltz
	        argv.remove("-f")
	        from pickle import load
	        try:
	            yaml_details = load(open(argv[-1] + ".ltz", "rb"))
	        except Exception:
	            yaml_details = save(argv, 3)
	    elif "-d" in argv:
	        doc(argv[-1])
	        exit()
	    else:
	        yaml_details = grab(argv, 3)
	    yes = "-y" in argv  # To run after command automatically
	    if yes:
	        argv.remove("-y")
	    after, yaml_details = yaml_details
	    content = open(argv[1]).read()
	    re_main = partial(main, yaml_details=yaml_details, isrecursion=True)
	    targetcode = main(yaml_details, content)
	    open(argv[2], "w").write(targetcode)
	    print(targetcode)
	    # For after command in settings
	    if after:  # Not None
	        from os import system
	        if isinstance(after, list):  # For multiple commands
	            after = " && ".join(after)
	        elif isinstance(after, dict):  # After command for different OS
	            from platform import system
	            osname = system().lower()  # Current os name
	            if osname not in after:
	                print(f"No after command for {osname}. OS name eg. linux, windows")
	                exit()
	            after = after[osname]
	        if not isinstance(after, str):
	            print("Invalid after command")
	            exit()
	        # To use address of source and target file in 'after' command
	        for var, val in zip(["$target", "$source"], [argv[2], argv[1]]):
	            after = after.replace(var, val)
	        if yes:
	            system(after)
	            exit()
	        inp = input(f"\nEnter to run and n to exit\nCommand:{after}\n")
	        if inp.lower() != "n":
	            system(after)
    except Exception as err:
        print("Error:", err)
