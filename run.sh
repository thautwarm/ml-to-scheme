for a in "a" "b" "c" "d" "e" "f"
do
  ml2scm test/$a.ml test/$a.rkt && racket test/$a.rkt
done