from antlr4 import ParseTreeWalker, InputStream, CommonTokenStream
from .grammars.CompositionalGrammarLexer import CompositionalGrammarLexer
from .grammars.CompositionalGrammarParser import CompositionalGrammarParser
from .grammars.TestCompositionalGrammarListener import TestCompositionalGrammarListener
from .helpers import VerboseErrorListener


def compositional_grammar_sctids(expression):
    input_stream = InputStream(expression)
    lexer = CompositionalGrammarLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = CompositionalGrammarParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(VerboseErrorListener())
    tree = parser.expression()

    listener = TestCompositionalGrammarListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    return listener.get_sctid_list()
