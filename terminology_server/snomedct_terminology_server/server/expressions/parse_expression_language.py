from antlr4 import ParseTreeWalker, CommonTokenStream, InputStream
from .grammars.ECLPortLexer import ECLPortLexer
from .grammars.ECLPortParser import ECLPortParser
from .grammars.TestECLPortListener import TestECLPortListener
from .helpers import VerboseErrorListener


def constraint_language_sctids(expression):
    input_stream = InputStream(expression)
    lexer = ECLPortLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = ECLPortParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(VerboseErrorListener())
    tree = parser.expressionconstraint()

    listener = TestECLPortListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    return listener.get_sctid_list()
