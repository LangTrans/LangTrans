# ![LangTrans](https://see.fontimg.com/api/renderfont4/1GZyj/eyJyIjoiZnMiLCJoIjo5MywidyI6MTAwMCwiZnMiOjkzLCJmZ2MiOiIjMDAwMDAwIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/PExhbmdUcmFucz4/rogueland-slab-bold.png)
To customize any programming language

<a href="https://discord.gg/3nDwppur5S"><img alt="Discord" src="https://img.shields.io/discord/802179593293267006?style=flat-square&logo=discord"></a>
<a href="https://langtrans.readthedocs.io/en/latest/"><img alt="Docs" src="https://img.shields.io/readthedocs/langtrans?style=flat-square&logo=read-the-docs"></a>
<a href="https://raw.githubusercontent.com/B-R-P/LangTrans/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/B-R-P/langtrans?style=flat-square&logo=open-source-initiative"></a>

LangTrans is a syntactic preprocessor<br>
It helps you to customize the syntax of any programming language<br>
It converts customized syntax to original syntax.<br>
It uses regular expression but it supports nesting(called part calling).

##### Customized Syntax of LISP

```python
func printhis(s):
	format(t,s)
printhis("Customized!")
```

##### Original Syntax 

```lisp
(defun printhis (s)
	(format t s)
)
(printhis "Customized!")
```

### 📝Customize with LangTrans

First you should write code with new syntax.<br>(Like example/source.clisp)

Second you should write regular expression to extract tokens from customized language, in a yaml file<br>(Like example/source.yaml)

Third to replace customized syntax with original syntax with help of token extracted, write the template of orginal syntax.<br>(Like example/target.yaml)

```console
py langtrans.py source.clisp target.lisp source target
                #<customized> <orginal> <syntax> <template>
```
(It will convert your customized language to original language)

Then you can use generated source code.<br>(Like target.lisp).

### 📄Documentation
For more see the [Documentation](https://langtrans.readthedocs.io/en/latest/).

### Languages

* [Common Lisp](https://github.com/B-R-P/LISP_Trans)
* [Python](https://github.com/LangTrans/Python_Trans)
* [Lua](https://github.com/B-R-P/Lua_Trans)
* [Languages by community](https://langtrans.github.io/langtransrepos/)

[Share your language here](https://forms.gle/YDEKapaTZmJspyDeA)
### Downloads
[Standalone](https://drive.google.com/uc?export=download&id=14lanbflcifeIM3PSCL3fF3rFxSBPrt7W)<br>
[Installer](https://drive.google.com/uc?export=download&id=15soZJZCDrDP5KGVxvD5L9Sg7109XVc7y)
