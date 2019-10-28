#lang racket
(require racket/match)
(match (list 1 2 3)
   [(list-rest 1 tl)
     (print tl)]
   [xs
     (print
       (length xs))])
