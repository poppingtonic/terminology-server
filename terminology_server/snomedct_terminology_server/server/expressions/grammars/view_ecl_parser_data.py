import sys
from antlr4 import ParseTreeWalker, CommonTokenStream, FileStream, InputStream
from ECLPortLexer import ECLPortLexer
from ECLPortParser import ECLPortParser
from TestECLPortListener import TestECLPortListener
from helpers import VerboseErrorListener
from expressions import expressions


def validate_expression(input_stream):
    lexer = ECLPortLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = ECLPortParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(VerboseErrorListener())
    tree = parser.expressionconstraint()

    listener = TestECLPortListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    assert type(listener.get_sctid_list()) is list
    sctid_list = [int(sctid) for sctid in listener.get_sctid_list()]
    sctid_assert_template = "assert expression_sctids('{}') == {}".format(
        input_stream.strdata, listener.get_sctid_list())
    active_concepts_template = """assert len(Concept.objects.filter(id__in={}, \
active=true)) == len({})""".format(sctid_list, sctid_list)
    with open('test_expression_constraint_language.py', 'a') as f:
        f.write(sctid_assert_template + '\n' + active_concepts_template + '\n')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_stream = FileStream(sys.argv[1])
        validate_expression(input_stream)
    else:
        for expression in expressions:
            input_stream = InputStream(expression)
            validate_expression(input_stream)

        print(len(expressions))
