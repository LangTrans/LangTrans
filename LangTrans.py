from yaml import load, SafeLoader
from re import compile as comp, MULTILINE, sub
from pickle import dump, load as cload, HIGHEST_PROTOCOL

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
    This function extract eachline and replace option from yaml
    
    :param sdef: Contains token options
    :type spattern: dic
    :param collections: Dictionary of collections and its names
    :return: [eachline_option,replace_option]
    :rtype: list
    """
    options = dict()
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
            options[tkname] = opns

    return options, check_collections(
        sdef["next"] if "next" in sdef else [], collections
    )


def addvar(variables, rv):
    for varname, value in reversed(variables.items()):
        rv = rv.replace(f"<{varname}>", value)
    return rv


def extract(spattern):
    """
    This function extract contents needed from yaml file with regex
    
    :param spattern: Dictionary with yaml file details
    :type spattern: dic
    :return: option(replace,eachline),regex,token_names
    :rtype: dic,dic,list
    """
    # Settings---------------------------------------------------
    collections = dict()
    if "settings" in spattern:
        setting = spattern["settings"]
        del spattern["settings"]
        if "variables" in setting:  # Replacing variable name with its value
            variables = setting["variables"]
            for part, sdef in spattern.items():
                spattern[part]["regex"] = addvar(variables, sdef["regex"])
                for tkn in sdef["tokens"]:
                    if tkn in sdef and "replace" in sdef[tkn]:
                        for p, replaces in enumerate(sdef[tkn]["replace"]):
                            spattern[part][tkn]["replace"][p][0] = addvar(
                                variables, replaces[0]
                            )

        if "collections" in setting:
            collections = setting["collections"]
    # ------------------------------------------------------------
    options = dict()
    regexs = dict()
    global_chk = []
    tknames = []
    for part, sdef in spattern.items():
        tkns = spattern[part[2:]]["tokens"] if part[0] == "_" else sdef["tokens"]
        regexs.update({part: comp(sdef["regex"], MULTILINE)})
        options.update({part: tknoptions(sdef, collections)})
        tknames.append(tuple(tkns))
        if "global" not in sdef or sdef["global"]:
            global_chk.append(part)
    return (options, regexs, tuple(tknames), tuple(global_chk))


def main(yaml_details, content, donly_check=False, donly=[]):
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
    (options, regexs, tokens, global_chk), tpattern = yaml_details
    lopcount = 0
    while 1:
        # matching tokens from code with regular expressions
        # --------------------------------------------------------------
        tknmatches = dict()
        partmatches = dict()
        empty = True
        for (part, pattern), tknames in zip(regexs.items(), tokens):
            if donly_check:  # For recursion
                if part not in donly:
                    continue
            elif part not in global_chk:
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
        if empty:
            break
        elif lopcount == 10**2:
            content += (
                "\n\nError:\tLoop Limit Exceded!\n\t"
                + f"Bug Locations: {list(part for part,matches in partmatches.items() if matches)}"
            )
            break
        lopcount += 1
        # ---------------------------------------------------------------
        for part, tknmatchez in tknmatches.items():  # Replacing parts in source code
            if part[0] != "_":  # Find two regex extract with one pattern
                pattern = tpattern[part]
            else:
                pattern = tpattern[part[2:]]
            tknopts, next_optns = options[part]
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
                            match = main(
                                yaml_details,
                                match,
                                donly_check=True,
                                donly=data,  # call list
                            )
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
                    temp_pattern = main(
                        yaml_details,
                        temp_pattern,
                        donly_check=True,
                        donly=next_optns,  # call list
                    )
                content = content.replace(partmatch, temp_pattern)
    return content


def grab(argv, l):
    spattern = load(open(argv[l] + ".yaml").read(), Loader=SafeLoader) # Source
    tpattern = load(open(argv[l + 1] + ".yaml").read(), Loader=SafeLoader) # Target
    return extract(spattern), tpattern


def save(argv, l):
    argv[-1] += ".ltz"
    yaml_details = grab(argv, l)
    dump(yaml_details, open(argv[-1], "wb"), protocol=HIGHEST_PROTOCOL)
    print("File saved as", argv[-1])
    return yaml_details


def doc(file):  # Printing Documentation # CommandLine: python langtrans.py -d source 
    yaml = load(open(file + ".yaml").read(), Loader=SafeLoader)
    if "settings" in yaml:
        settings = yaml["settings"]
        if "lang" in settings:
            print("Language:", settings["lang"])
        if "author" in settings:
            print("Author:", settings["author"])
        del yaml["settings"]
    docs = []
    p = t = e = 7
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
        if len(about) > e:
            e = len(about)
    print("Part", " " * (p - 5), "Tokens", " " * (t - 7), "About", " " * (e - 6))
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
            try:
                yaml_details = cload(open(argv[-1] + ".ltz", "rb"))
            except Exception:
                yaml_details = save(argv, 3)
        elif "-d" in argv:
            doc(argv[-1])
            exit()
        else:
            yaml_details = grab(argv, 3)
        content = open(argv[1]).read()
        targetcode = main(yaml_details, content)
        open(argv[2], "w").write(targetcode)
        print(targetcode)
    except Exception as err:
        print("Error:", err)
