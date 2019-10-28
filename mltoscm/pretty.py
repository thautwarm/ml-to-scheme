from prettyprinter import pretty_call, register_pretty
from dataclasses import is_dataclass
from mltoscm import ast


def reg_dataclass(T):
    fields = list(T.__annotations__)
    t_name = T.__name__

    @register_pretty(T)
    def f(x, ctx):
        return pretty_call(ctx, t_name,
                           **{field: getattr(x, field)
                              for field in fields})


for _, each in ast.__dict__.items():
    if isinstance(each, type) and is_dataclass(each) and issubclass(
            each, ast.AST):
        reg_dataclass(each)
