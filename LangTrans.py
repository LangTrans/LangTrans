from re import sub,compile, MULTILINE, error as rerror
from os import system
from os.path import dirname
from sys import argv
from functools import partial

"""
LangTrans
---------
To customize syntax of any programming language.
"""

def comp(regex):
    """
    Compile regular expression

    :param regex: Regular Expression
    :type regex: str
    """
    try:
    	return compile(regex,MULTILINE)
    except rerror as err:
        print("Error:","Invalid regex")
        print(err.msg)
        print("Regex:",regex)
        print(" "*(err.pos+7)+"^")
        raise err

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
            collection=collection[1:]
            if collection not in collections:
                print("Error:",collection,"not found")
                continue
            narr += collections[collection]
            continue
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
    for tkname,opts in sdef.items():
        if isinstance(opts, dict):
            opns = dict()
            # Token options
            for opn, data in opts.items():
                if opn == "eachline":
                    opns.update({"eachline": data})
                elif opn == "replace":
                    try:
                        opns.update(
                            {
                                "replace": [
                                	(comp(reprgx), "") # For removing
                                	if isinstance(reprgx, str)
                                	else (comp(reprgx[0]), reprgx[1]) # For replacing
                                    if len(reprgx)==2
                                    else (comp(reprgx[0]), "") # For removing
                                    for reprgx in data
                                ]
                            }
                        )
                    except rerror as err:
                        print(f"Location: Replace option for token({tkname})")
                        raise err
                elif opn == "call":
                    opns.update({"call": check_collections(data, collections)})
            if "," in tkname: # Spliting Token options
            	for tk in tkname.split(","):
            		trans_options[tk] = opns
            	continue
            trans_options[tkname] = opns

    return trans_options, (check_collections(sdef["next"], collections) if "next" in sdef else [])

def addvar(variables, rv):
    """
    To Replace <varname> with its value

    :param variables: Dictionary of variables
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
    # Settings-----------------------------------------------------
    # Importing builtin variables
    variables = grab_var(dirname(__file__) + "\\builtin")
    after = None
    if "settings" in spattern:
        setting = spattern["settings"]
        del spattern["settings"]
        after = setting.get("after")
        if "varfile" in setting: # Importing variables from varfile
            variables.update(grab_var(setting["varfile"]))
        if "variables" in setting: # Adding variables in settings
            variables.update(setting["variables"])
        collections = setting["collections"] if "collections" in setting else dict()
    else:
    	collections = dict()

    trans_options = dict()
    match_options = dict()
    try:
        for part, sdef in spattern.items():
            for opt in sdef.values(): 
                if isinstance(opt, dict) and "replace" in opt:
                    for replace in opt["replace"]:  # Replacing variables in replace option
                        replace[0] = addvar(variables, replace[0])
            match_options.update(
                {
                    part: (
                        comp(addvar(variables, sdef["regex"])), # Compiled regex without variables
                        sdef["tokens"], # Token_names
                        ("global" not in sdef or sdef["global"]), # Checking Global
                    )
                }
            )
            trans_options.update({part: tknoptions(sdef, collections)})

    except rerror: # Invalid Regex Error
        print("Part:",part)
        exit()
    except KeyError as err: # For part without regex or tokens
    	print("Error:",err,"not found in",part)
    	exit()
    return after, (match_options, trans_options)

def matching(content, match_options, isrecursion):
    """
    To match parts of source code

    :param content: source code
    :param match_options: Options for each part in yaml file
    :param isrecursion: Boolean to find convert function is in recursion or not
    :type content: str
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

def convert(yaml_details, content, isrecursion=False, donly=[]):
    """
    This is main function convert new syntax to orginal syntax

    :param content: Code with new syntax
    :param yaml_details: Details extracted from yaml files
    :param isrecursion: To check recursion call or not
    :param donly: parts that should only converted(used during part calling)
    :type donly: list
    :type isrecursion: bool
    :type content: str
    :type yaml_details: tuple
    :return: Return code with original syntax
    :rtype: str
    """
    (match_options, trans_options), tpattern = yaml_details
    lopcount = 0
    if isrecursion:
    	match_options = {part:match_options[part] for part in donly}
    while 1:
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
        for part, tknmatchez in tknmatches.items():
            pattern = tpattern[part]
            tknopts, next_optns = trans_options[part]
            for tknmatch, partmatch in zip(tknmatchez, partmatches[part]):
                temp_pattern = pattern
                for tkname, match in tknmatch.items():
                    if tkname not in tknopts:
                        continue
                    for opn, data in tknopts[tkname].items():
                        # Token options
                            if opn == "replace":
                                # For replace option
                                for rgx in data:  # List of replace
                                    match = sub(*rgx, match)
                            elif opn == "call":
                                match = re_convert(content=match,donly=data)  # call list
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
                    temp_pattern = re_convert(content=temp_pattern,donly=next_optns)
                content = content.replace(partmatch, temp_pattern)
    return content

def grab(argv, l):
    """
    To get details from yaml files

    :param argv: array of arguments
    :param l: location of argument needed
    :type argv: list
    :type l: int
    :return: after command and yaml details
    :rtype:  (str or list or dic or None), tuple(dic,dic)
    """
    from yaml import load, SafeLoader
    from yaml.scanner import ScannerError
    
    try:
    	file = argv[l]+".yaml"
    	spattern = load(open(file).read(), Loader=SafeLoader)
    	file = argv[l+1]+".yaml"
    	tpattern = load(open(file).read(), Loader=SafeLoader)
    except ScannerError as err: # Error message for Invalid Yaml File
        print("Error:",file,'is invalid')
        print(err.problem,err.context)
        print(err.problem_mark.get_snippet())
        exit()
    for part in spattern:  # Template checking
    	if not(part in tpattern or part=="settings"):
    		if part.startswith("_"):# For parts with same pattern
    			bpart = part[:2] #Base part
    			if bpart in spattern:# Since template is same, tokens also same
    				spattern[part]['tokens']=spattern[bpart]['tokens']
    			else:
    				print("Error:",bpart,"for",part,"not found")
    				exit()

    			if bpart in tpattern: # Template checking
    				tpattern[part]=tpattern[bpart]
    				continue
    			part=bpart
    		print("Error: Template for",part,"not found")
    		exit()
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
    except FileNotFoundError as err:
        print(f"Error: varfile({err.filename}) not found\n")
    except ValueError:
        print(f"Error: Invalid varfile({file}.yaml)\n")
    return variables

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
    if len(argv) == 1 or (len(argv) == 2 and argv[1] == "-h"):
        print("Arg usage: <SoureFileName> <OutputFileName> <SyntaxRepr> <PatternRepr>")
        print("SyntaxRepr,PatternRepr: without extension(.yaml) ")
        exit()
    elif len(argv) < 3:
        print("Error: Insufficient number of arguments")
        exit()
    try:
        #Terminal Options------------------------------------------------
        yes = "-y" in argv  # To run after command automatically
        verbose = "-v" in argv # Verbose Mode - print source code
        no = "-n" in argv# To exit without executing after command

        if verbose:
            argv.remove("-v")
        if yes:
            argv.remove("-y")
        if no:
            argv.remove("-n")

        if "-c" in argv:  # Compile into ltz
            from pickle import dump, HIGHEST_PROTOCOL
            argv[-1] += ".ltz"
            dump(grab(argv, 2), open(argv[-1], "wb"), protocol=HIGHEST_PROTOCOL)
            print("File saved as", argv[-1])
            exit()
        elif "-f" in argv:  # Run compiled ltz
            argv.remove("-f")
            from pickle import load
            try:
                yaml_details = load(open(argv[-1] + ".ltz", "rb"))
            except FileNotFoundError as err:
                print("Error:",err.filename,"not found")
                exit()
        elif "-d" in argv:
            doc(argv[-1])
            exit()
        else:
            yaml_details = grab(argv, 3)
        #-------------------------------------------------------------------
        after, yaml_details = yaml_details
        content = open(argv[1]).read()
        re_convert = partial(convert,yaml_details=yaml_details,isrecursion=True)
        targetcode = convert(yaml_details,content)
        print("Compiled successfully")
        open(argv[2], "w").write(targetcode)
        print("Saved as",argv[2])
        if verbose:
            print(targetcode)
        # For after command in settings
        if not(no) and after:  # Not None
            if isinstance(after, list):  # For multiple commands
                after = " && ".join(after)
            elif isinstance(after, dict):  # After command for different OS
                from platform import system
                osname = system().lower()  # Current os name
                if osname not in after:
                    print(f"Error: No after command for {osname}. OS name eg. linux, windows")
                    exit()
                after = after[osname]
            if not isinstance(after, str):
                print("Error: Invalid after command")
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
        print("Program Error:",err)
