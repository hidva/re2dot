

class IToken(object):

    def is_operator(self):
        raise RuntimeError("Not implemented!")

    def is_left_parenthesis(self):
        raise RuntimeError("Not implemented!")

    def is_right_parenthesis(self):
        raise RuntimeError("Not implemented!")

    def compare_operator_precedence(self, right):
        raise RuntimeError("Not implemented!")

    def __cls_def_end(self):
        return


class ILexer(object):

    def next(self):
        """
        next() 用来返回下一个 Token, 若返回 None, 则表明到达了 end of file.
        :rtype: IToken
        """
        raise RuntimeError("Not implemented!")

    def __cls_def_end(self):
        return
