from mltoscm.ast import *
from types import FunctionType
from dataclasses import dataclass
from contextlib import contextmanager
import sys


@dataclass(order=True, frozen=True)
class Symbol:
    n: str

    def __repr__(self):
        return self.n


class _SymbolBuilder:
    def __getattr__(self, item):
        return Symbol(item)


sym = _SymbolBuilder()


def cls_dispatch(f):
    dispatch = {}

    def base(actual_self, arg):
        func = dispatch.get(type(arg), f)
        return func(actual_self, arg)

    def register(f: FunctionType):
        arg = f.__code__.co_varnames[1]
        dispatch[f.__annotations__[arg]] = f
        return None

    base.register = register
    return base


class Visitor:
    def __init__(self):
        pass

    def feed(self, n: Top):
        return list(map(self.the_stmt, n.stmts))

    @cls_dispatch
    def the_stmt(self, n: Stmt):
        raise NotImplementedError

    @cls_dispatch
    def the_exp(self, n: Exp):
        raise NotImplementedError

    @cls_dispatch
    def the_case(self, n: Case):
        raise NotImplementedError

    @the_stmt.register
    def the_let(self, let: Let):
        ident = let.ident
        exp = let.exp
        return sym.define, Symbol(ident.ident), self.the_exp(exp)

    @the_stmt.register
    def the_open(self, open_str: OpenString):
        return sym.require, open_str.path.str

    @the_stmt.register
    def the_open(self, open_dot: OpenId):
        return sym.require, Symbol(open_dot.ident.ident)

    @the_stmt.register
    def the_do(self, do: Do):
        return self.the_exp(do.exp)

    @the_exp.register
    def the_let_exp(self, let_exp: LetExp):
        ident = let_exp.stmt.ident
        bound = let_exp.stmt.exp
        block = let_exp.exp
        return sym.let, [(Symbol(ident.ident), self.the_exp(bound))
                         ], self.the_exp(block)

    @the_exp.register
    def the_app(self, app: App):
        f = self.the_exp(app.f)
        args = map(self.the_exp, app.args)
        return (f, *args)

    @the_exp.register
    def the_lam(self, lam: Lam):
        args = tuple(Symbol(arg.ident) for arg in lam.args)
        return Symbol("lambda"), args, self.the_exp(lam.body)

    @the_exp.register
    def the_match(self, match: Match):
        exp = self.the_exp(match.on)

        def mk_case(case: Case, guard: Exp, body: Exp):
            case = self.the_case(case)
            body = self.the_exp(body)
            if guard is None:
                return [case, body]
            return [case, Symbol("#:when"), self.the_exp(guard), body]

        cases = [
            mk_case(case, guard, body) for (case, guard, body) in match.cases
        ]
        return (sym.match, exp, *cases)

    @the_exp.register
    def the_bool(self, n: BoolExpr):
        if n.leaf.num:
            return Symbol("#t")
        return Symbol("#f")

    @the_exp.register
    def the_sym(self, n: SymExpr):
        return Symbol(r"'{}".format(n.leaf.ident))

    @the_exp.register
    def the_chr(self, n: ChrExpr):
        return Symbol(r"#\{}".format(n.leaf.str))

    @the_exp.register
    def the_str(self, n: StrExpr):
        return n.leaf.str

    @the_exp.register
    def the_num(self, n: NumExpr):
        return n.leaf.num

    @the_exp.register
    def the_var(self, v: Ident):
        return Symbol(v.ident)

    @the_exp.register
    def the_list(self, n: List):
        base = (sym.list, *map(self.the_exp, n.elts))
        if n.tl is None:
            return base
        return sym.cons, base, self.the_exp(n.tl)

    @the_case.register
    def the_or(self, n: OrCase):
        return (Symbol("or"), *map(self.the_case, n.cases))

    @the_case.register
    def the_and(self, n: AndCase):
        return (Symbol("and"), *map(self.the_case, n.cases))

    @the_case.register
    def the_bool(self, n: BoolCase):
        if n.leaf.num:
            return Symbol("#t")
        return Symbol("#f")

    @the_case.register
    def the_sym(self, n: SymCase):
        return Symbol(r"'{}".format(n.leaf.ident))

    @the_case.register
    def the_chr(self, n: ChrCase):
        return Symbol(r"#\{}".format(n.leaf.str))

    @the_case.register
    def the_str(self, n: StrCase):
        return n.leaf.str

    @the_case.register
    def the_num(self, n: NumCase):
        return n.leaf.num

    @the_case.register
    def the_capture(self, n: Ident):
        return Symbol(n.ident)

    @the_case.register
    def the_list_case(self, n: ListCase):
        elts = map(self.the_case, n.elts)
        tl = n.tl

        if tl is None:
            return (sym.list, *elts)

        return (Symbol("list-rest"), *elts, self.the_case(tl))


indent_tokens = {"match", "if", "let", "define", "lambda"}


@contextmanager
def no_indent(self: 'Emit'):
    ind = self.indent
    self.indent = 0
    try:
        yield
    finally:
        self.indent = ind


class Emit:
    def __init__(self, io=None):
        self.indent = 0
        self.io = (io or sys.stdout).write

    @cls_dispatch
    def emit(self, n):
        self.io(' ' * self.indent)
        if isinstance(n, str):
            self.io('"' + n.replace('"', '\\"') + '"')
            return
        self.io(repr(n))

    def emit_seq(self, n):
        if not n:
            return
        hd, *tl = n
        with no_indent(self):
            self.emit(hd)
        if tl and (isinstance(tl[0], (Symbol, int, str))
                   or isinstance(hd, Symbol) and hd.n in indent_tokens):
            self.io(" ")
            self.indent += 1
            self.emit_seq(tl)
            self.indent -= 1
            return
        ind = self.indent
        self.indent += 2
        for each in tl:
            self.io('\n')
            self.emit(each)
        self.indent = ind

    @emit.register
    def emit_tp(self, n: tuple):
        self.io(' ' * self.indent)
        self.io("(")
        self.emit_seq(n)
        self.io(")")

    @emit.register
    def emit_lst(self, n: list):
        self.io(' ' * self.indent)
        self.io("[")
        self.emit_seq(n)
        self.io("]")
