.. LangTrans documentation master file, created by
   sphinx-quickstart on Thu Jan 14 11:17:17 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to LangTrans's documentation!
=====================================
LangTrans is used to customize any programming language.
You can make your own syntax for any programming languages. 

How it works?
=============
LangTrans convert your syntax into orginal syntax.
Regular Expression is used to extract tokens from your language.
It should be written in a yaml file.
You should write template of syntax of orginal language in another yaml file.
LangTrans take both yaml files as input and convert code written in new syntax to orginal syntax.

.. toctree::
   :maxdepth: 3
   :caption: Contents:
   :numbered:
Methods
=======

.. automodule:: LangTrans
   :members:
   :undoc-members:
   :show-inheritance:

Implementation
==============
| To customize you should extract tokens with regular expression.
| Then you should create the template of orginal language with token you extracted.
Token Extraction
----------------
YAML file with regular expression

Syntax
^^^^^^
.. code-block:: yaml

	typeofsynax:
		regex: regex (regex for token1) <var1> regex
		tokens: ["token1","token2","token3"]
		token1:
			eachline: extra_here <line> extra_here
			replace: [[regex,"replacewith"],["regex here"]]
	_1typeofsyntax:
		regex: another regex
		tokens: ["token1","token2","token3"]
	#Code here like above
	#...................
	#...................
	#...................
	settings:
		loop: #boolean value here(default: False)
		looplimit: #integer here
		variables:
			var1: #regex
			var2: #regex
			var3 : #regex

| **typeofsyntax** - Type of syntax you wanted to match(arithmetic,loop,etc)
| 			   		If one type have same pattern and different regex
| 			   		You can write _<anycharacter><typeofsyntax> for next regex.(like _1typeofsyntax)
| 			   		Both regex use one pattern(typeofsyntax)
| **regex** - Place where regular expression to extract particular block of code including tokens.
| 			Regular expression for tokens must be inside brackets.
| **tokens** - Name of tokens you wanted to extract
| **token1** - You can modify tokens you extracted
| 		 	*eachline* - You can additional content for eachline
| 		 				<line> represents orginal content in eachline
| 		 				It loops through every line
| 		 	*replace* - To replace or delete any unwanted content in token
| 		 				All should be in a list
| 		 				To replace add a list with first as regular expression of content
| 		 				and second with content you wanted to replace with
| 		 				To delete add a list with one content(regular expression of content you wanted to remove) 
| **settings** - In setting you have loop, looplimit and variables
| 		   		*loop* -  To pass through regular expresion multiple times
| 		   		*looplimit* - Number of times to pass
| 		  		*variables* - You can make variables than can used inside regular expression by <varname>
Example
^^^^^^^
.. code-block:: yaml

	shorthand:
	  regex: <var>\+=<var>
	  tokens: [var,num]
	settings:
		loop: False
		variables:
			var: ([A-Za-z0-9_]+)

Template
--------
Template of orginal language in YAML

Syntax
^^^^^^
.. code-block:: yaml

	typeofsyntax: "syntax1 <token1> middle syntax <token2> syntax3 <token3>"

| You can represent syntax of orginal language here(like a template)
| **token1,token2,token3**  - Represents tokens extracted
| Write tokens inside template of orginal language(<tokename>)

Example
^^^^^^^
.. code-block:: yaml

	shorthand: (incf <var> <num>)

Command Line
============
**Usage:**

.. code-block:: console

	langtrans <SoureFileName> <OutputFileName> <SyntaxRepr> <PatternRepr>

| **SourceFileName** - File name of source code written with new syntax
| **OutputFileName** - File name of source code you want to generate with orginal syntax
| **SyntaxRepr**     - File name of YAML file for token extraction without extension(.yaml)
| **PatternRepr**    - File name of YAML file with template of orginal language without extension
As Module
=========
.. code-block:: python
	
	#Common Lisp is taken as example
	from LangTrans import main
	#source code wriiten in new syntax
	newcode = open("source.clisp").read()
	#source.yaml-New syntax
	#target.yaml-Syntax of orginal language(Lisp)
	targetcode = main(newcode, "source.yaml", "target.yaml")#Transpiling...
	open("target.lisp","w").write(targetcode)
	print(targetcode)

Downloads
=========

| `Standalone <https://drive.google.com/uc?export=download&id=14lanbflcifeIM3PSCL3fF3rFxSBPrt7W>`_
| `Installer <https://drive.google.com/uc?export=download&id=15soZJZCDrDP5KGVxvD5L9Sg7109XVc7y>`_
| `Source Code <https://github.com/B-R-P/LangTrans>`_
