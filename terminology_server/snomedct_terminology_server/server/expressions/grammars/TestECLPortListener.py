import os
from antlr4 import *
from .ECLPortParser import ECLPortParser
from snomedct_terminology_server.server.utils import as_bool

DEBUG_EXPRESSIONS = as_bool(os.environ.get('DEBUG_EXPRESSIONS', False))

# This class defines a complete listener for a parse tree produced by ECLPortParser.
class TestECLPortListener(ParseTreeListener):
    # Enter a parse tree produced by ECLPortParser#expressionconstraint.
    def enterExpressionconstraint(self, ctx:ECLPortParser.ExpressionconstraintContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print("\n\n****================= NEW EXPRESSION CONSTRAINT =================****")
            print('\n[expression constraint] : ', ctx.getText())
        self.sctid_list = []

    # Exit a parse tree produced by ECLPortParser#expressionconstraint.
    def exitExpressionconstraint(self, ctx:ECLPortParser.ExpressionconstraintContext):
        pass

    # Enter a parse tree produced by ECLPortParser#simpleexpressionconstraint.
    def enterSimpleexpressionconstraint(self, ctx:ECLPortParser.SimpleexpressionconstraintContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[simple expression constraint] : ', ctx.getText())
        # if '<<' in ctx.getText():
        #     import pdb; pdb.set_trace()

    # Exit a parse tree produced by ECLPortParser#simpleexpressionconstraint.
    def exitSimpleexpressionconstraint(self, ctx:ECLPortParser.SimpleexpressionconstraintContext):
        pass


    # Enter a parse tree produced by ECLPortParser#refinedexpressionconstraint.
    def enterRefinedexpressionconstraint(self, ctx:ECLPortParser.RefinedexpressionconstraintContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[refined expression constraint] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#refinedexpressionconstraint.
    def exitRefinedexpressionconstraint(self, ctx:ECLPortParser.RefinedexpressionconstraintContext):
        pass


    # Enter a parse tree produced by ECLPortParser#compoundexpressionconstraint.
    def enterCompoundexpressionconstraint(self, ctx:ECLPortParser.CompoundexpressionconstraintContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[compound expression constraint] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#compoundexpressionconstraint.
    def exitCompoundexpressionconstraint(self, ctx:ECLPortParser.CompoundexpressionconstraintContext):
        pass


    # Enter a parse tree produced by ECLPortParser#conjunctionexpressionconstraint.
    def enterConjunctionexpressionconstraint(self, ctx:ECLPortParser.ConjunctionexpressionconstraintContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[conjunction expression constraint] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#conjunctionexpressionconstraint.
    def exitConjunctionexpressionconstraint(self, ctx:ECLPortParser.ConjunctionexpressionconstraintContext):
        pass


    # Enter a parse tree produced by ECLPortParser#disjunctionexpressionconstraint.
    def enterDisjunctionexpressionconstraint(self, ctx:ECLPortParser.DisjunctionexpressionconstraintContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[disjunction expression constraint] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#disjunctionexpressionconstraint.
    def exitDisjunctionexpressionconstraint(self, ctx:ECLPortParser.DisjunctionexpressionconstraintContext):
        pass


    # Enter a parse tree produced by ECLPortParser#exclusionexpressionconstraint.
    def enterExclusionexpressionconstraint(self, ctx:ECLPortParser.ExclusionexpressionconstraintContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[exclusion expression constraint] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#exclusionexpressionconstraint.
    def exitExclusionexpressionconstraint(self, ctx:ECLPortParser.ExclusionexpressionconstraintContext):
        pass


    # Enter a parse tree produced by ECLPortParser#subexpressionconstraint.
    def enterSubexpressionconstraint(self, ctx:ECLPortParser.SubexpressionconstraintContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[subexpression constraint] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#subexpressionconstraint.
    def exitSubexpressionconstraint(self, ctx:ECLPortParser.SubexpressionconstraintContext):
        pass


    # Enter a parse tree produced by ECLPortParser#focusconcept.
    def enterFocusconcept(self, ctx:ECLPortParser.FocusconceptContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[focus concept] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#focusconcept.
    def exitFocusconcept(self, ctx:ECLPortParser.FocusconceptContext):
        pass


    # Enter a parse tree produced by ECLPortParser#memberof.
    def enterMemberof(self, ctx:ECLPortParser.MemberofContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[member of] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#memberof.
    def exitMemberof(self, ctx:ECLPortParser.MemberofContext):
        pass


    # Enter a parse tree produced by ECLPortParser#conceptreference.
    def enterConceptreference(self, ctx:ECLPortParser.ConceptreferenceContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[concept reference] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#conceptreference.
    def exitConceptreference(self, ctx:ECLPortParser.ConceptreferenceContext):
        pass


    # Enter a parse tree produced by ECLPortParser#conceptid.
    def enterConceptid(self, ctx:ECLPortParser.ConceptidContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[concept id] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#conceptid.
    def exitConceptid(self, ctx:ECLPortParser.ConceptidContext):
        pass


    # Enter a parse tree produced by ECLPortParser#term.
    def enterTerm(self, ctx:ECLPortParser.TermContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[term] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#term.
    def exitTerm(self, ctx:ECLPortParser.TermContext):
        pass


    # Enter a parse tree produced by ECLPortParser#wildcard.
    def enterWildcard(self, ctx:ECLPortParser.WildcardContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[wildcard] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#wildcard.
    def exitWildcard(self, ctx:ECLPortParser.WildcardContext):
        pass


    # Enter a parse tree produced by ECLPortParser#constraintoperator.
    def enterConstraintoperator(self, ctx:ECLPortParser.ConstraintoperatorContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[constraint operator] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#constraintoperator.
    def exitConstraintoperator(self, ctx:ECLPortParser.ConstraintoperatorContext):
        pass


    # Enter a parse tree produced by ECLPortParser#descendantof.
    def enterDescendantof(self, ctx:ECLPortParser.DescendantofContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[descendant of] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#descendantof.
    def exitDescendantof(self, ctx:ECLPortParser.DescendantofContext):
        pass


    # Enter a parse tree produced by ECLPortParser#descendantorselfof.
    def enterDescendantorselfof(self, ctx:ECLPortParser.DescendantorselfofContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[descendant or self] : ', ctx.getText())


    # Exit a parse tree produced by ECLPortParser#descendantorselfof.
    def exitDescendantorselfof(self, ctx:ECLPortParser.DescendantorselfofContext):
        pass


    # Enter a parse tree produced by ECLPortParser#ancestorof.
    def enterAncestorof(self, ctx:ECLPortParser.AncestorofContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[ancestor of] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#ancestorof.
    def exitAncestorof(self, ctx:ECLPortParser.AncestorofContext):
        pass


    # Enter a parse tree produced by ECLPortParser#ancestororselfof.
    def enterAncestororselfof(self, ctx:ECLPortParser.AncestororselfofContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[ancestor or self] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#ancestororselfof.
    def exitAncestororselfof(self, ctx:ECLPortParser.AncestororselfofContext):
        pass


    # Enter a parse tree produced by ECLPortParser#conjunction.
    def enterConjunction(self, ctx:ECLPortParser.ConjunctionContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[conjunction] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#conjunction.
    def exitConjunction(self, ctx:ECLPortParser.ConjunctionContext):
        pass


    # Enter a parse tree produced by ECLPortParser#disjunction.
    def enterDisjunction(self, ctx:ECLPortParser.DisjunctionContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[disjunction] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#disjunction.
    def exitDisjunction(self, ctx:ECLPortParser.DisjunctionContext):
        pass


    # Enter a parse tree produced by ECLPortParser#exclusion.
    def enterExclusion(self, ctx:ECLPortParser.ExclusionContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[disjunction] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#exclusion.
    def exitExclusion(self, ctx:ECLPortParser.ExclusionContext):
        pass


    # Enter a parse tree produced by ECLPortParser#refinement.
    def enterRefinement(self, ctx:ECLPortParser.RefinementContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('refinement: ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#refinement.
    def exitRefinement(self, ctx:ECLPortParser.RefinementContext):
        pass


    # Enter a parse tree produced by ECLPortParser#conjunctionrefinementset.
    def enterConjunctionrefinementset(self, ctx:ECLPortParser.ConjunctionrefinementsetContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[conjunction refinement set] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#conjunctionrefinementset.
    def exitConjunctionrefinementset(self, ctx:ECLPortParser.ConjunctionrefinementsetContext):
        pass


    # Enter a parse tree produced by ECLPortParser#disjunctionrefinementset.
    def enterDisjunctionrefinementset(self, ctx:ECLPortParser.DisjunctionrefinementsetContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[disjunction refinement set] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#disjunctionrefinementset.
    def exitDisjunctionrefinementset(self, ctx:ECLPortParser.DisjunctionrefinementsetContext):
        pass


    # Enter a parse tree produced by ECLPortParser#subrefinement.
    def enterSubrefinement(self, ctx:ECLPortParser.SubrefinementContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[subrefinement] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#subrefinement.
    def exitSubrefinement(self, ctx:ECLPortParser.SubrefinementContext):
        pass


    # Enter a parse tree produced by ECLPortParser#attributeset.
    def enterAttributeset(self, ctx:ECLPortParser.AttributesetContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[attribute set] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#attributeset.
    def exitAttributeset(self, ctx:ECLPortParser.AttributesetContext):
        pass


    # Enter a parse tree produced by ECLPortParser#conjunctionattributeset.
    def enterConjunctionattributeset(self, ctx:ECLPortParser.ConjunctionattributesetContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[conjunction attribute set] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#conjunctionattributeset.
    def exitConjunctionattributeset(self, ctx:ECLPortParser.ConjunctionattributesetContext):
        pass


    # Enter a parse tree produced by ECLPortParser#disjunctionattributeset.
    def enterDisjunctionattributeset(self, ctx:ECLPortParser.DisjunctionattributesetContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[disjunction attribute set] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#disjunctionattributeset.
    def exitDisjunctionattributeset(self, ctx:ECLPortParser.DisjunctionattributesetContext):
        pass


    # Enter a parse tree produced by ECLPortParser#subattributeset.
    def enterSubattributeset(self, ctx:ECLPortParser.SubattributesetContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[sub attribute set] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#subattributeset.
    def exitSubattributeset(self, ctx:ECLPortParser.SubattributesetContext):
        pass


    # Enter a parse tree produced by ECLPortParser#attributegroup.
    def enterAttributegroup(self, ctx:ECLPortParser.AttributegroupContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[attribute group] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#attributegroup.
    def exitAttributegroup(self, ctx:ECLPortParser.AttributegroupContext):
        pass


    # Enter a parse tree produced by ECLPortParser#attribute.
    def enterAttribute(self, ctx:ECLPortParser.AttributeContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[attribute] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#attribute.
    def exitAttribute(self, ctx:ECLPortParser.AttributeContext):
        pass


    # Enter a parse tree produced by ECLPortParser#cardinality.
    def enterCardinality(self, ctx:ECLPortParser.CardinalityContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[cardinality] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#cardinality.
    def exitCardinality(self, ctx:ECLPortParser.CardinalityContext):
        pass


    # Enter a parse tree produced by ECLPortParser#to.
    def enterTo(self, ctx:ECLPortParser.ToContext):
        pass

    # Exit a parse tree produced by ECLPortParser#to.
    def exitTo(self, ctx:ECLPortParser.ToContext):
        pass

    # Enter a parse tree produced by ECLPortParser#many.
    def enterMany(self, ctx:ECLPortParser.ManyContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[many] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#many.
    def exitMany(self, ctx:ECLPortParser.ManyContext):
        pass


    # Enter a parse tree produced by ECLPortParser#reverseflag.
    def enterReverseflag(self, ctx:ECLPortParser.ReverseflagContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[reverse flag] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#reverseflag.
    def exitReverseflag(self, ctx:ECLPortParser.ReverseflagContext):
        pass


    # Enter a parse tree produced by ECLPortParser#attributeoperator.
    def enterAttributeoperator(self, ctx:ECLPortParser.AttributeoperatorContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[attribute operator]: ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#attributeoperator.
    def exitAttributeoperator(self, ctx:ECLPortParser.AttributeoperatorContext):
        pass


    # Enter a parse tree produced by ECLPortParser#attributename.
    def enterAttributename(self, ctx:ECLPortParser.AttributenameContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[attribute name]: ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#attributename.
    def exitAttributename(self, ctx:ECLPortParser.AttributenameContext):
        pass


    # Enter a parse tree produced by ECLPortParser#expressionconstraintvalue.
    def enterExpressionconstraintvalue(self, ctx:ECLPortParser.ExpressionconstraintvalueContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[expression constraint value]: ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#expressionconstraintvalue.
    def exitExpressionconstraintvalue(self, ctx:ECLPortParser.ExpressionconstraintvalueContext):
        pass


    # Enter a parse tree produced by ECLPortParser#expressioncomparisonoperator.
    def enterExpressioncomparisonoperator(self, ctx:ECLPortParser.ExpressioncomparisonoperatorContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[expression comparison operator] : ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#expressioncomparisonoperator.
    def exitExpressioncomparisonoperator(self, ctx:ECLPortParser.ExpressioncomparisonoperatorContext):
        pass


    # Enter a parse tree produced by ECLPortParser#numericcomparisonoperator.
    def enterNumericcomparisonoperator(self, ctx:ECLPortParser.NumericcomparisonoperatorContext):
        pass

    # Exit a parse tree produced by ECLPortParser#numericcomparisonoperator.
    def exitNumericcomparisonoperator(self, ctx:ECLPortParser.NumericcomparisonoperatorContext):
        pass


    # Enter a parse tree produced by ECLPortParser#stringcomparisonoperator.
    def enterStringcomparisonoperator(self, ctx:ECLPortParser.StringcomparisonoperatorContext):
        pass

    # Exit a parse tree produced by ECLPortParser#stringcomparisonoperator.
    def exitStringcomparisonoperator(self, ctx:ECLPortParser.StringcomparisonoperatorContext):
        pass


    # Enter a parse tree produced by ECLPortParser#numericvalue.
    def enterNumericvalue(self, ctx:ECLPortParser.NumericvalueContext):
        if DEBUG_EXPRESSIONS:  # noqa
            print('[numeric value]: ', ctx.getText())

    # Exit a parse tree produced by ECLPortParser#numericvalue.
    def exitNumericvalue(self, ctx:ECLPortParser.NumericvalueContext):
        pass


    # Enter a parse tree produced by ECLPortParser#stringvalue.
    def enterStringvalue(self, ctx:ECLPortParser.StringvalueContext):
        pass

    # Exit a parse tree produced by ECLPortParser#stringvalue.
    def exitStringvalue(self, ctx:ECLPortParser.StringvalueContext):
        pass


    # Enter a parse tree produced by ECLPortParser#integervalue.
    def enterIntegervalue(self, ctx:ECLPortParser.IntegervalueContext):
        pass

    # Exit a parse tree produced by ECLPortParser#integervalue.
    def exitIntegervalue(self, ctx:ECLPortParser.IntegervalueContext):
        pass


    # Enter a parse tree produced by ECLPortParser#decimalvalue.
    def enterDecimalvalue(self, ctx:ECLPortParser.DecimalvalueContext):
        pass

    # Exit a parse tree produced by ECLPortParser#decimalvalue.
    def exitDecimalvalue(self, ctx:ECLPortParser.DecimalvalueContext):
        pass


    # Enter a parse tree produced by ECLPortParser#nonnegativeintegervalue.
    def enterNonnegativeintegervalue(self, ctx:ECLPortParser.NonnegativeintegervalueContext):
        pass

    # Exit a parse tree produced by ECLPortParser#nonnegativeintegervalue.
    def exitNonnegativeintegervalue(self, ctx:ECLPortParser.NonnegativeintegervalueContext):
        pass


    # Enter a parse tree produced by ECLPortParser#sctid.
    def enterSctid(self, ctx:ECLPortParser.SctidContext):
        sctid = ctx.getText()
        sctid_length = len(str(sctid))
        try:
            assert 6 <= sctid_length <= 18
        except AssertionError:
            raise Exception("SNOMED CT Identifiers should be between 6 and 18 characters long. The number you used: {}, is {} characters long. Please check your expression for correctness.".format(sctid, sctid_length))
        if DEBUG_EXPRESSIONS:  # noqa
            print('number matches sctId rule: {}'.format(ctx.getText()), '\n')
        self.sctid_list.append(sctid)

    # Exit a parse tree produced by ECLPortParser#sctid.
    def exitSctid(self, ctx:ECLPortParser.SctidContext):
        pass


    # Enter a parse tree produced by ECLPortParser#ws.
    def enterWs(self, ctx:ECLPortParser.WsContext):
        pass

    # Exit a parse tree produced by ECLPortParser#ws.
    def exitWs(self, ctx:ECLPortParser.WsContext):
        pass


    # Enter a parse tree produced by ECLPortParser#mws.
    def enterMws(self, ctx:ECLPortParser.MwsContext):
        pass

    # Exit a parse tree produced by ECLPortParser#mws.
    def exitMws(self, ctx:ECLPortParser.MwsContext):
        pass


    # Enter a parse tree produced by ECLPortParser#sp.
    def enterSp(self, ctx:ECLPortParser.SpContext):
        pass

    # Exit a parse tree produced by ECLPortParser#sp.
    def exitSp(self, ctx:ECLPortParser.SpContext):
        pass


    # Enter a parse tree produced by ECLPortParser#htab.
    def enterHtab(self, ctx:ECLPortParser.HtabContext):
        pass

    # Exit a parse tree produced by ECLPortParser#htab.
    def exitHtab(self, ctx:ECLPortParser.HtabContext):
        pass


    # Enter a parse tree produced by ECLPortParser#cr.
    def enterCr(self, ctx:ECLPortParser.CrContext):
        pass

    # Exit a parse tree produced by ECLPortParser#cr.
    def exitCr(self, ctx:ECLPortParser.CrContext):
        pass


    # Enter a parse tree produced by ECLPortParser#lf.
    def enterLf(self, ctx:ECLPortParser.LfContext):
        pass

    # Exit a parse tree produced by ECLPortParser#lf.
    def exitLf(self, ctx:ECLPortParser.LfContext):
        pass


    # Enter a parse tree produced by ECLPortParser#qm.
    def enterQm(self, ctx:ECLPortParser.QmContext):
        pass

    # Exit a parse tree produced by ECLPortParser#qm.
    def exitQm(self, ctx:ECLPortParser.QmContext):
        pass


    # Enter a parse tree produced by ECLPortParser#bs.
    def enterBs(self, ctx:ECLPortParser.BsContext):
        pass

    # Exit a parse tree produced by ECLPortParser#bs.
    def exitBs(self, ctx:ECLPortParser.BsContext):
        pass


    # Enter a parse tree produced by ECLPortParser#digit.
    def enterDigit(self, ctx:ECLPortParser.DigitContext):
        pass

    # Exit a parse tree produced by ECLPortParser#digit.
    def exitDigit(self, ctx:ECLPortParser.DigitContext):
        pass


    # Enter a parse tree produced by ECLPortParser#zero.
    def enterZero(self, ctx:ECLPortParser.ZeroContext):
        pass

    # Exit a parse tree produced by ECLPortParser#zero.
    def exitZero(self, ctx:ECLPortParser.ZeroContext):
        pass


    # Enter a parse tree produced by ECLPortParser#digitnonzero.
    def enterDigitnonzero(self, ctx:ECLPortParser.DigitnonzeroContext):
        pass

    # Exit a parse tree produced by ECLPortParser#digitnonzero.
    def exitDigitnonzero(self, ctx:ECLPortParser.DigitnonzeroContext):
        pass


    # Enter a parse tree produced by ECLPortParser#nonwsnonpipe.
    def enterNonwsnonpipe(self, ctx:ECLPortParser.NonwsnonpipeContext):
        pass

    # Exit a parse tree produced by ECLPortParser#nonwsnonpipe.
    def exitNonwsnonpipe(self, ctx:ECLPortParser.NonwsnonpipeContext):
        pass


    # Enter a parse tree produced by ECLPortParser#anynonescapedchar.
    def enterAnynonescapedchar(self, ctx:ECLPortParser.AnynonescapedcharContext):
        pass

    # Exit a parse tree produced by ECLPortParser#anynonescapedchar.
    def exitAnynonescapedchar(self, ctx:ECLPortParser.AnynonescapedcharContext):
        pass


    # Enter a parse tree produced by ECLPortParser#escapedchar.
    def enterEscapedchar(self, ctx:ECLPortParser.EscapedcharContext):
        pass

    # Exit a parse tree produced by ECLPortParser#escapedchar.
    def exitEscapedchar(self, ctx:ECLPortParser.EscapedcharContext):
        pass


    # Enter a parse tree produced by ECLPortParser#utf8_2.
    def enterUtf8_2(self, ctx:ECLPortParser.Utf8_2Context):
        pass

    # Exit a parse tree produced by ECLPortParser#utf8_2.
    def exitUtf8_2(self, ctx:ECLPortParser.Utf8_2Context):
        pass


    # Enter a parse tree produced by ECLPortParser#utf8_3.
    def enterUtf8_3(self, ctx:ECLPortParser.Utf8_3Context):
        pass

    # Exit a parse tree produced by ECLPortParser#utf8_3.
    def exitUtf8_3(self, ctx:ECLPortParser.Utf8_3Context):
        pass


    # Enter a parse tree produced by ECLPortParser#utf8_4.
    def enterUtf8_4(self, ctx:ECLPortParser.Utf8_4Context):
        pass

    # Exit a parse tree produced by ECLPortParser#utf8_4.
    def exitUtf8_4(self, ctx:ECLPortParser.Utf8_4Context):
        pass


    # Enter a parse tree produced by ECLPortParser#utf8_tail.
    def enterUtf8_tail(self, ctx:ECLPortParser.Utf8_tailContext):
        pass

    # Exit a parse tree produced by ECLPortParser#utf8_tail.
    def exitUtf8_tail(self, ctx:ECLPortParser.Utf8_tailContext):
        pass

    def get_sctid_list(self):
        return self.sctid_list
