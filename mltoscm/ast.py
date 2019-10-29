from enum import Enum, auto as _auto
import abc
import typing as t
from dataclasses import dataclass


class AST:
    pass


class Leaf(AST):
    pass


@dataclass(frozen=True, order=True)
class Ident(Leaf):
    ident:str
    colno:int
    lineno:int
    pass


@dataclass(frozen=True, order=True)
class Str(Leaf):
    str:str
    colno:int
    lineno:int
    pass


@dataclass(frozen=True, order=True)
class Num(Leaf):
    num:object
    colno:int
    lineno:int
    pass


class Stmt(AST):
    pass


class Exp(AST):
    pass


class Case(AST):
    pass


@dataclass(frozen=True, order=True)
class Top(AST):
    stmts:t.List[Stmt]
    pass


@dataclass(frozen=True, order=True)
class Let(Stmt):
    ident:Ident
    exp:Exp
    pass


@dataclass(frozen=True, order=True)
class OpenString(Stmt):
    path:Str
    pass


@dataclass(frozen=True, order=True)
class OpenId(Stmt):
    ident:Ident
    pass


@dataclass(frozen=True, order=True)
class Do(Stmt):
    exp:Exp
    pass


@dataclass(frozen=True, order=True)
class LetExp(Exp):
    stmt:Let
    exp:Exp
    pass


@dataclass(frozen=True, order=True)
class App(Exp):
    f:Exp
    args:t.List[Exp]
    pass


@dataclass(frozen=True, order=True)
class Lam(Exp):
    args:t.List[Ident]
    body:Exp
    pass


@dataclass(frozen=True, order=True)
class Match(Exp):
    on:Exp
    cases:t.List[t.Tuple[Case,
    Exp,
    Exp]]
    pass


@dataclass(frozen=True, order=True)
class BoolExpr(Exp):
    leaf:Num
    pass


@dataclass(frozen=True, order=True)
class SymExpr(Exp):
    leaf:Ident
    pass


@dataclass(frozen=True, order=True)
class ChrExpr(Exp):
    leaf:Str
    pass


@dataclass(frozen=True, order=True)
class NumExpr(Exp):
    leaf:Num
    pass


@dataclass(frozen=True, order=True)
class StrExpr(Exp):
    leaf:Str
    pass


@dataclass(frozen=True, order=True)
class List(Exp):
    elts:t.List[Exp]
    tl:t.Optional[Exp]
    pass


@dataclass(frozen=True, order=True)
class BoolCase(Case):
    leaf:Num
    pass


@dataclass(frozen=True, order=True)
class SymCase(Case):
    leaf:Ident
    pass


@dataclass(frozen=True, order=True)
class ChrCase(Case):
    leaf:Str
    pass


@dataclass(frozen=True, order=True)
class NumCase(Case):
    leaf:Num
    pass


@dataclass(frozen=True, order=True)
class StrCase(Case):
    leaf:Str
    pass


@dataclass(frozen=True, order=True)
class ListCase(Case):
    elts:t.List[Case]
    tl:t.Optional[Case]
    pass


@dataclass(frozen=True, order=True)
class AndCase(Case):
    cases:t.List[Case]
    pass


@dataclass(frozen=True, order=True)
class OrCase(Case):
    cases:t.List[Case]
    pass
