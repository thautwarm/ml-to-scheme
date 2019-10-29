
let left = fn x -> [:left, x]
let right = fn x -> [:right, x]
let either? = fn x -> match x with
      | [a, _] when member(a, [:left, :right]) -> 
