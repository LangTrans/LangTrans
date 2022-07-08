# ![LangTrans](https://see.fontimg.com/api/renderfont4/1GZyj/eyJyIjoiZnMiLCJoIjo5MywidyI6MTAwMCwiZnMiOjkzLCJmZ2MiOiIjMDAwMDAwIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/PExhbmdUcmFucz4/rogueland-slab-bold.png)
To customize any programming language

<a href="https://discord.gg/3nDwppur5S"><img alt="Discord" src="https://img.shields.io/discord/802179593293267006?style=flat-square&logo=discord"></a>
<a href="https://bijinregipanicker.gitbook.io/langtrans/"><img alt="Docs" src="https://img.shields.io/badge/Gitbook-docs-lightgrey?style=flat-square&logo=gitbook&logoColor=white"></a>
<a href="https://raw.githubusercontent.com/B-R-P/LangTrans/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/B-R-P/langtrans?style=flat-square&logo=open-source-initiative"></a>

LangTrans is a syntactic preprocessor<br>
It helps you to customize the syntax of any programming language<br>
It converts customized syntax to original syntax.<br>
It uses regular expression but it supports nesting(called part calling).
### Example
##### Customized Syntax of Python
```py
#Print
p"Hello World"
# Anonymous function
inc = (x) => x+1
# Lambda function
twice(x) = 2*x
# Single Line try-except
try inc("1") Exception print("Error:",err)
# Print Done if x is defined other wise Failed
print((x||True)?"Done":"Failed")
# Single Line if and check x defined or not
print('x is not defined') if !x
# Pipe Syntax
1 -> inc
|> print
# Arithmetic operations with functions 
print((inc+twice)(3))
#Scope syntax work like in javascript
#scope1#
print("Scope1")
print("Done")

#scope2#
print("scope2")
print("Done")

#PEP 359 - The "make" statement 
make type name(arg):
	x = 1
	y = 3

```

##### Customized Syntax of LISP

```python
func printhis(s):
	format(t,s)
printhis("Customized!")
```

### Documentation
------------------

* [Getting Started](https://bijinregipanicker.gitbook.io/langtrans/getting-started)

* [Full Documentation](https://bijinregipanicker.gitbook.io/langtrans/)

### Languages
--------------

* [Python](https://github.com/LangTrans/Python_Trans)
* [C](https://github.com/LangTrans/C_Trans)
* [Common Lisp](https://github.com/LangTrans/LISP_Trans)
* [Lua](https://github.com/LangTrans/Lua_Trans)
* [Languages by community](https://langtrans.github.io/langtransrepos/)

[Share your language here](https://forms.gle/YDEKapaTZmJspyDeA)

### Downloads
-------------

* [Standalone](https://github.com/LangTrans/LangTrans/releases/download/1.6/langtrans.exe)<br>
* [Installer](https://github.com/LangTrans/LangTrans/releases/download/1.6/LangTrans_Installer.exe)
