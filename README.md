## ml-to-scheme

A simple ML language, see grammar at https://github.com/thautwarm/ml-to-scheme/blob/master/yesml.rbnf .

Target racket.

In fact not very trivial due to the greatly reduced code, and more easy-to-write and powerful
pattern matching.

## Usage

```
ml2scm <xxx.ml> <xxx.rkt>
racket xxx.rkt
```

##
```
do match [1, 2, 3] with
    | [1||tl] -> print tl
    | xs      -> print (length xs)

->

#lang racket
(require racket/match)
(match (list 1 2 3)
   [(list-rest 1 tl)
     (print tl)]
   [xs
     (print
       (length xs))])


let add2 = fn (x) -> +(x, 2)
let main = fn () ->
    let x = add2 1
    in *(2, x)

->

#lang racket
(require racket/match)
(define add2
   (lambda (x)
      (+ x 2)))
(define main
   (lambda ()
      (let [(x
  (add2 1))]
         (* 2 x))))
```