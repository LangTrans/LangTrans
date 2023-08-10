<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/_LangTrans_dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/_LangTrans_light.svg">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="./assets/_LangTrans_light.svg">
</picture>

<br />

[![Discord](https://img.shields.io/discord/802179593293267006?style=flat-square&logo=discord)](https://discord.gg/3nDwppur5)
[![Docs](https://img.shields.io/badge/Gitbook-docs-lightgrey?style=flat-square&logo=gitbook&logoColor=white)](https://bijinregipanicker.gitbook.io/langtrans/)
[![License](https://img.shields.io/github/license/B-R-P/langtrans?style=flat-square&logo=open-source-initiative)](https://raw.githubusercontent.com/B-R-P/LangTrans/main/LICENSE)
[![myPy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

LangTrans is a syntactic preprocessor that allows you to customize the syntax of any programming language. It operates by translating your custom syntax into the original language syntax, enabling you to write code in a manner that suits your style, while still conforming to the programming language's specifications. It employs regular expressions to extract tokens from your custom language and uses these tokens to generate a representation of the original language syntax.

## Quick Start

There are two ways you can install LangTrans:

### **Clone repository**

Use the following command to clone the repository:

```bash
git clone https://github.com/LangTrans/LangTrans.git
```

After cloning, navigate into the LangTrans directory.

Once repo is cloned to computer, run this command to install dependencies:

    pip install -r requirements.txt

### **Download executable**

Go to [Releases](https://github.com/LangTrans/LangTrans/releases) and download the [latest executable]((https://github.com/LangTrans/LangTrans/releases/download/1.6/langtrans.exe)) or a [installer](https://github.com/LangTrans/LangTrans/releases/download/1.6/LangTrans_Installer.exe).

## Usage

You can use LangTrans from the command line using the following structure:

```bash
py langtrans.py <SoureFileName> <OutputFileName> <SyntaxRepr> <PatternRepr>
```

* **SoureFileName**: Name of the source code file written with your new syntax
* **OutputFileName**: Name of the source code file you want to generate with the original syntax
* **SyntaxRepr**: Name of the YAML file for your syntax representation (without .yaml extension)
* **PatternRepr**: Name of the YAML file for the pattern representation of the original language (without .yaml extension)

### Flags

You can also use the following options with the langtrans.py command:

* `-h`: Displays help information
* `-v`: Activates verbose mode
* `-y`: Executes the 'after' command automatically
* `-n`: Exits without executing the 'after' command

## Examples

Here is our take on custom [Python](https://github.com/LangTrans/Python_Trans):

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

Here is a sample of the customized [Common Lisp](https://github.com/LangTrans/LISP_Trans):

```lisp
func printhis(s):
  format(t,s)
printhis("Customized!")
```

## Languages

* [Python](https://github.com/LangTrans/Python_Trans)
* [C](https://github.com/LangTrans/C_Trans)
* [Common Lisp](https://github.com/LangTrans/LISP_Trans)
* [Lua](https://github.com/LangTrans/Lua_Trans)
* [Languages by community](https://langtrans.github.io/langtransrepos/)

You can share your language [here](https://forms.gle/YDEKapaTZmJspyDeA).

## Testing

From the root run:

    pytest tests/test_LangTrans.py

## Contributing

We welcome contributions from everyone. If you're interested in contributing, here's how you can help:

1. **Creating versions for other languages**: If you're proficient in a particular programming language and wish to help [create a version of LangTrans](https://forms.gle/YDEKapaTZmJspyDeA) for it, please feel free to start. We'd greatly appreciate your expertise.

1. **Reporting Bugs**: If you encounter any bugs or issues, please open a new issue describing the bug, how you came across it, and any potential causes or solutions you have in mind.

1. **Feature Suggestions**: If you have any ideas for new features or improvements, we'd love to hear them. Please open an issue describing your suggestion in as much detail as possible.

1. **Code Contributions**: If you'd like to contribute code to fix bugs or add features, please fork and open a pull request. Ensure your code follows any style guidelines and include as much information as possible about your changes.

Before contributing, please make sure to check the existing issues and pull requests to avoid duplicating efforts. If you're new to open-source contribution and need guidance, don't hesitate to reach out.

## Support

If you need support with LangTrans, there are several ways we can assist you:

1. **GitHub Issues**: If you're experiencing a problem with LangTrans or want to suggest improvements or new features, you can open a new issue on our GitHub repository.

1. **Documentation**: You can find a wealth of information about how to use LangTrans, including detailed guides and examples, in our [Gitbook documentation](https://bijinregipanicker.gitbook.io/langtrans/).

1. **Community**: You can join our [Discord community](https://discord.gg/3nDwppur5S), where you can ask questions, share your ideas, and get help from other LangTrans users.
