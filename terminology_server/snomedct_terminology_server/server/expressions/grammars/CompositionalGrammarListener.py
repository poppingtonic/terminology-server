# Generated from CompositionalGrammar.g4 by ANTLR 4.5.3
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CompositionalGrammarParser import CompositionalGrammarParser
else:
    from CompositionalGrammarParser import CompositionalGrammarParser

# This class defines a complete listener for a parse tree produced by CompositionalGrammarParser.
class CompositionalGrammarListener(ParseTreeListener):

    # Enter a parse tree produced by CompositionalGrammarParser#expressionfile.
    def enterExpressionfile(self, ctx:CompositionalGrammarParser.ExpressionfileContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#expressionfile.
    def exitExpressionfile(self, ctx:CompositionalGrammarParser.ExpressionfileContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#expression.
    def enterExpression(self, ctx:CompositionalGrammarParser.ExpressionContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#expression.
    def exitExpression(self, ctx:CompositionalGrammarParser.ExpressionContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#subexpression.
    def enterSubexpression(self, ctx:CompositionalGrammarParser.SubexpressionContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#subexpression.
    def exitSubexpression(self, ctx:CompositionalGrammarParser.SubexpressionContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#definitionstatus.
    def enterDefinitionstatus(self, ctx:CompositionalGrammarParser.DefinitionstatusContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#definitionstatus.
    def exitDefinitionstatus(self, ctx:CompositionalGrammarParser.DefinitionstatusContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#equivalentto.
    def enterEquivalentto(self, ctx:CompositionalGrammarParser.EquivalenttoContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#equivalentto.
    def exitEquivalentto(self, ctx:CompositionalGrammarParser.EquivalenttoContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#subtypeof.
    def enterSubtypeof(self, ctx:CompositionalGrammarParser.SubtypeofContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#subtypeof.
    def exitSubtypeof(self, ctx:CompositionalGrammarParser.SubtypeofContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#focusconcept.
    def enterFocusconcept(self, ctx:CompositionalGrammarParser.FocusconceptContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#focusconcept.
    def exitFocusconcept(self, ctx:CompositionalGrammarParser.FocusconceptContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#conceptreference.
    def enterConceptreference(self, ctx:CompositionalGrammarParser.ConceptreferenceContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#conceptreference.
    def exitConceptreference(self, ctx:CompositionalGrammarParser.ConceptreferenceContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#conceptid.
    def enterConceptid(self, ctx:CompositionalGrammarParser.ConceptidContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#conceptid.
    def exitConceptid(self, ctx:CompositionalGrammarParser.ConceptidContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#term.
    def enterTerm(self, ctx:CompositionalGrammarParser.TermContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#term.
    def exitTerm(self, ctx:CompositionalGrammarParser.TermContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#refinement.
    def enterRefinement(self, ctx:CompositionalGrammarParser.RefinementContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#refinement.
    def exitRefinement(self, ctx:CompositionalGrammarParser.RefinementContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#attributegroup.
    def enterAttributegroup(self, ctx:CompositionalGrammarParser.AttributegroupContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#attributegroup.
    def exitAttributegroup(self, ctx:CompositionalGrammarParser.AttributegroupContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#attributeset.
    def enterAttributeset(self, ctx:CompositionalGrammarParser.AttributesetContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#attributeset.
    def exitAttributeset(self, ctx:CompositionalGrammarParser.AttributesetContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#attribute.
    def enterAttribute(self, ctx:CompositionalGrammarParser.AttributeContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#attribute.
    def exitAttribute(self, ctx:CompositionalGrammarParser.AttributeContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#attributename.
    def enterAttributename(self, ctx:CompositionalGrammarParser.AttributenameContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#attributename.
    def exitAttributename(self, ctx:CompositionalGrammarParser.AttributenameContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#attributevalue.
    def enterAttributevalue(self, ctx:CompositionalGrammarParser.AttributevalueContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#attributevalue.
    def exitAttributevalue(self, ctx:CompositionalGrammarParser.AttributevalueContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#expressionvalue.
    def enterExpressionvalue(self, ctx:CompositionalGrammarParser.ExpressionvalueContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#expressionvalue.
    def exitExpressionvalue(self, ctx:CompositionalGrammarParser.ExpressionvalueContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#stringvalue.
    def enterStringvalue(self, ctx:CompositionalGrammarParser.StringvalueContext):
        pass

    # Exit a parse tree produced by CompositionalGrammarParser#stringvalue.
    def exitStringvalue(self, ctx:CompositionalGrammarParser.StringvalueContext):
        pass


    # Enter a parse tree produced by CompositionalGrammarParser#numericvalue.
    def enterNumericvalue(self, ctx:CompositionalGrammarParser.NumericvalueContext):
        pass

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
        pass

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


