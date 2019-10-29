
do match [1, 2, 3] with
    | [1||tl] -> print tl
    | xs      -> print (length xs)