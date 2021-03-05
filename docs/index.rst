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

Functions
=========

 .. automodule:: LangTrans
   :members:
   :undoc-members:
   :show-inheritance:

.. raw:: html

	<dl class="py function">
	<dt id="LangTrans.check_collections">
	<code class="sig-prename descclassname">LangTrans.</code><code class="sig-name descname">check_collections</code><span class="sig-paren">(</span><em class="sig-param"><span class="n">calls</span></em>, <em class="sig-param"><span class="n">collections</span></em><span class="sig-paren">)</span><a class="headerlink" href="#LangTrans.check_collections" title="Permalink to this definition">¶</a></dt>
	<dd><p>Add collections into call list</p>
	<dl class="field-list simple">
	<dt class="field-odd">Parameters</dt>
	<dd class="field-odd"><ul class="simple">
	<li><p><strong>calls</strong> (<em>list</em>) – List with collection names and part names</p></li>
	<li><p><strong>collections</strong> (<em>dic</em>) – Collections and its names</p></li>
	</ul>
	</dd>
	<dt class="field-even">Returns</dt>
	<dd class="field-even"><p>Collections added array</p>
	</dd>
	<dt class="field-odd">Return type</dt>
	<dd class="field-odd"><p>list</p>
	</dd>
	</dl>
	</dd></dl>

	<dl class="py function">
	<dt id="LangTrans.extract">
	<code class="sig-prename descclassname">LangTrans.</code><code class="sig-name descname">extract</code><span class="sig-paren">(</span><em class="sig-param"><span class="n">spattern</span></em>, <em class="sig-param"><span class="n">collections</span></em><span class="sig-paren">)</span><a class="headerlink" href="#LangTrans.extract" title="Permalink to this definition">¶</a></dt>
	<dd><p>Extract contents needed from yaml file with regex</p>
	<dl class="field-list simple">
	<dt class="field-odd">Parameters</dt>
	<dd class="field-odd"><ul class="simple">
	<li><p><strong>spattern</strong> (<em>dic</em>) – Dictionary with yaml file details</p></li>
	<li><p><strong>collections</strong> – Collections and its names</p></li>
	</ul>
	</dd>
	<dt class="field-even">Returns</dt>
	<dd class="field-even"><p>option(replace,eachline),regex,token_names,global_chk</p>
	</dd>
	<dt class="field-odd">Return type</dt>
	<dd class="field-odd"><p>dic,dic,list,dic</p>
	</dd>
	</dl>
	</dd></dl>

	<dl class="py function">
	<dt id="LangTrans.main">
	<code class="sig-prename descclassname">LangTrans.</code><code class="sig-name descname">main</code><span class="sig-paren">(</span><em class="sig-param"><span class="n">content</span></em>, <em class="sig-param"><span class="n">spattern_details</span></em>, <em class="sig-param"><span class="n">tpattern</span></em>, <em class="sig-param"><span class="n">donly_check</span><span class="o">=</span><span class="default_value">False</span></em>, <em class="sig-param"><span class="n">donly</span><span class="o">=</span><span class="default_value">[]</span></em>, <em class="sig-param"><span class="n">loop</span><span class="o">=</span><span class="default_value">False</span></em>, <em class="sig-param"><span class="n">loplimit</span><span class="o">=</span><span class="default_value">7</span></em><span class="sig-paren">)</span><a class="headerlink" href="#LangTrans.main" title="Permalink to this definition">¶</a></dt>
	<dd><p>Convert new syntax to orginal syntax</p>
	<dl class="field-list simple">
	<dt class="field-odd">Parameters</dt>
	<dd class="field-odd"><ul class="simple">
	<li><p><strong>content</strong> (<em>str</em>) – Code with new syntax</p></li>
	<li><p><strong>spattern_details</strong> (<em>tuple</em>) – Options extracted</p></li>
	<li><p><strong>tpattern</strong> (<em>dic</em>) – Dictionary containing pattern of original syntax</p></li>
	<li><p><strong>donly_check</strong> (<em>bool</em>) – Recursion or not boolean</p></li>
	<li><p><strong>donly</strong> (<em>list</em>) – Array of part name that are called during recursion</p></li>
	<li><p><strong>loop</strong> (<em>bool</em>) – Loop option</p></li>
	<li><p><strong>loplimit</strong> (<em>int</em>) – Number of loops</p></li>
	</ul>
	</dd>
	<dt class="field-even">Returns</dt>
	<dd class="field-even"><p>Return code with original syntax</p>
	</dd>
	<dt class="field-odd">Return type</dt>
	<dd class="field-odd"><p>str</p>
	</dd>
	</dl>
	</dd></dl>

	<dl class="py function">
	<dt id="LangTrans.settings">
	<code class="sig-prename descclassname">LangTrans.</code><code class="sig-name descname">settings</code><span class="sig-paren">(</span><em class="sig-param"><span class="n">spattern</span></em><span class="sig-paren">)</span><a class="headerlink" href="#LangTrans.settings" title="Permalink to this definition">¶</a></dt>
	<dd><p>Replace var name wit its value</p>
	<dl class="field-list simple">
	<dt class="field-odd">Parameters</dt>
	<dd class="field-odd"><p><strong>spattern</strong> (<em>dic</em>) – Dictionary with yaml file details</p>
	</dd>
	<dt class="field-even">Returns</dt>
	<dd class="field-even"><p>collections,lop,loplimit</p>
	</dd>
	<dt class="field-odd">Return type</dt>
	<dd class="field-odd"><p>dic,bool,int</p>
	</dd>
	</dl>
	</dd></dl>

	<dl class="py function">
	<dt id="LangTrans.tknoptions">
	<code class="sig-prename descclassname">LangTrans.</code><code class="sig-name descname">tknoptions</code><span class="sig-paren">(</span><em class="sig-param"><span class="n">sdef</span></em>, <em class="sig-param"><span class="n">collections</span></em><span class="sig-paren">)</span><a class="headerlink" href="#LangTrans.tknoptions" title="Permalink to this definition">¶</a></dt>
	<dd><p>Extract eachline and replace option from yaml</p>
	<dl class="field-list simple">
	<dt class="field-odd">Parameters</dt>
	<dd class="field-odd"><ul class="simple">
	<li><p><strong>sdef</strong> (<em>dic</em>) – Contains token options</p></li>
	<li><p><strong>collections</strong> (<em>dic</em>) – Collections and its names</p></li>
	</ul>
	</dd>
	<dt class="field-even">Returns</dt>
	<dd class="field-even"><p>(call,eachline_option,replace_option)</p>
	</dd>
	<dt class="field-odd">Return type</dt>
	<dd class="field-odd"><p>tuple</p>
	</dd>
	</dl>
	</dd></dl>

	</div>


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
		token1:
			eachline: extra_here <line> extra_here
			replace: [[regex,"replacewith"],["regex here"]]
			call: [other_typeofsyntax]
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
		collections:
			collection_name: [typeofsyntax1,typeofsyntax2]
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
| **global** - if it is False it works only after calling it otherwise it works normally.
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
| **settings** - In setting you have loop, looplimit and variables
| 		   		*loop* -  To pass through regular expresion multiple times
| 		   		*looplimit* - Number of times to pass
| 		  		*variables* - You can make variables than can used inside regular expression by <varname>
|				*collections* - List of typeofsyntax/part with a name
|						It can be called
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
