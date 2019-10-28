let add2 = fn (x) -> +(x, 2)

let main = fn () ->
    let x = add2 1
    in *(2, x)