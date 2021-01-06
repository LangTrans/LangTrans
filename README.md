# LangTrans
To customize any programming language

LangTrans  help you to customize syntax of any programming language.

### Customize with LangTrans

First you should write code with new syntax.(Like source.clisp)

Second you should write regular expression to extract tokens from customized language, in a yaml file.(Like source.yaml)

Third to replace customized syntax with original syntax. With help of token extracted, write orginal syntax.(Like target.yaml)

Run trans.py (It will convert your customized language to orginal language)

Then you can use generated source code(Like target.lisp).

### Languages

[Common Lisp]("https://github.com/B-R-P/LangTrans")