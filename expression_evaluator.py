"""
Smart Campus Algorithmic Engine: Phase 1 Linear Data Structures
File: core/expression_evaluator.py

Stack Application for Expression Handling:
1. Syntax & Parentheses / Bracket Balancing Check: O(n)
2. Infix-to-Postfix (Reverse Polish Notation) Conversion via Shunting-Yard: O(n)
3. Postfix Expression Evaluation with Variable Substitution: O(n)

All stack operations utilize the custom LinkedStack (no built-in Python list as stack).
"""

import re
from typing import Dict, List, Optional, Tuple
from core.stack import LinkedStack


class ExpressionError(Exception):
    """Custom exception for expression parsing and evaluation errors."""
    pass


def check_balanced_brackets(expression: str) -> Tuple[bool, str]:
    """
    Validates if brackets '()', '[]', '{}' in an expression are properly matched and balanced.
    Uses custom LinkedStack.
    Returns: (is_balanced: bool, explanation: str)
    """
    stack = LinkedStack()
    bracket_pairs = {')': '(', ']': '[', '}': '{'}
    opening_brackets = set(bracket_pairs.values())

    for idx, char in enumerate(expression):
        if char in opening_brackets:
            stack.push((char, idx))
        elif char in bracket_pairs:
            if stack.is_empty():
                return False, f"Unmatched closing bracket '{char}' at index {idx}."
            top_char, top_idx = stack.pop()
            expected_open = bracket_pairs[char]
            if top_char != expected_open:
                return False, f"Mismatched brackets: expected '{expected_open}' to match '{char}' at index {idx}, but found '{top_char}' from index {top_idx}."

    if not stack.is_empty():
        top_char, top_idx = stack.pop()
        return False, f"Unclosed opening bracket '{top_char}' at index {top_idx}."

    return True, "All parentheses and brackets are properly balanced."


def tokenize_expression(expression: str) -> List[str]:
    """
    Splits mathematical expression into tokens (numbers, variable names, operators, brackets).
    Example: '(attendees + equipment_units) * 0.9' -> ['(', 'attendees', '+', 'equipment_units', ')', '*', '0.9']
    """
    # Pattern matching floats/ints, identifiers (variables), and operators
    token_pattern = r"(\d+(?:\.\d+)?|[a-zA-Z_][a-zA-Z0-9_]*|\*\*|[+\-*/^()%\[\]{}])"
    raw_tokens = re.findall(token_pattern, expression)
    # Filter out empty whitespace tokens
    return [t.strip() for t in raw_tokens if t.strip()]


def infix_to_postfix(expression: str) -> List[str]:
    """
    Converts Infix mathematical expression to Postfix (Reverse Polish Notation)
    using Dijkstra's Shunting-Yard algorithm powered by custom LinkedStack.
    """
    # Check bracket validity first
    is_balanced, reason = check_balanced_brackets(expression)
    if not is_balanced:
        raise ExpressionError(f"Syntax Error: {reason}")

    precedence = {
        '^': 4,
        '*': 3, '/': 3, '%': 3,
        '+': 2, '-': 2
    }
    right_associative = {'^'}

    output_queue: List[str] = []
    op_stack = LinkedStack()

    tokens = tokenize_expression(expression)

    for token in tokens:
        # Check if number (float or int) or variable identifier
        if re.match(r"^\d+(?:\.\d+)?$", token) or re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", token):
            output_queue.append(token)
        elif token in "([{":
            op_stack.push(token)
        elif token in ")]}":
            matching_open = {'(': ')', '[': ']', '{': '}'}
            # Pop operators until matching opening bracket
            popped = False
            while not op_stack.is_empty():
                top = op_stack.peek()
                if top in "([{":
                    op_stack.pop()
                    popped = True
                    break
                else:
                    output_queue.append(op_stack.pop())
            if not popped:
                raise ExpressionError(f"Mismatched closing bracket '{token}'.")
        elif token in precedence:
            curr_prec = precedence[token]
            while not op_stack.is_empty():
                top = op_stack.peek()
                if top in "([{":
                    break
                top_prec = precedence.get(top, 0)
                # Left-associative: pop while top_prec >= curr_prec
                # Right-associative (^): pop while top_prec > curr_prec
                if (token not in right_associative and top_prec >= curr_prec) or \
                   (token in right_associative and top_prec > curr_prec):
                    output_queue.append(op_stack.pop())
                else:
                    break
            op_stack.push(token)
        else:
            raise ExpressionError(f"Unrecognized operator or token: '{token}'")

    # Pop remaining operators
    while not op_stack.is_empty():
        top = op_stack.pop()
        if top in "([{)]}":
            raise ExpressionError("Mismatched parentheses in expression.")
        output_queue.append(top)

    return output_queue


def evaluate_postfix(postfix_tokens: List[str], variables: Optional[Dict[str, float]] = None) -> float:
    """
    Evaluates Postfix tokens using a custom LinkedStack of operands.
    Replaces variable identifiers with values from the variables dictionary.
    """
    if variables is None:
        variables = {}

    operand_stack = LinkedStack()

    for token in postfix_tokens:
        # Check if float/int number
        if re.match(r"^\d+(?:\.\d+)?$", token):
            operand_stack.push(float(token))
        # Check if variable name
        elif re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", token):
            if token not in variables:
                raise ExpressionError(f"Undefined variable in expression: '{token}'")
            operand_stack.push(float(variables[token]))
        # Operator
        elif token in {'+', '-', '*', '/', '%', '^'}:
            if len(operand_stack) < 2:
                raise ExpressionError(f"Malformed expression: insufficient operands for operator '{token}'.")
            b = operand_stack.pop()
            a = operand_stack.pop()

            if token == '+':
                res = a + b
            elif token == '-':
                res = a - b
            elif token == '*':
                res = a * b
            elif token == '/':
                if b == 0:
                    raise ZeroDivisionError("Division by zero in formula evaluation.")
                res = a / b
            elif token == '%':
                if b == 0:
                    raise ZeroDivisionError("Modulo by zero in formula evaluation.")
                res = a % b
            elif token == '^':
                res = a ** b
            else:
                raise ExpressionError(f"Unknown operator '{token}'.")

            operand_stack.push(res)
        else:
            raise ExpressionError(f"Unexpected token in postfix evaluation: '{token}'")

    if len(operand_stack) != 1:
        raise ExpressionError(f"Malformed expression: stack ended with {len(operand_stack)} values instead of 1.")

    return operand_stack.pop()


def evaluate_campus_formula(expression: str, variables: Optional[Dict[str, float]] = None) -> Tuple[bool, float, str, List[str]]:
    """
    High-level API:
    1. Validates parentheses balancing.
    2. Converts infix to postfix using LinkedStack.
    3. Evaluates postfix using LinkedStack.
    Returns: (success: bool, result_value: float, explanation: str, postfix_tokens: List[str])
    """
    try:
        is_balanced, reason = check_balanced_brackets(expression)
        if not is_balanced:
            return False, 0.0, reason, []

        postfix = infix_to_postfix(expression)
        result = evaluate_postfix(postfix, variables)
        return True, round(result, 2), "Formula evaluated successfully.", postfix
    except Exception as e:
        return False, 0.0, str(e), []
