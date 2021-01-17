from sys import argv,exit
from LangTrans import main
if len(argv)==1 or (len(argv)==2 and argv[1]=="-h"):
	print("Arg usage: <SoureFileName> <OutputFileName> <SyntaxRepr> <PatternRepr>")
	print("SoureFileName: *.C* SyntaxRepr,PatternRepr: without extension(.yaml) ")
	exit()
elif len(argv)<5:
	print("Error: Insufficient number of arguments")
	exit()
try:
	targetcode = main(open(argv[1]).read(), argv[3]+".yaml", argv[4]+".yaml")
	open(argv[2],"w").write(targetcode)
	print(targetcode)
except Exception as err:
	print("Error:",err)