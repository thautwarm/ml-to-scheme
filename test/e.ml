let f =
    let rec g = fn x ->
        match x with
        | 0 -> 1
        | x ->
            let v = -(x, 1) in
            *(g v, x)
    in g

do println(f 10)