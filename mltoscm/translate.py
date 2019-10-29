from wisepy2 import wise
from mltoscm.parser_wrap import parse
from mltoscm.trivial import Visitor, Emit
import sys


def s2s(filename: str, out: str):
    with open(filename) as f:
        src = f.read()
    toplevel = parse(src).contents[1]
    stmts = Visitor().feed(toplevel)
    with open(out, 'w') as f:
        print("#lang racket", file=f)
        print("(require racket/match)", file=f)
        emit = Emit(io=f)
        for each in stmts:
            emit.emit(each)
            print(file=f)


def execute(filename: str):
    import tempfile
    from pathlib import Path
    from subprocess import check_call
    cur = Path(".").absolute()
    out = tempfile.mktemp(suffix='.rkt', dir=str(cur))
    try:
        s2s(filename, out)
        check_call(["racket", out])
    finally:
        Path(out).unlink()


def ml2scm():
    wise(s2s)(sys.argv[1:])


def mlscm():
    wise(execute)(sys.argv[1:])
