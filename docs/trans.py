#Common Lisp is taken as example
from LangTrans import main
#source code wriiten in new syntax
newcode = open("source.clisp").read()
#source.yaml-New syntax
#target.yaml-Syntax of orginal language(Lisp)
targetcode = main(newcode, "source.yaml", "target.yaml")#Transpiling...
open("target.lisp","w").write(targetcode)
print(targetcode)