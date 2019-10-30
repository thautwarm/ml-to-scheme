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
           _) #t]
         [_ #f])))
(define either2?
   (lambda (x)
      (match x
         [(list a _) #:when
            (member a
               (list 'left 'right))
            #t]
         [_ #f])))
(println
  (either?
    (right 1)))
(println
  (either2?
    (right 1)))
