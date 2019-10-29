from builtins import list
from mltoscm import ast
from mltoscm.ast import *
from mltoscm.cst import Cons, nil, CST, Token

none = None
true = True
false = False


def _ToConst(tk: Token):
    return eval(tk.value)


def MKNum(tk: Token):
    return Num(eval(tk.value), tk.colno, tk.lineno)


def MKStr(tk: Token):
    return Str(eval(tk.value), tk.colno, tk.lineno)


def MKBool(tk: Token):
    return Num((False, True)[tk.value == "true"], tk.colno, tk.lineno)


def MKSym(tk: Token):
    val = tk.value
    if val.endswith(')'):
        val = val[2:-1]
    else:
        val = val[1:]
    return Ident(val, tk.colno, tk.lineno)


ToNum = ToStr = _ToConst


def MKAndCase(elts):
    if len(elts) == 1:
        return elts[0]
    return AndCase(elts)


def MKOrCase(elts):
    if len(elts) == 1:
        return elts[0]
    return OrCase(elts)


def MKIdent(tk: Token):
    return Ident(tk.value, tk.colno, tk.lineno)


def MKLRList(x: CST):
    """
    for nodes produced by
        A = [A] B
    , convert them to a sequence [B, B, ...]
    """
    res = []
    _len = len
    cs = x.contents
    while True:
        end = cs[-1]
        res.append(end)
        if _len(cs) is 1:
            break
        cs = cs[0].contents
    res.reverse()
    return res


def MKLRCommaList(x: CST):
    """
    for nodes produced by
        A = [A Comma] B
    , convert them to a sequence [B, B, ...]
    """
    res = []
    _len = len
    cs = x.contents
    while True:
        end = cs[-1]
        res.append(end)
        if _len(cs) is 1:
            break
        cs = cs[0][0].contents
    res.reverse()
    return res


Tuple0 = ()


def Tuple1(a):
    return a,


def Tuple2(a, b):
    return a, b


def Tuple3(a, b, c):
    return a, b, c
