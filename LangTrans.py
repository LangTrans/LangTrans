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
    if len(collections) == 0:
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
    oneachline = dict()
    replase = dict()
    call = dict()
    nsdef=dict()
    for tkns,opts in sdef.items():#Spliting Token options
        if "," in tkns:
            for tkn in tkns.split(","):
                nsdef[tkn]=opts
        else:
            nsdef[tkns]=opts
    sdef=nsdef;del nsdef
    for tkname in sdef["tokens"]:
        if tkname in sdef:
            tknopt = sdef[tkname]  # Token options
            if "eachline" in tknopt:
                oneachline.update({tkname: tknopt["eachline"]})
            if "replace" in tknopt:
                replase.update(
                    {
                        tkname: [
                            (comp(repregex[0]), repregex[1])
                            if 1 < len(repregex)
                            else (comp(repregex[0]), "")
                            for repregex in tknopt["replace"]
                        ]
                    }
                )
            if "call" in tknopt:
                call.update({tkname: check_collections(tknopt["call"], collections)})
    return (call, oneachline, replase)


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
    loop = False
    loplimit = 7
    if "settings" in spattern:
        setting = spattern["settings"]
        del spattern["settings"]
        if "loop" in setting:
            loop = setting["loop"]
        if "looplimit" in setting:
            loplimit = setting["looplimit"]
        if "variables" in setting:  # Replacing variable name with its value
            for part, sdef in spattern.items():
                if part != "settings":
                    rv = sdef["regex"]  # regex with var
                    for varname, rgx in reversed(setting["variables"].items()):
                        if "<" + varname + ">" in rv:  # regex without var
                            rv = rv.replace("<" + varname + ">", rgx)
                    spattern[part]["regex"] = rv
        if "collections" in setting:
            collections = setting["collections"]
    # ------------------------------------------------------------
    options = dict()
    regexs = dict()
    global_chk = []
    tknames = []
    for part, sdef in spattern.items():
        if part[0] == "_":
            sdef["tokens"] = spattern[part[2:]]["tokens"]
        regexs.update({part: comp(sdef["regex"], MULTILINE)})
        options.update({part: tknoptions(sdef, collections)})
        tknames.append(tuple(sdef["tokens"]))
        if "global" not in sdef or sdef["global"]:
            global_chk.append(part)
    return (options, regexs, tuple(tknames), tuple(global_chk), loop, loplimit)


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
    (options, regexs, tokens, global_chk, loop, loplimit), tpattern = yaml_details
    lopcount = 0
    while 1:
        # matching tokens from code with regular expressions
        # --------------------------------------------------------------
        tknmatches = dict()
        partmatches = dict()
        for (part, pattern), tknames in zip(regexs.items(), tokens):
            if donly_check:  # For recursion
                if part not in donly:
                    continue
            elif part not in global_chk:
                continue
            # Part matching
            partmatches[part] = [i.group() for i in pattern.finditer(content)]
            # Token matching
            if len(tknames) == 1:
                tknmatches[part] = [
                    {tkname: matches}
                    for matched in partmatches[part]
                    for matches, tkname in zip(pattern.findall(matched), tknames)
                ]
                continue
            tknmatches[part] = [
                {tkname: match for match, tkname in zip(matches, tknames)}
                for matched in partmatches[part]
                for matches in pattern.findall(matched)
            ]
        # ---------------------------------------------------------------
        for part in tknmatches:  # Replacing parts in source code
            if part[0] != "_":  # Find two regex extract with one pattern
                pattern = tpattern[part]
            else:
                pattern = tpattern[part[2:]]
            calls, oneachline, replacer = options[part]
            for tknmatch, partmatch in zip(tknmatches[part], partmatches[part]):
                temp_pattern = pattern
                for tkname, match in tknmatch.items():
                    if tkname in oneachline:  # For oneachline option
                        line = oneachline[tkname]
                        match = "\n".join(
                            [
                                line.replace("<line>", l)
                                for l in match.split("\n")
                                if l.strip() != ""
                            ]
                        )
                    if tkname in replacer:  # For replace option
                        for rgx in replacer[tkname]:
                            match = sub(*rgx, match)
                    # Token options
                    if tkname in calls:  # For part calls
                        match = main(
                            yaml_details,
                            match,
                            donly_check=True,
                            donly=calls[tkname],
                        )
                    # Replacing pattern tokens expression with tokens
                    temp_pattern = temp_pattern.replace(f"<{tkname}>", match)
                content = content.replace(partmatch, temp_pattern)
        lopcount += 1
        if not loop or lopcount == loplimit:
            break
    return content


def grab(argv, l):
    spattern = load(open(argv[l] + ".yaml").read(), Loader=SafeLoader)  # Source
    tpattern = load(open(argv[l + 1] + ".yaml").read(), Loader=SafeLoader)  # Target
    return extract(spattern), tpattern


def save(argv, l):
    argv[-1] += ".ltz"
    yaml_details = grab(argv, l)
    dump(yaml_details, open(argv[-1], "wb"), protocol=HIGHEST_PROTOCOL)
    print("File saved as", argv[-1])
    return yaml_details


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
        else:
            yaml_details = grab(argv, 3)
        content = open(argv[1]).read()
        targetcode = main(yaml_details, content)
        open(argv[2], "w").write(targetcode)
        print(targetcode)
    except Exception as err:
        print("Error:", err)
