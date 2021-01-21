# ![LangTrans](https://drive.google.com/uc?export=download&id=1IXL9Gx_uz4c4gMm52IXsNgDKJ0WgC0jb)
To customize any programming language

LangTrans  help you to customize syntax of any programming language.<br>It convert customized syntax to original syntax.

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

### Customize with LangTrans

First you should write code with new syntax.<br>(Like source.clisp)

Second you should write regular expression to extract tokens from customized language, in a yaml file<br>(Like source.yaml)

Third to replace customized syntax with original syntax. With help of token extracted, write orginal syntax.(Like target.yaml)

Run trans.py<br>(It will convert your customized language to original language)

Then you can use generated source code.<br>(Like target.lisp).

### Documentation
See the [Documentation](https://langtrans.readthedocs.io/en/latest/).

### Languages

[Common Lisp](https://github.com/B-R-P/LISP_Trans)

Other languages coming soon...

### Downloads
[Standalone](https://drive.google.com/uc?export=download&id=14lanbflcifeIM3PSCL3fF3rFxSBPrt7W)<br>
[Installer](https://drive.google.com/uc?export=download&id=15soZJZCDrDP5KGVxvD5L9Sg7109XVc7y)

