## ml-to-scheme

A simple ML language, see grammar at https://github.com/thautwarm/ml-to-scheme/blob/master/yesml.rbnf .

Target racket.

In fact not very trivial due to the greatly reduced code, and more easy-to-write and powerful
pattern matching.

## Usage

After cloning this repo, how about installing dependencies and `ml2scm` executable in **10 seconds** ?

You might have suffered a lot from `npm` or other slow package managers.

```bash
git clone https://github.com/thautwarm/ml-to-scheme &&
pip install rbnf-rts                                &&
python setup.py install
```

And the usage is easy,
```bash
ml2scm <xxx.ml> <xxx.rkt>
racket xxx.rkt

# `mlscm xxx.ml` will execute the file directly.
```

## Grammar

### Do

In top level, you can execute expressions via the `do` syntax.

```ocaml
do println 1
```

### Let-Definition

In top level, you can define a variable in this way:

```ocaml
let x = 1
let add10 = fun x -> x `+` 10
```

### Open

It'll get mapped to racket's `require` syntax.

```ocaml
open racket/match
open "./utils"
```

maps to

```scheme
(require racket/match)
(require "./utils")
```

### Block Expression

Concatenate a list of expressions,  execute them in order and treat the last one
as return.

```ocaml

let x = print 1;
        print 2;
        3
```

### Let In Expression

`let ... and ... in ...` juxtaposes several independent local bindings,
and return the expression held after the token `in`.

`let rec ... and ... in` makes this series of local bindings able to mutually reference each other.

```ocaml
let f = fun x ->
    let rec f = fun x -> g x
    and g = fun y -> y + 1
    in f 2
```

### Bool Expression

```ocaml
true || false
a `equals?` b && c
```

### If, Lambda, Match

If:

```ocaml
if cond then
    true_clause
else
    false_clause
```

Lambda:
```ocaml
fn x -> x
fn x -> x end
fun x -> x
fun x -> x end
```

When there're syntactic conflicts, feel free to use `end` to resolve.

Match:
```ocaml
match x with
| [3, 4.0, "str", :symbol, _] -> ...
| [hd#tl] -> ...
| pattern when predicate ->
| as-pattern -> dosomewith(as-pattern)
| pat1 & pat2 & pat3 -> ...
| pat1 | pat2 | pat3 -> ...
```

The precedence of `&` is higher than `|`.

Still, feel free to add an `end` in the end of a match expression,
to resolve possible syntactic conflicts.


### Application

Things are not curried in fact.

`f 1` is a syntax sugar for `f(1)`.

You can define functions in this way:

```ocaml
let f = fun x1 -> fun x2 -> ...
```

By this, you can then use the function in the currying way `f 1 2 ...`.

### List Expression

There's no `Tuple`, due to the target language is racket.
Use lists as tuples will suffice you use cases.

Note that to construct a list with a head and a tail,
you can use `[hd1, hd2, hd3#tl]` or `cons(hd1, cons(hd2, cons(hd3, tl)))`.


Check test directory for more examples.
