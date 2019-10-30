from rbnf_rts.rts import Tokens, State, AST
from mltoscm.parser_wrap import parse
from mltoscm.trivial import Visitor, Emit

a = parse("""
let x = 1
open racket/match
let main = fn (x) ->
    match x with
    | 1 | 2 | 3 -> 50
    | _ -> 5
""")

assert isinstance(a, AST) and a.tag == "START"

emit = Emit()
asts = Visitor().feed(a.contents[1])
for each in asts:
    emit.emit(each)
    print()


a = parse("""
let add2 = fn (x) -> +(x,  2)

let main = fn () ->
    println 1;
    let x = add2 1
    in [*(2, x)#[1, 2]];
    [1#x]
    
""")

assert isinstance(a, AST) and a.tag == "START"

emit = Emit()
asts = Visitor().feed(a.contents[1])
for each in asts:
    emit.emit(each)
    print()



