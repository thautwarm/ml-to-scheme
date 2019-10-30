from mltoscm.parser import *
from mltoscm import parsing_required
from rbnf_rts.rts import Tokens, State, AST
from typing import Union, Tuple, List
from typing_extensions import Literal
import re

__all__ = ['parse']
_code = mk_parser.__code__
argnames = _code.co_varnames[:_code.co_argcount]
_parse = mk_parser(**{arg: getattr(parsing_required, arg) for arg in argnames})

Errors = Tuple[Literal[False], List[Tuple[int, str]]]
Parsed = Tuple[Literal[True], AST]

comment = re.compile(r"//[^\n]*")


def parse(text: str, filename: str = "unknown") -> Union[Parsed, Errors]:
    text = comment.sub("", text)
    tokens = list(run_lexer(filename, text))
    # for e in tokens:
    #     print(e)
    res = _parse(State(), Tokens(tokens))
    if res[0]:
        return res[1]
    msgs = []
    for each in res[1]:
        i, msg = each
        token = tokens[i]
        lineno = token.lineno
        colno = token.colno
        msgs.append(f"Line {lineno}, column {colno}, {msg}")
    raise SyntaxError(f"Filename {filename}:\n" + "\n".join(msgs))
