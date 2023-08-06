# Py_Trans

Customized python syntax

<table>

<thead>

<tr>

<th>Customized Syntax</th>

<th>Original Syntax</th>

</tr>

</thead>

<tbody>

<tr>

<td>

```py
p"Hello World"
```

</td>

<td>

```py
print("Hello World")
```

</td>

</tr>

<tr>

<td>

```py
inc = (x) => x+1
```

</td>

<td>

```py
inc = lambda x: x+1
```

</td>

</tr>

<tr>

<td>

```py
twice(x) = 2*x
add(x,y) = x+y
```

</td>

<td>

```py
twice = lambda x:2*x
add = lambda x,y:x+y
```

</td>

</tr>

<tr>

<td>

```py
1 -> inc
|> twice -> print
```

</td>

<td>

```py
print(twice(inc(1)))
```

</td>

</tr>

<tr>

<td>

```py
print<-inc<-twice<-1
```

</td>

<td>

```py
print(inc(twice(1)))
```

</td>

</tr>

<tr>

<td>

```py
try inc("1") Exception print("Error:",err)
```

</td>

<td>

```py
try:
  inc("1")
except Exception as err:
  print("Error:",err)
```

</td>

</tr>

<tr>

<td>

```py
print((x||True)?"Done":"Failed")
```

</td>

<td>

```py
print("Done" if (x if 'x' in locals() else True) else "Failed")
```

</td>

</tr>

<tr>

<td>

```py
print('x is not defined') if !x
```

</td>

<td>

```py
if 'x' not in locals():
   print('x is not defined')
```

</td>

</tr>

<tr>

<td>

```py
print((inc+twice)(3))
```

</td>

<td>

```py
print(inc(3)+twice(3))
```

</td>

</tr>

<tr>

<td>

```py
make type name(object):
    x = 1
    if x==1:
      pass
    y = 3

make dict test:
    this =  "this"
    if this == "this":
      pass
    that = "that"
```

</td>

<td>

```py
def name():
    x = 1
    if x==1:
      return locals()
    y = 3
    return locals()
name = type("name", (object,), name())

def test():
    this =  "this"
    if this == "this":
        return locals()
    that = "that"
    return locals()

test = test()
```

</td>

</tr>

<tr>

<td>

```py
#scope1#
print("Scope1")
print("Done")

#scope2#
print("Scope2")
print("Done")
```

</td>

<td>

```py
def scope1():
    print("Scope1")
    print("Done")
scope1()

def scope2():
    print("Scope2")
    print("Done")
scope2()
```

</td>

</tr>

</tbody>

</table>

Feel free to edit the syntax in your way.
