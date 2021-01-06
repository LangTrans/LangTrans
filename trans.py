#Common Lisp is taken as example

from LangTrans import main
#source code wriiten in new syntax
newcode = open("source.clisp").read()
							#New syntax 
targetcode = main(newcode, "source.yaml", "target.yaml")#Transpiling...
										  #Syntax of orginal language(Lisp)
print(targetcode)
open("target.lisp","w").write(targetcode)