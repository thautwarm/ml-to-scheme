let left = fn x -> [:left, x]
let right = fn x -> [:right, x]
let either? = fn x -> match x with
      | [:left | :right, _] -> true
      | _ -> false

let either2? = fn x -> match x with
      | [a, _] when member(a, [:left, :right]) -> true
      | _ -> false

do println (either? (right 1))
do println (either2? (right 1))
