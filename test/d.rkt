#lang racket
(require racket/match)
(define left
   (lambda (x)
      (list 'left x)))
(define right
   (lambda (x)
      (list 'right x)))
(define either?
   (lambda (x)
      (match x
         [(list
  (or 'left 'right)
  _) true]
         [_ false])))
(define either2?
   (lambda (x)
      (match x
         [(list a _) #:when
            (member a
               (list 'left 'right))
            true]
         [_ false])))
(println
  (either?
    (right 1)))
(println
  (either2?
    (right 1)))
