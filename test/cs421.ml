open "./artc-ast.rkt"
open "./utils.rkt"
open "./artc-semantic-domain.rkt"

let in-range? = fun (x, low, high) ->
	let low  = char->integer low in
	let high = char->integer high in
	let x    = char->integer x in
	low `<=` x && high `>=` x


let valid-var? = fun var ->
	let str = symbol->string var in
	if member(str, keywords) then false
	else
	let chars = string->list str in
	match chars with
	| [ch#tl] when in-range?(ch, 'a', 'z') ||
			       in-range?(ch, 'A', 'Z') ->
		let rec check = fn xs ->
			match xs with
			| [] -> true
			| [ch#xs] when
				in-range?(ch, 'a', 'z') ||
				in-range?(ch, 'A', 'Z') ||
				in-range?(ch, '0', '9')  -> check xs
			| _ -> false
		in check tl
	| _ -> false

let keywords = [
	"program", "block", "declare",
	"if", "while", "sprint", "boolean", "int",
	"true", "false",
	"+", "-", "*", "/", "@", "?", "<", ">", "=", "<=", ">=", "&", "%",
	":="
]

let mk-check-ctx = fun () -> cons(typemap-create(), state-create())

let ctx-type-of = fun (ctx, var) ->
	typemap-type-of(car ctx, var)

let ctx-decl = fun (ctx, var, ty) ->
	let tenv = typemap-add(car ctx, var, ty)
	and st   = state-add(cdr ctx, var) in
	cons(tenv, st)

let ctx-decl? = fun (ctx, var) ->
	typemap-contains(car ctx, var)

let ctx-init? = fun (ctx, var) ->
	not(state-get-value(cdr ctx, var) `member` [:undefined, :error])

let ctx-with-tenv = fun (ctx, tenv) ->
	cons(tenv, cdr ctx)

let ctx-with-vars = fun (ctx, vars) ->
	cons(car ctx, vars)

let ctx-tenv = fun ctx -> car ctx
let ctx-vars = fun ctx -> cdr ctx

let ctx-mutate = fun (ctx, var, val) ->
	if state-get-value(ctx-vars ctx, var) `equal?` :error
	then
		error(format("~a not declared", var))
	else
		ctx-with-vars(ctx, state-update(ctx-vars ctx, var, val))

let ctx-val-of = fun (ctx, var) ->
	state-get-value(cdr ctx, var)

let ctx-delete = fun (ctx, var) ->
	let tenv = typemap-delete(ctx-tenv ctx, var)
	and st   = state-delete(ctx-vars ctx, var) in
	cons(tenv, st)

let not-decl = fun x ->
	match x with
	| [:declare #_] -> false
	| _ -> true

let mk-expr = fun (val, ty) ->
	[:expr, val, ty]

let expr-type = fun expr ->
	match expr with
	| [:expr, _, ty] -> ty
	| _ -> error(format("expect an expression, got ~a", expr))

let expr-val = fun expr ->
	match expr with
	| [:expr, val, _] -> val
	| _ -> error(format("expect an expression, got ~a", expr))

let second = fun xs ->
	match xs with
	| [_, e#_] -> e
	| _ -> error("not inbound")


let forM = fun f -> fun ctx -> fun xs ->
	let rec apply = fun (xs, ctx) ->
		match xs with
		| [] -> [[], ctx]
		| [hd#tl] ->
		let hdM = f ctx hd in
		let tlM = apply(tl, second hdM) in
		[[car hdM # car tlM], second tlM]
	in apply(xs, ctx)

let forM_ = fun f -> fun ctx -> fun xs ->
	let rec apply = fun (xs, ctx) ->
		match xs with
		| [] -> ctx
		| [hd#tl] ->
		let hdM = f ctx hd in
		apply(tl, second hdM)
	in apply(xs, ctx)

let not-equal? = fun (a, b) -> not (a `equal?` b)

let interpret-program = fun prog ->
	let ctx = mk-check-ctx()
	and check = fun tag -> fun f -> fun x -> fun node ->
		match node with
		| [hd#_] when hd `equal?` tag -> f x node
		| _ -> error(format("expect a list that starts with ~a, got ~a", tag, x))
	in
	let rec interpret-expr =
		fun ctx ->
		fun node ->
		match node with
		| :true ->
			mk-expr(true, :boolean)
		| :false ->
			mk-expr(false, :boolean)
		| var when symbol? var ->
			if not (valid-var? var)
			then
				error(format("~a not a valid symbol", var))
			else
			if not (ctx-decl?(ctx, var))
			then
				error(format("~a not declared yet", var))
			else
			if not (ctx-init?(ctx, var))
			then
				error(format("~a not initialized yet", var))
			else
			let ty = ctx-type-of(ctx, var) in
			let val = ctx-val-of(ctx, var) in
			mk-expr(val, ty)
		| i when integer? i ->
			mk-expr(i, :int)
		| [op & (:+ | :- | :* | :/ | :@ | :?), a, b] ->
			let a = interpret-expr ctx a in
			let b = interpret-expr ctx b in
			let func = iii_func op in
			assert(expr-type a `equal?` :int, "lhs here must be int");
			assert(expr-type b `equal?` :int, "rhs here must be int");
			mk-expr(expr-val a `func` expr-val b, :int)
		| [op & (:< | :> | :(=) | :(<=) | :(>=)), a, b] ->
			let a = interpret-expr ctx a in
			let b = interpret-expr ctx b in
			let func = iib_func op in
			assert(expr-type a `equal?` :int, "lhs here must be int");
			assert(expr-type b `equal?` :int, "rhs here must be int");
			mk-expr(expr-val a `func` expr-val b, :boolean)
		| [op & (:& | :%), a, b] ->
			let a = interpret-expr ctx a in
			let b = interpret-expr ctx b in
			let func = bbb_func op in
			assert(expr-type a `equal?` :boolean, "lhs here must be boolean");
			assert(expr-type b `equal?` :boolean, "rhs here must be boolean");
			mk-expr(expr-val a `func` expr-val b, :boolean)
		| [:~, a] ->
			let a = interpret-expr ctx a in
			assert(expr-type a `equal?` :boolean, "operand here must be boolean");
			mk-expr(not (expr-val a), :boolean)
		| [:-, a] ->
			let a = interpret-expr ctx a in
			assert(expr-type a `equal?` :int, "operand here must be int");
			mk-expr(-(expr-val a), :int)

	in let rec interpret-stmt =
		fun ctx ->
		fun node ->
		match node with
		| [:program #tl] ->
			let decls = take-until(not-decl, tl)
			and blocks = drop-until(not-decl, tl) in
			match forM (check :declare interpret-stmt) ctx decls with
			| [entered-vars, ctx] ->
				let dups = check-duplicates entered-vars in
				if dups `not-equal?` false
				then
					error(format("redeclarations: ~a", dups))
				else
				if length blocks `not-equal?` 1
				then
					error(format(
						"expect only one block from a program, got ~a", length blocks))
				else
				check :block interpret-stmt ctx (car blocks)
			| _ -> error("malformed program")
			end
		| [:block #stmts] ->

			let decls = take-until(not-decl, stmts) in
			let bodies = drop-until(not-decl, stmts) in
			match forM (check :declare interpret-stmt) ctx decls with
			| [entered-vars, ctx] ->

				let interp-with-check = fun ctx -> fun node ->

					if list? node && car node `member`
						[:block, :(:=), :if, :while, :sprint]
					then
						interpret-stmt ctx node
					else
						error(format("expected a statement, got ~a", node))
				in
				let ctx = forM_ interp-with-check ctx bodies in
				let ctx = foldr(fun (o, ctx) -> ctx-delete(ctx, o), ctx, entered-vars) in
				[:ok, ctx]
			| _ ->  error("malformed program")
			end
		| [:declare, ty, var] ->
			if not (symbol? ty && symbol? var && valid-var? var)
			then
				error(format("malformed declare: ~a", node))
			else
			if not (member(ty, [:boolean, :int]))
			then
				error(format("unsupported type ~a", ty))
			else
			if (ctx-decl?(ctx, var))
			then
				error(format("redeclaration of variable ~a", var))
			else
			[var, ctx-decl(ctx, var, ty)]
		| [:(:=), var, exp] ->
			let exp = interpret-expr ctx exp             in
			let ctx = ctx-mutate(ctx, var, expr-val exp) in
			let expect-ty = ctx-type-of(ctx, var)
			and actual-ty = expr-type exp                in
			if not(actual-ty `equal?` expect-ty)
			then
				error(
					format(
						"expect type of ~a to be ~a, got ~a",
						var,
						expect-ty,
						actual-ty))
			else [:ok, ctx]
		| [:if, cond, tC] ->
			match interpret-expr ctx cond with
			| [:expr, true, :boolean] ->
				interpret-stmt ctx tC
			| [:expr, false, :boolean] ->
				[:ok, ctx]
			| [:expr, val, ty] ->
				error(format(
					"if conditional must be a boolean, got ~a, valued ~a", ty, val))
			| _ -> error("malformed if statement")
			end
		| [:if, cond, tC, fC] ->
			match interpret-expr ctx cond with
			| [:expr, true, :boolean] ->
				interpret-stmt ctx tC
			| [:expr, false, :boolean] ->
				interpret-stmt ctx fC
			| [:expr, val, ty] ->
				error(format(
					"if conditional must be a boolean, got ~a, valued ~a", ty, val))
			| _ -> error("malformed if statement")
			end
		| [:while, cond, clause] ->
			let rec loop = fn ctx ->
				match interpret-expr ctx cond with
				| [:expr, true, :boolean] ->
					let ctx = second(interpret-stmt ctx clause)
					in loop ctx
				| [:expr, false, :boolean] ->
					[:ok, ctx]
				| _ ->
					error("malformed while statement")
			in loop ctx
		| [:sprint, format] ->
			print(format);
			println(ctx-vars ctx);
			[:ok, ctx]
		| [:sprint, format, exp] ->
			let exp = interpret-expr ctx exp in
			print(format);
			println(expr-val exp);
			[:ok, ctx]

	in ctx-vars(second(interpret-stmt ctx prog))

let iii_func = fn op ->
	match op with
	| :+ -> +
	| :- -> -
	| :* -> *
	| :/ -> /
	| :@ -> expt
	| :? -> modulo


let iib_func = fn op ->
	match op with
	| :< -> <
	| :> -> >
	| :(=) -> equal?
	| :(<=) -> <=
	| :(>=) -> >=

let bbb_func = fn op ->
	match op with
	| :& -> fn (a, b) -> a && b
	| :% -> fn (a, b) -> a || b

let assert = fn (x, msg) ->
	match x with
	| true -> :ok
	| _    -> error(msg)
