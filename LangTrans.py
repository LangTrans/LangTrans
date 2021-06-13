from os import system
from os.path import dirname
from sys import argv, exit
from functools import partial
from colorama import init,Fore
init(autoreset=True)#  For colored error
error_msg=Fore.RED+"Error:"
"""
LangTrans
---------
To customize/upgrade syntax of any programming language.
"""
def comp(regex):
    """
    Compile regular expression

    :param regex: Regular Expression
    :type regex: str
    """         # To emulate tokens(in parsers)
    regex = regex.replace(" ",r"\s+")\
                 .replace("~",r"\s*")
    try:                    #re.MULTILINE=8
    	return compile(regex,8)
    except rerror as err:
        print(error_msg,"Invalid regex")
        print(err.msg)
        print("Regex:",regex.replace("\n",r"\n")\
                            .replace("\t",r"\t"))
        print(" "*(err.pos+7)+"^")
        raise err

def check_collections(calls, collections):
    """
    This add collections into call list

    :param calls: List with collection names and part names
    :type calls: list
    :param collections: Dictionary of collections and its names
    :type collections: dict
    :return: Collection replaced call list
    """
    if not collections:
        return calls
    narr = []
    for collection in calls:
        if collection.startswith("$"):
            collection=collection[1:]
            if collection not in collections:
                exit(f"Error: ${collection} not found")
            narr += collections[collection]
            continue
        narr.append(collection)
    return tuple(narr)

def tknoptions(sdef, collections):
    """
    This function extract token options from yaml file

    :param sdef: Contains token options
    :type spattern: dict
    :param collections: Dictionary of collections and its names
    :return: unmatches,default values,translation options and next call list
    :rtype: dict,dict,dict,list
    """
    trans_option = {}
    unmatches = {}
    defaults = {}
    tkns = sdef["tokens"]
    for tkname,opts in sdef.items():
        if isinstance(opts, dict):
            opns = {}
            # Token options
            for opn, data in opts.items():
                if opn == "eachline":
                    opns.update({"eachline": data})
                elif opn == "replace":
                    try:
                        opns.update(
                            {
                                "replace": tuple([ # Tuple
	                            	(comp(reprgx[0]), reprgx[1]) # For replacing
	                                if len(reprgx)==2
	                                else (comp(reprgx[0]), "") # For removing
	                                for reprgx in data
                                ])
                            }
                        )
                    except rerror as err:
                        print(f"Location: Replace option for token({tkname})")
                        raise err
                elif opn == "call":
                    opns.update({"call": check_collections(data, collections)})
                elif opn == "unmatch":
                    if not isinstance(data, list):
                        data = (data,)
                    try:                            # Compiling regex
                        unmatches.update({tkname:map(comp,data)})
                    except rerror as err:
                        print(f'Location: Unmatch for token({tkname})')
                        raise err
                elif opn=="default":
                    defaults.update({tkname:data})
            if "," in tkname: # Spliting Token options
            	for tk in tkname.split(","):
                    if tk not in tkns: return print(f"Error: {tk} not found in tokens")#TypeError
                    trans_option[tk] = opns
            	continue
            if tkname not in tkns:
                return print(f"{error_msg} {tkname} not found in tokens")#TypeError
            trans_option[tkname] = opns
                                            #Next Options
    return unmatches,defaults,trans_option, (check_collections(sdef["next"], collections) if "next" in sdef else 0)

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

def compile_rgx(errors,var):
    for name,error in errors.items():
        if name=="outside":
            compile_rgx(error,var)
            continue
        error['regex']=comp(addvar(var,error['regex']))

def comp_err(name,variables):
    """
    Compiling regexs in error file
    :param name: Name of errfile
    :param variables: Global variables
    :type name: str
    :type variables: dict
    :return: compiled error inside and outside part
    :rtype: (dict,dict)
    """
    errors_def=load_yaml(name)
    outside={}
    for part,errors in errors_def.items():
        compile_rgx(errors,variables)
        if 'outside' in errors:
            outside[part]=errors.pop('outside')
    if 'outside' in errors_def: # Outside not related to part
        outside['']=errors_def.pop('outside')
    return errors_def,outside

def extract(spattern):
    """
    This function extract contents needed from yaml file with regex

    :param spattern: Dictionary with yaml file details
    :type spattern: dict
    :return: after command and (match options, token options)
    :rtype: (None|str|list|dict),tuple(dict,dict)
    """
    # Settings-----------------------------------------------------
    # Importing builtin variables
    variables = grab_var(dirname(__file__) + "\\builtin")
    after = None
    errfile = 0#False
    #outside=0
    if "settings" in spattern:
        setting = spattern.pop('settings')
        after = setting.get("after")
        if "varfile" in setting: # Importing variables from varfile
            variables.update(grab_var(setting["varfile"]))
        if "variables" in setting: # Adding variables in settings
            variables.update(setting["variables"])
        if 'errfile' in setting:
            errfile,outside = comp_err(setting['errfile'],variables)
        collections = setting["collections"] if "collections" in setting else 0#False
    else:
    	collections = 0#False
    trans_options = {}
    match_options = {}
    try:
        for part, sdef in spattern.items():
            for opt in sdef.values(): 
                if isinstance(opt, dict) and "replace" in opt:
                    for replace in opt["replace"]:  # Replacing variables in replace option
                        replace[0] = addvar(variables, replace[0])
            regex = comp(addvar(variables, sdef["regex"]))# Compiled regex without variables
            tokens = tuple(sdef["tokens"])# Token_names
            if regex.groups!=len(tokens):
                if regex.groups==0 and len(tokens)<2:
                    regex =  comp(f"({regex.pattern})")
                else:           
                    print("Part:",part)
                    print("Token Names:",len(tokens),"Capture Groups:",regex.groups)
                    exit(error_msg+" Number of token names is not equal to number of capture groups")
            unmatches,defaults,*tknopns = tknoptions(sdef, collections)
            match_options.update({
                part: (
                    regex, 
                    tokens, 
                    int("global" not in sdef or sdef["global"]), # Checking Global
                    (   # Unmatch regexs for tokens
                        tuple([addvar(variables,unmatch) for unmatch in unmatches]),
                        ( # Unmatch regexs for part 
                            tuple([comp(addvar(variables,unmatch)) for unmatch in sdef["unmatch"]])
                            if "unmatch" in sdef
                            else ()
                        )
                    ),
                    defaults,
                    int("once" in sdef and sdef["once"]),
                    (errfile[part] if errfile and part in errfile else 0)#0-False
                )
            })
            trans_options.update({part: tknopns})

    except (rerror,TypeError): #Regex and unknown token option error 
        exit(f"Part:{part}")
    except KeyError as err: # For part without regex or tokens
    	exit(f"{error_msg} {err} not found in {part}")
    return after, (match_options, trans_options,(outside if errfile and outside else 0))

def err_report(part,msg,name,match,tkns,content,matchstr):
    pos,l,indexed = getotalines(content.splitlines(),matchstr)
    err_part=match.group()
    if part: # Part Name
        print(f"[{Fore.MAGENTA+part+Fore.RESET}]")
    line=indexed[0].lstrip()
    lineno=str(pos+1)+" |"
    #error Line
    print(Fore.CYAN+lineno,line.replace(err_part,Fore.RED+err_part+Fore.RESET))
    total_msg = addvar(# Replacing variables in main and err match
        {# Err
            '$'+str(l):tkn
            for l,tkn in enumerate(match.groups(),start=1)
        },
         addvar(tkns,msg)# Main
    )
    #Error Name
    print(" "*(line.index(err_part)+len(lineno)),Fore.RED+name.replace("_"," "))
    print(Fore.YELLOW+total_msg)#Error Info
    exit()

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
    partmatches = {}
    oncedone = matching.oncedone
    for part, options in match_options.items():
                                    # Unmatches
        pattern,tknames,global_chk,(untkn,unpart),defaults,once,err = options
        if not isrecursion:
            if not global_chk: continue # For "global: False"
            if once: # For parts match once
                if part in oncedone: continue
                matching.oncedone.append(part)
        partmatch = []      # Part matching
        for match in pattern.finditer(content):
            matchstr = match.group()
            if unpart and any((bool(rgx.search(matchstr)) for rgx in unpart)):
                continue
            match = { # Assigning default value for None  
                        tkname:(m if m!=None else defaults.get(tkname,""))
                        for tkname,m in zip(tknames,match.groups())
                    }
            if err:# If error definition exists
                for name,error in err.items(): # Static Code Analysis
                    err_match = error['regex'].search(matchstr)
                    if err_match:
                        err_report(part,error['msg'],name,err_match,match,content,matchstr)
                                          #Token names and matched tokens
            if untkn and any(( # Checking unmatch on every token
                        bool(rgx.search(match))
                        for match, tkname in match.items()
                        for rgx in untkn.get(tkname,())
                    )):
                continue
            partmatch.append((matchstr,match))
        if partmatch:
            partmatches.update({part:partmatch})
    return partmatches
matching.oncedone = []  # List of "once: True" parts that are already matched

def outside_err(outside,content):
    for part,errors in outside.items():
        for name,error in errors.items():
            err_match = error['regex'].search(content)
            if err_match:
                err_report(part,error.get('msg',""),name,err_match,{},content,err_match.group())

def convert(yaml_details, content, isrecursion=False, donly=()):
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
    (match_options, trans_options, outside), tpattern = yaml_details
    lopcount = 0
    if isrecursion:
    	match_options = {part:match_options[part] for part in donly}
    elif outside: # Outside error checks
        outside_err(outside,content)
    while 1:
        partsmatches = matching(content, match_options, isrecursion)
        if not partsmatches:  # Break when no match found
            break
        elif lopcount > 100:
            print(error_msg+" Loop Limit Exceded")
            print("Bug Locations:\n","\n".join((f"{part}:{matches}" for part,matches in partsmatches.items())))
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
                    for opn, data in tknopts[tkname].items():
                        # Token options
                            if opn == "replace":
                                from re import sub
                                # For replace option
                                for rgx in data:  # data-match and replace
                                    match = sub(*rgx, match)
                            elif opn == "call":
                                match = re_convert(content=match,donly=data)  # call list
                            elif opn == "eachline": # For oneachline option
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
                try:
                    content = content.replace(partmatch, temp_pattern)
                except Exception:
                    print(temp_pattern)
    return content

def getotalines(lines,substring):
    sublines = substring.splitlines()
    sublen = len(sublines)
    for pos,line in enumerate(lines):
        if sublines[0] in line: #If first line matched
            if pos>=(len(lines)-sublen): # If reached end of string
                return
            indexed = lines[pos:pos+sublen] # rest of line
            for linepart,subline in zip(indexed,sublines[1:]): # Check rest of line
                if subline not in linepart: # Break if subline not matched
                    break
            else: # Break if sublines are matched
                break
    else: # Return if sublines are not matched in lines
        return# No match Found
    return pos,sublen,indexed#dict(zip(sublines,indexed))

def load_yaml(file):
    """
    To load yaml files
    :param file: File base name
    :type file: str
    :return: Yaml Details
    :rtype: dict 
    """
    from yaml import load, SafeLoader
    from yaml.scanner import ScannerError
    from yaml.parser import ParserError
    file+=".yaml"
    try:
        return load(open(file).read(), Loader=SafeLoader)
    except (ScannerError,ParserError) as err: # Error message for Invalid Yaml File
        print(error_msg,file,'is invalid')
        print(err.problem,err.context)
        print(err.problem_mark.get_snippet())
        exit()
    except FileNotFoundError:
        exit(f"{error_msg} {file} not found")

def grab(source, target):
    """
    To get details from source and target yaml files

    :param argv: array of arguments
    :param l: location of argument needed
    :type argv: list
    :type l: int
    :return: after command and yaml details
    :rtype:  (str or list or dict or None), tuple(dict,dict)
    """
    spattern = load_yaml(source)
    tpattern = load_yaml(target)
    for part in spattern:  # Template checking
    	if not(part in tpattern or part=="settings"):
            if part.startswith("_"):# For parts with same pattern
                bpart = part[2:] #Base part
                if bpart in spattern:# Since template is same, tokens also same
                	spattern[part]['tokens']=spattern[bpart]['tokens']
                else:
                	exit(f"{error_msg} {bpart} for {part} not found")
                if bpart in tpattern: # Template checking
                	tpattern[part]=tpattern[bpart]
                	continue
                part=bpart
            if not spattern[part]['tokens']:
                tpattern[part]=""
                continue
            exit(f"{error_msg} Template for {part} not found")
    after, rest = extract(spattern)
    return after, (rest, tpattern)

def grab_var(file):
    """
    To variables from external file

    :param file: Address of external file
    :type file: str
    :return: Dictionary of variables
    :rtype: dict
    """
    variables = {}
    try:
        v = load_yaml(file)
        if v is not None:
            variables.update(v)
    except ValueError:
        exit(f"{error_msg} Invalid varfile({file}.yaml)\n")
    return variables

def get_ltz(filename):
    from pickle import load
    try:
        return load(open(filename+".ltz", "rb"))
    except FileNotFoundError as err:
        exit(f"{error_msg} {err.filename} not found")

def doc(file):
    """
    To print documentation of part in yaml file
    CommandLine: python langtrans.py -d source

    :param file: Addres of file
    :type file: str
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
        print(part + " " * (p - len(part)), 
              tkns + " " * (t - len(tkns)), 
              about.replace('\n', '\n'+" "*(p+t+2))
             )
  
if __name__ == "__main__":
    if len(argv) == 1 or (len(argv) == 2 and argv[1] == "-h"):
        print("Arg usage: <SoureFileName> <OutputFileName> <SyntaxRepr> <PatternRepr>")
        exit("SyntaxRepr,PatternRepr: without extension(.yaml)")
    elif len(argv) < 3:
        exit(error_msg+" Insufficient number of arguments")
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
            from re import compile, error as rerror

            argv[-1] += ".ltz"
            dump(grab(argv[2], argv[3]), open(argv[-1], "wb"), protocol=HIGHEST_PROTOCOL)
            print(Fore.GREEN+"Compiled successfully")
            exit("File saved as "+argv[-1])
        elif "-f" in argv:  # Run compiled ltz
            argv.remove("-f")
            yaml_details = get_ltz(argv[-1])
        elif "-d" in argv:
            doc(argv[-1])
            exit()
        else:
            from re import compile, error as rerror
            from collections import defaultdict

            yaml_details = grab(argv[3], argv[4])
        #-------------------------------------------------------------------
        after, yaml_details = yaml_details
        content = open(argv[1]).read()
        re_convert = partial(convert,yaml_details=yaml_details,isrecursion=True)
        targetcode = convert(yaml_details,content)
        open(argv[2], "w").write(targetcode)
        print(Fore.GREEN,"Saved as",argv[2])
        if verbose:
            print(targetcode)
        # For after command in settings
        if not(no) and after:  # Not None
            if isinstance(after, dict):  # After command for different OS
                from platform import system as systm
                osname = systm().lower()  # Current os name
                if osname not in after:
                    print(f"{error_msg} No after command for {osname}. OS name eg. linux, windows")
                    exit()
                after = after[osname]
            if isinstance(after, list):  # For multiple commands
                after = " && ".join(after)
            # To use address of source and target file in 'after' command
            after_var = (
                            ("$target",argv[2]),
                            ("$source",argv[1]),
                            ("$current",dirname(__file__))
                        )
            for var, val in after_var:
                after = after.replace(var, val)
            if yes:
                system(after)
                exit()
            print("\nEnter to run and n to exit\nCommand:",after)
            inp = input()
            if inp.lower() != "n":
                system(after)
    except Exception as err:
        print("Program",error_msg,err)
