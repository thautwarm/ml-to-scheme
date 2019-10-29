#lang racket
(require racket/match)
(define f
   (letrec
     [(g
  (lambda (x)
     (match x
        [0 1]
        [x
          (let [(v
  (- x 1))]
             (*
               (g v)
               x))])))]
     g))
(println
  (f 10))
