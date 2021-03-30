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

Function
========

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
		global: True
		next: [other_typeofsyntax,$collection_name]
		token1:
			eachline: extra_here <line> extra_here
			replace: [[regex,"replacewith"],["regex here"]]
			call: [other_typeofsyntax,$collection_name]
	_1typeofsyntax:
		regex: another regex
		tokens: ["token1","token2","token3"]
	#Code here like above
	#...................
	#...................
	#...................
	settings:
		collections:
			collection_name: [typeofsyntax1,typeofsyntax2]
		variables:
			var1: #regex
			var2: #regex
			var3 : #regex
		after: #Command Line Commands
		#after:
		#- Command One
		#- Command Two
		#after:
		#	windows: Command 
		#	linux: Command

| **typeofsyntax** - Type of syntax you wanted to match(arithmetic,loop,etc)
| 			   		If one type have same pattern and different regex
| 			   		You can write _<anycharacter><typeofsyntax> for next regex.(like _1typeofsyntax)
| 			   		Both regex use one pattern(typeofsyntax)
| **regex** - Place where regular expression to extract particular block of code including tokens.
| 			Regular expression for tokens must be inside brackets.
| **tokens** - Name of tokens you wanted to extract
| **global** - If it is False it works only after calling it otherwise it works normally.
| **next** - To pass converted syntax into another or same part
| **token1** - You can modify tokens you extracted
| 		 	*eachline* - You can additional content for eachline
| 		 				<line> represents orginal content in eachline
| 		 				It loops through every line
| 		 	*replace* - To replace or delete any unwanted content in token
| 		 				All should be in a list
| 		 				To replace add a list with first as regular expression of content
| 		 				and second with content you wanted to replace with
| 		 				To delete add a list with one content(regular expression of content you wanted to remove)
|			*call* - To call another regex from another part/typeofsyntax
|				 Write name of part/typeofsyntax inside array of call.
|				 It work only on token(token1) part extracted from source code.
| **settings** - For settings, like variables, collections, after command
| 		  		*variables* - You can make variables than can used inside regular expression by <varname>
|				*collections* - List of typeofsyntax/part with a name
|						It can be used in call and next
|				*after* - To run command line commands after translation
|					  $target and $source can be used inside command($target-address of translated file,$source-address of source file)
|					  eg. python $target
Example
^^^^^^^
.. code-block:: yaml

	shorthand:
	  regex: <var>\+=<var>
	  tokens: [var,num]
	settings:
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

Downloads
=========

| `Standalone <https://github.com/LangTrans/LangTrans/releases/download/1.6/langtrans.exe>`_
| `Installer <https://github.com/LangTrans/LangTrans/releases/download/1.6/LangTrans_Installer.exe>`_
| `Source Code <https://github.com/LangTrans/LangTrans>`_
