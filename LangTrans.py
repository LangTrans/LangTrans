from yaml import load, SafeLoader
from re import compile as comp, MULTILINE, sub

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
    for tkname in sdef["tokens"]:
        if tkname in sdef:
            tknopt = sdef[tkname]  # Token options
            if "eachline" in tknopt:
                oneachline.update({tkname: tkopt["eachline"]})
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


def extract(spattern, collections):
    """
    This function extract contents needed from yaml file with regex

    :param spattern: Dictionary with yaml file details
    :type spattern: dic
    :return: option(replace,eachline),regex,token_names
    :rtype: dic,dic,list
    """
    options = dict()
    regexs = dict()
    global_chk = dict()
    tknames = []
    for part, sdef in spattern.items():
        if part[0] == "_":
            sdef["tokens"] = spattern[part[2:]]["tokens"]
        regexs.update({part: comp(sdef["regex"], MULTILINE)})
        options.update({part: tknoptions(sdef, collections)})
        tknames.append(sdef["tokens"])
        global_chk.update({part: (sdef["global"] if "global" in sdef else True)})
    return (options, regexs, tknames, global_chk)


def settings(spattern):
    """
    This function replace var name wit its value

    :param spattern: Dictionary with yaml file details
    :type spattern: dic
    :return: lop,loplimit
    :rtype: bool,int
    """
    collections = dict()
    loop = False
    loplimit = 7
    if "settings" in spattern:
        setting = spattern["settings"]
        if "loop" in setting:
            loop = setting["loop"]
        if "looplimit" in setting:
            loplimit = setting["looplimit"]
        if "variables" in setting:  # Replacing variable name with its value
            for part, sdef in spattern.items():
                if part != "settings":
                    rv = sdef["regex"]  # regex with var
                    for varname, rgx in setting["variables"].items():
                        if "<" + varname + ">" in rv:  # regex without var
                            rv = rv.replace("<" + varname + ">", rgx)
                    spattern[part]["regex"] = rv
        del spattern["settings"]
        if "collections" in setting:
            collections = setting["collections"]
    return (collections, loop, loplimit)


def main(
    content,
    spattern_details,
    tpattern,
    donly_check=False,
    donly=[],
    loop=False,
    loplimit=7,
):
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
    options, regexs, tokens, global_chk = spattern_details

    # matching tokens from code with regular expressions
    # --------------------------------------------------------------
    tknmatches = dict()
    partmatches = dict()
    for (part, pattern), tknames in zip(regexs.items(), tokens):
        if donly_check:  # For recursion
            if part not in donly:
                continue
        elif not global_chk[part]:
            continue
        # Part matching
        partmatches[part] = [i.group() for i in pattern.finditer(content)]
        # Token matching
        unitkn = len(tknames) == 1
        tknmatches[part] = [
            {tkname: matches}
            if unitkn
            else {tkname: match for match, tkname in zip(matches, tknames)}
            for partmatched in partmatches[part]
            for matches, tkname in zip(pattern.findall(partmatched), tknames)
        ]
    del regexs, tokens, global_chk, donly, donly_check
    # ---------------------------------------------------------------
    lopcount = 0
    while 1:
        for part in tknmatches:  # Replacing parts in source code
            if part[0] != "_":  # Find two regex extract with one pattern
                pattern = tpattern[part]
            else:
                pattern = tpattern[part[2:]]
            calls, oneachline, replacer = options[part]
            for tknmatch, partmatch in zip(tknmatches[part], partmatches[part]):
                temp_pattern = pattern
                for tkname, match in tknmatch.items():
                    # Token options
                    if tkname in calls:  # For part calls
                        match = main(
                            match,
                            spattern_details,
                            tpattern,
                            donly_check=True,
                            donly=calls[tkname],
                            loop=loop,
                            loplimit=loplimit,
                        )
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
                    # Replacing pattern tokens expression with tokens
                    temp_pattern = temp_pattern.replace(f"<{tkname}>", match)
                content = content.replace(partmatch, temp_pattern)
        lopcount += 1
        if not loop:
            break
        elif lopcount == loplimit:
            break
    return content


if __name__ == "__main__":
    from sys import argv, exit

    if len(argv) == 1 or (len(argv) == 2 and argv[1] == "-h"):
        print("Arg usage: <SoureFileName> <OutputFileName> <SyntaxRepr> <PatternRepr>")
        print("SyntaxRepr,PatternRepr: without extension(.yaml) ")
        exit()
    elif len(argv) < 5:
        print("Error: Insufficient number of arguments")
        exit()
    try:
        spattern = load(open(argv[3] + ".yaml").read(), Loader=SafeLoader)  # Source
        tpattern = load(open(argv[4] + ".yaml").read(), Loader=SafeLoader)  # Target
        content = open(argv[1]).read()
        collections, loop, loplimit = settings(spattern)  # Collections Added
        targetcode = main(
            content,
            extract(spattern, collections),
            tpattern,
            loop=loop,
            loplimit=loplimit,
        )
        open(argv[2], "w").write(targetcode)
        print(targetcode)
    except Exception as err:
        print("Error:", err)
