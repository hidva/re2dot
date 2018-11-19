
import lexer
import fa


class Token(lexer.IToken):
    ALTERNATION_KIND = 'ALTERNATION'
    CONCATENATION_KIND = 'CONCATENATION'
    CLOSURE_KIND = 'CLOSURE'
    OPERAND_KIND = 'OPERAND'
    LEFT_PARENTHESIS_KIND = 'LEFT_PARENTHESIS_KIND'
    RIGHT_PARENTHESIS_KIND = 'RIGHT_PARENTHESIS_KIND'

    _OP_PRECEDENCE_MAP = {
        ALTERNATION_KIND: 0x66,
        CONCATENATION_KIND: 0xcc,
        CLOSURE_KIND: 0xff,
    }

    def __init__(self, kind, lexeme):
        self.kind = kind
        self.lexeme = lexeme
        return

    def is_operator(self):
        return self.kind != Token.OPERAND_KIND

    def is_left_parenthesis(self):
        return self.kind == Token.LEFT_PARENTHESIS_KIND

    def is_right_parenthesis(self):
        return self.kind == Token.RIGHT_PARENTHESIS_KIND

    def compare_operator_precedence(self, right):
        """
        :type right: Token
        """
        return Token._OP_PRECEDENCE_MAP[self.kind] - Token._OP_PRECEDENCE_MAP[right.kind]

    def __str__(self):
        return '<%s, %s>' % (self.kind, self.lexeme)

    def __cls_def_end(self):
        return


class Lexer(lexer.ILexer):
    ALTERNATION_TOKEN = Token(Token.ALTERNATION_KIND, '|')
    CONCATENATION_TOKEN = Token(Token.CONCATENATION_KIND, '')
    CLOSURE_TOKEN = Token(Token.CLOSURE_KIND, '*')
    LEFT_PARENTHESIS_TOKEN = Token(Token.LEFT_PARENTHESIS_KIND, '(')
    RIGHT_PARENTHESIS_TOKEN = Token(Token.RIGHT_PARENTHESIS_KIND, ')')

    def __init__(self, input_data):
        self.data = input_data
        self.pos = 0
        self.pre_token = None
        return

    def next(self):
        if self.pos >= len(self.data):
            return None

        ch = self.data[self.pos]
        if ch == ')':
            self.pre_token = Lexer.RIGHT_PARENTHESIS_TOKEN
            self.pos += 1
            return self.pre_token
        if ch == '|':
            self.pre_token = Lexer.ALTERNATION_TOKEN
            self.pos += 1
            return self.pre_token
        if ch == '*':
            self.pre_token = Lexer.CLOSURE_TOKEN
            self.pos += 1
            return self.pre_token

        # 用来判断是否需要返回一个 CONCATENATION_KIND token, 或许可以使用查表法来避免这么多分支.
        if self.pre_token is not None and \
                (self.pre_token.kind == Token.OPERAND_KIND or self.pre_token.kind == Token.CLOSURE_KIND or
                 self.pre_token.kind == Token.RIGHT_PARENTHESIS_KIND):
            self.pre_token = Token(Token.CONCATENATION_KIND, '')
            return self.pre_token

        if ch == '(':
            self.pre_token = Lexer.LEFT_PARENTHESIS_TOKEN
            self.pos += 1
            return self.pre_token

        self.pre_token = Token(Token.OPERAND_KIND, ch)
        self.pos += 1
        return self.pre_token

    def __cls_def_end(self):
        return


def execute_rpn(tokens):
    """
    :type tokens: list[Token]
    :rtype: fa.FA
    """
    fa_stack = []
    for token in tokens:
        if not token.is_operator():
            fa_stack.append(fa.FA(token.lexeme))
            continue

        if token.kind == Token.CLOSURE_KIND:
            if len(fa_stack) <= 0:
                raise RuntimeError("Unexpected Token: %s" % token)
            fa_stack[-1].closure()
        elif token.kind == Token.CONCATENATION_KIND:
            if len(fa_stack) <= 1:
                raise RuntimeError("Unexpected Token: %s" % token)
            fa_stack[-2].concat(fa_stack[-1])
            fa_stack.pop()
        else:
            assert token.kind == Token.ALTERNATION_KIND
            if len(fa_stack) <= 1:
                raise RuntimeError("Unexpected Token: %s" % token)
            fa_stack[-2].alternate(fa_stack[-1])
            fa_stack.pop()
    if len(fa_stack) != 1:
        raise RuntimeError("Lack Operator")
    return fa_stack[0]
