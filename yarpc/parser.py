from enum import Enum
from typing import Union

import ply.lex as lex
import ply.yacc as yacc


class SyntaxError(Exception):
    def __init__(self, text: str):
        self.text = text


class Action(Enum):
    CONNECT = "REQUEST"
    PING = "PING"
    INFO = "INFO"
    REQUEST = "REQUEST"
    RESPOND = "RESPOND"


class Query:
    def __init__(
        self,
        action: Action,
        parameter: str = None,
        destination: Union[int, str] = "ALL",
    ):
        self.action = action
        self.parameter = parameter
        if parameter:
            self.clean_parameter = parameter.replace("'", "\\'")
        self.destination = destination

    @property
    def has_parameter(self) -> bool:
        return self.parameter is not None

    def __str__(self) -> str:
        if not self.has_parameter:
            return f"{self.action};"
        else:
            return f"{self.action} '{self.clean_parameter}' TO {self.destination};"


tokens = (
    "SEMICOLON",
    "ALL",
    "TO",
    "STRING",
    "INTEGER",
    "PING",
    "INFO",
    "REQUEST",
    "RESPOND",
    "CONNECT",
)

# very basic integers
t_INTEGER = r"\d+"

# our actions
t_PING = r"PING"
t_INFO = r"INFO"
t_REQUEST = r"REQUEST|REQ"
t_RESPOND = r"RESPOND|RESP"
t_CONNECT = r"CONNECT|CONN"

t_SEMICOLON = r";"
t_TO = r"TO|FROM"
t_ALL = r"ALL"
t_ignore_WS = r"\s+"


def t_STRING(t: lex.LexToken) -> lex.LexToken:
    r'("(?:\\"|.)*?"|\'(?:\\\'|.)*?\')'

    # make multiple quotes possible like this
    t.value = t.value[1:-1]
    t.value = bytes(t.value, "utf-8").decode("unicode_escape")

    return t


def t_error(t: lex.LexToken) -> None:
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lex.lex(optimize=1)


def p_query(p: yacc.YaccProduction) -> None:
    """
    query : action_noargs SEMICOLON
          | action_args STRING SEMICOLON
          | action_args STRING TO destination SEMICOLON
    """
    nargs = len(p) - 2  # minus [0] and ;
    if nargs == 1:  # action_noargs
        p[0] = Query(action=p[1])
    elif nargs == 2:  # action_args STRING
        p[0] = Query(action=p[1], parameter=p[2])
    elif nargs == 4:  # action_args STRING TO destination
        p[0] = Query(action=p[1], parameter=p[2], destination=p[4])


# def p_action(p):
#    """
#    action : PING
#           | INFO
#           | REQUEST
#           | RESPOND
#           | CONNECT
#    """
#    p[0] = p[1]


def p_action_no_args(p: yacc.YaccProduction) -> None:
    """
    action_noargs : PING
                  | INFO
                  | CONNECT
    """
    p[0] = p[1]


def p_action_args(p: yacc.YaccProduction) -> None:
    """
    action_args : REQUEST
                | RESPOND
    """
    p[0] = p[1]


def p_destination(p: yacc.YaccProduction) -> None:
    """
    destination : INTEGER
                | ALL
    """
    p[0] = p[1]


def p_error(p: yacc.YaccProduction) -> None:
    if not p:  # missing ;
        raise SyntaxError("Missing ; after query")
    raise SyntaxError("Syntax error at '%s'" % p.value)


parser = yacc.yacc()

if __name__ == "__main__":
    while True:
        try:
            s = input("yarpc > ")
        except (EOFError, KeyboardInterrupt):
            break
        if not s:
            continue
        try:
            r = parser.parse(s)
        except SyntaxError as e:
            print(e.text)
        print(r)
