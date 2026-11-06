"""
Unit Tests for Stack Application: Expression Handling & Bracket Balancing
File: tests/test_expression.py
"""

import unittest
from core.expression_evaluator import (
    check_balanced_brackets,
    infix_to_postfix,
    evaluate_postfix,
    evaluate_campus_formula,
    ExpressionError
)


class TestExpressionEvaluator(unittest.TestCase):

    def test_balanced_brackets(self):
        # Valid balanced expressions
        valid_expressions = [
            "(a + b) * (c - d)",
            "{[()]}",
            "((10 + 20) * [30 / 5])",
            "no_brackets_at_all",
            ""
        ]
        for expr in valid_expressions:
            is_bal, msg = check_balanced_brackets(expr)
            self.assertTrue(is_bal, f"Expected '{expr}' to be balanced: {msg}")

        # Invalid unbalanced expressions
        invalid_expressions = [
            "( [ ) ]",            # Mismatched nesting
            "((a + b)",           # Unclosed open
            "a + b)",             # Unmatched close
            "{ [ ( ] ) }"         # Cross-nested brackets
        ]
        for expr in invalid_expressions:
            is_bal, _ = check_balanced_brackets(expr)
            self.assertFalse(is_bal, f"Expected '{expr}' to be detected as unbalanced.")

    def test_infix_to_postfix_conversion(self):
        cases = [
            ("A + B", ["A", "B", "+"]),
            ("A + B * C", ["A", "B", "C", "*", "+"]),
            ("(A + B) * C", ["A", "B", "+", "C", "*"]),
            ("A ^ B ^ C", ["A", "B", "C", "^", "^"]),  # Right-associative exponentiation
            ("A * (B + C) / D", ["A", "B", "C", "+", "*", "D", "/"])
        ]
        for infix, expected_postfix in cases:
            res = infix_to_postfix(infix)
            self.assertEqual(res, expected_postfix, f"Mismatch for '{infix}'")

    def test_evaluate_postfix_arithmetic(self):
        # Expression: (10 + 20) * 3 / 2 = 45.0
        tokens = ["10", "20", "+", "3", "*", "2", "/"]
        val = evaluate_postfix(tokens)
        self.assertEqual(val, 45.0)

        # Exponentiation: 2 ^ 3 = 8
        tokens_pow = ["2", "3", "^"]
        self.assertEqual(evaluate_postfix(tokens_pow), 8.0)

    def test_evaluate_with_variables(self):
        # Formula: (BaseFee + LabFee) * (1 - Discount / 100)
        # BaseFee=40000, LabFee=10000, Discount=20 -> (50000) * 0.8 = 40000.0
        formula = "(BaseFee + LabFee) * (1 - Discount / 100)"
        variables = {
            "BaseFee": 40000,
            "LabFee": 10000,
            "Discount": 20
        }
        success, net_fee, msg, postfix = evaluate_campus_formula(formula, variables)
        self.assertTrue(success)
        self.assertEqual(net_fee, 40000.0)
        self.assertIn("BaseFee", postfix)

    def test_division_by_zero(self):
        success, val, msg, _ = evaluate_campus_formula("100 / (5 - 5)")
        self.assertFalse(success)
        self.assertIn("Division by zero", msg)


if __name__ == "__main__":
    unittest.main()
