
import lexer


def convert2rpn(lexer_input):
    """
    :type lexer_input: lexer.ILexer
    :rtype: list[lexer.IToken]
    """
    operator_stack = []
    result_stack = []

    while 1:
        token = lexer_input.next()
        if token is None:
            break

        if token.is_left_parenthesis():
            operator_stack.append(token)
            continue

        if token.is_right_parenthesis():
            while len(operator_stack) > 0 and not operator_stack[-1].is_left_parenthesis():
                result_stack.append(operator_stack.pop())
            if len(operator_stack) <= 0:
                raise RuntimeError("Unmatched ')'!")
            operator_stack.pop()
            continue

        if not token.is_operator():
            result_stack.append(token)
            continue

        while len(operator_stack) > 0 and not operator_stack[-1].is_left_parenthesis() and \
                token.compare_operator_precedence(operator_stack[-1]) <= 0:
            result_stack.append(operator_stack.pop())
        operator_stack.append(token)

    while len(operator_stack) > 0:
        token = operator_stack.pop()
        if token.is_left_parenthesis():
            raise RuntimeError("Unmatched '('!")
        result_stack.append(token)

    return result_stack
