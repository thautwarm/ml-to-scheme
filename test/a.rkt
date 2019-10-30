#lang racket
(require racket/match)
(define add2
   (lambda (x)
      (+ x 2)))
(define main
   (lambda ()
      (let [[x
         (add2 1)]]
         (* 2 x))))
