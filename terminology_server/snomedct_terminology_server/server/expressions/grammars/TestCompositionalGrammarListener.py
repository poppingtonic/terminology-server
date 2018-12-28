# Generated from CompositionalGrammarPort.g4 by ANTLR 4.5.3
import os
from antlr4 import *
from .CompositionalGrammarParser import CompositionalGrammarParser
from ..helpers import verhoeff_digit
from snomedct_terminology_server.server.utils import as_bool

DEBUG_EXPRESSIONS = as_bool(os.environ.get('DEBUG_EXPRESSIONS', False))

# This class defines a complete listener for a parse tree produced by CompositionalGrammarParser.
class TestCompositionalGrammarListener(ParseTreeListener):
    def __init__(self):
        self.subexpression = {}

    # Enter a parse tree produced by CompositionalGrammarParser#expressionfile.
    def enterExpressionfile(self, ctx:CompositionalGrammarParser.ExpressionfileContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('\n[expression constraint] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#expressionfile.
    def exitExpressionfile(self, ctx:CompositionalGrammarParser.ExpressionfileContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#expression.
    def enterExpression(self, ctx:CompositionalGrammarParser.ExpressionContext):
        self.sctid_list = []
        if DEBUG_EXPRESSIONS:  # noqa
            print('\n\n****========== EXPRESSION ==========****\n')
            print('[expression] : ', ctx.getText(), '\n')

        definition_status = '==='
        subexpression_concept_reference = ctx.subexpression().focusconcept().conceptreference(0).conceptid().getText()
        if ctx.definitionstatus():
            definition_status = ctx.definitionstatus().getText()

            if DEBUG_EXPRESSIONS:  # noqa
                print('eval {} {}'.format(definition_status, subexpression_concept_reference))
        else:
            if DEBUG_EXPRESSIONS:  # noqa
                print('eval {}'.format(subexpression_concept_reference))
        # import pdb; pdb.set_trace()

    # Exit a parse tree produced by CompositionalGrammarParser#expression.
    def exitExpression(self, ctx:CompositionalGrammarParser.ExpressionContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('\n<<< sctid list: ', self.sctid_list, '\n')


    # Enter a parse tree produced by CompositionalGrammarParser#subexpression.
    def enterSubexpression(self, ctx:CompositionalGrammarParser.SubexpressionContext):
        self.subexpression['focus_concept'] = {}
        if DEBUG_EXPRESSIONS:  # noqa
            print('[subexpression] : ', ctx.getText(), '\n')
            if DEBUG_EXPRESSIONS:  # noqa
                print('[SE] focusconcept: ', ctx.focusconcept().getText(), '\n')
        concept_reference_array = ctx.focusconcept().conceptreference()
        ids = self.subexpression['focus_concept']['concept_ids'] = [concept.conceptid().getText()
                                                                    for concept
                                                                    in concept_reference_array]
        if len(concept_reference_array) == 2:
            if DEBUG_EXPRESSIONS:  # noqa
                print("\n>>>>[check] if these two: {} are in the same hierarchy\n\n".format(ids))
        elif len(concept_reference_array) == 1:
            if DEBUG_EXPRESSIONS:  # noqa
                print("only one id in this focusconcept: {} ".format(ids))
            # import pdb; pdb.set_trace()

    # Exit a parse tree produced by CompositionalGrammarParser#subexpression.
    def exitSubexpression(self, ctx:CompositionalGrammarParser.SubexpressionContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('\n\n')
            if DEBUG_EXPRESSIONS:  # noqa
                print(self.subexpression)
                if DEBUG_EXPRESSIONS:  # noqa
                    print('\n\n')


    # Enter a parse tree produced by CompositionalGrammarParser#definitionstatus.
    def enterDefinitionstatus(self, ctx:CompositionalGrammarParser.DefinitionstatusContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[definition status] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#definitionstatus.
    def exitDefinitionstatus(self, ctx:CompositionalGrammarParser.DefinitionstatusContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#equivalentto.
    def enterEquivalentto(self, ctx:CompositionalGrammarParser.EquivalenttoContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[equivalent to] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#equivalentto.
    def exitEquivalentto(self, ctx:CompositionalGrammarParser.EquivalenttoContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#subtypeof.
    def enterSubtypeof(self, ctx:CompositionalGrammarParser.SubtypeofContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[subtype of] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#subtypeof.
    def exitSubtypeof(self, ctx:CompositionalGrammarParser.SubtypeofContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#focusconcept.
    def enterFocusconcept(self, ctx:CompositionalGrammarParser.FocusconceptContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[focus concept] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#focusconcept.
    def exitFocusconcept(self, ctx:CompositionalGrammarParser.FocusconceptContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#conceptreference.
    def enterConceptreference(self, ctx:CompositionalGrammarParser.ConceptreferenceContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('\n[concept reference] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#conceptreference.
    def exitConceptreference(self, ctx:CompositionalGrammarParser.ConceptreferenceContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#conceptid.
    def enterConceptid(self, ctx:CompositionalGrammarParser.ConceptidContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[concept id] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#conceptid.
    def exitConceptid(self, ctx:CompositionalGrammarParser.ConceptidContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#term.
    def enterTerm(self, ctx:CompositionalGrammarParser.TermContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[term] : ', ctx.getText(), '\n')

    # Exit a parse tree produced by CompositionalGrammarParser#term.
    def exitTerm(self, ctx:CompositionalGrammarParser.TermContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#refinement.
    def enterRefinement(self, ctx:CompositionalGrammarParser.RefinementContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[refinement] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#refinement.
    def exitRefinement(self, ctx:CompositionalGrammarParser.RefinementContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#attributegroup.
    def enterAttributegroup(self, ctx:CompositionalGrammarParser.AttributegroupContext):
        # import pdb; pdb.set_trace()
        if DEBUG_EXPRESSIONS:  # noqa
            print('[attribute group] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#attributegroup.
    def exitAttributegroup(self, ctx:CompositionalGrammarParser.AttributegroupContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#attributeset.
    def enterAttributeset(self, ctx:CompositionalGrammarParser.AttributesetContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[attribute set] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#attributeset.
    def exitAttributeset(self, ctx:CompositionalGrammarParser.AttributesetContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#attribute.
    def enterAttribute(self, ctx:CompositionalGrammarParser.AttributeContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[attribute] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#attribute.
    def exitAttribute(self, ctx:CompositionalGrammarParser.AttributeContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#attributename.
    def enterAttributename(self, ctx:CompositionalGrammarParser.AttributenameContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[attribute name] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#attributename.
    def exitAttributename(self, ctx:CompositionalGrammarParser.AttributenameContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#attributevalue.
    def enterAttributevalue(self, ctx:CompositionalGrammarParser.AttributevalueContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[attribute value] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#attributevalue.
    def exitAttributevalue(self, ctx:CompositionalGrammarParser.AttributevalueContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#expressionvalue.
    def enterExpressionvalue(self, ctx:CompositionalGrammarParser.ExpressionvalueContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[expression value] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#expressionvalue.
    def exitExpressionvalue(self, ctx:CompositionalGrammarParser.ExpressionvalueContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#stringvalue.
    def enterStringvalue(self, ctx:CompositionalGrammarParser.StringvalueContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[string value] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#stringvalue.
    def exitStringvalue(self, ctx:CompositionalGrammarParser.StringvalueContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#numericvalue.
    def enterNumericvalue(self, ctx:CompositionalGrammarParser.NumericvalueContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[numeric value] : ', ctx.getText())

    # Exit a parse tree produced by CompositionalGrammarParser#numericvalue.
    def exitNumericvalue(self, ctx:CompositionalGrammarParser.NumericvalueContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#integervalue.
    def enterIntegervalue(self, ctx:CompositionalGrammarParser.IntegervalueContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#integervalue.
    def exitIntegervalue(self, ctx:CompositionalGrammarParser.IntegervalueContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#decimalvalue.
    def enterDecimalvalue(self, ctx:CompositionalGrammarParser.DecimalvalueContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#decimalvalue.
    def exitDecimalvalue(self, ctx:CompositionalGrammarParser.DecimalvalueContext):
        pass

    # Enter a parse tree produced by CompositionalGrammarParser#sctid.
    def enterSctid(self, ctx:CompositionalGrammarParser.SctidContext):
        sctid = ctx.getText()
        check_digit = sctid[-1]
        identifier = sctid[:-1]

        if verhoeff_digit(identifier) != check_digit:
            raise Exception(
                "The SNOMED Identifier has an invalid check digit")

        sctid_length = len(str(sctid))
        try:
            assert 6 <= sctid_length <= 18
        except AssertionError:
            raise Exception("SNOMED CT Identifiers should be between 6 and 18 characters long. The number you used: {}, is {} characters long. Please check your expression for correctness.".format(sctid, sctid_length))
        if DEBUG_EXPRESSIONS:  # noqa
            print('number matches sctId rule: {}'.format(ctx.getText()))
        self.sctid_list.append(sctid)

    # Exit a parse tree produced by CompositionalGrammarParser#sctid.
    def exitSctid(self, ctx:CompositionalGrammarParser.SctidContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#ws.
    def enterWs(self, ctx:CompositionalGrammarParser.WsContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#ws.
    def exitWs(self, ctx:CompositionalGrammarParser.WsContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#sp.
    def enterSp(self, ctx:CompositionalGrammarParser.SpContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#sp.
    def exitSp(self, ctx:CompositionalGrammarParser.SpContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#htab.
    def enterHtab(self, ctx:CompositionalGrammarParser.HtabContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#htab.
    def exitHtab(self, ctx:CompositionalGrammarParser.HtabContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#cr.
    def enterCr(self, ctx:CompositionalGrammarParser.CrContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#cr.
    def exitCr(self, ctx:CompositionalGrammarParser.CrContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#lf.
    def enterLf(self, ctx:CompositionalGrammarParser.LfContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#lf.
    def exitLf(self, ctx:CompositionalGrammarParser.LfContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#qm.
    def enterQm(self, ctx:CompositionalGrammarParser.QmContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#qm.
    def exitQm(self, ctx:CompositionalGrammarParser.QmContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#bs.
    def enterBs(self, ctx:CompositionalGrammarParser.BsContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#bs.
    def exitBs(self, ctx:CompositionalGrammarParser.BsContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#digit.
    def enterDigit(self, ctx:CompositionalGrammarParser.DigitContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#digit.
    def exitDigit(self, ctx:CompositionalGrammarParser.DigitContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#zero.
    def enterZero(self, ctx:CompositionalGrammarParser.ZeroContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#zero.
    def exitZero(self, ctx:CompositionalGrammarParser.ZeroContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#digitnonzero.
    def enterDigitnonzero(self, ctx:CompositionalGrammarParser.DigitnonzeroContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#digitnonzero.
    def exitDigitnonzero(self, ctx:CompositionalGrammarParser.DigitnonzeroContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#nonwsnonpipe.
    def enterNonwsnonpipe(self, ctx:CompositionalGrammarParser.NonwsnonpipeContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#nonwsnonpipe.
    def exitNonwsnonpipe(self, ctx:CompositionalGrammarParser.NonwsnonpipeContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#anynonescapedchar.
    def enterAnynonescapedchar(self, ctx:CompositionalGrammarParser.AnynonescapedcharContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#anynonescapedchar.
    def exitAnynonescapedchar(self, ctx:CompositionalGrammarParser.AnynonescapedcharContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#escapedchar.
    def enterEscapedchar(self, ctx:CompositionalGrammarParser.EscapedcharContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#escapedchar.
    def exitEscapedchar(self, ctx:CompositionalGrammarParser.EscapedcharContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#utf8_2.
    def enterUtf8_2(self, ctx:CompositionalGrammarParser.Utf8_2Context):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#utf8_2.
    def exitUtf8_2(self, ctx:CompositionalGrammarParser.Utf8_2Context):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#utf8_3.
    def enterUtf8_3(self, ctx:CompositionalGrammarParser.Utf8_3Context):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#utf8_3.
    def exitUtf8_3(self, ctx:CompositionalGrammarParser.Utf8_3Context):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#utf8_4.
    def enterUtf8_4(self, ctx:CompositionalGrammarParser.Utf8_4Context):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#utf8_4.
    def exitUtf8_4(self, ctx:CompositionalGrammarParser.Utf8_4Context):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#utf8_tail.
    def enterUtf8_tail(self, ctx:CompositionalGrammarParser.Utf8_tailContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#utf8_tail.
    def exitUtf8_tail(self, ctx:CompositionalGrammarParser.Utf8_tailContext):
        pass

    def get_sctid_list(self):
        return self.sctid_list
