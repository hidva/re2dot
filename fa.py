from graphviz import Digraph
import collections


class State(object):
    def __init__(self, state_id, is_start, is_accept, fa):
        self.is_start = is_start
        self.is_accept = is_accept
        self.froms = []
        self.tos = []
        self.state_id = state_id
        self.fa = fa
        return

    def follow(self, ch):
        """
        :rtype: list[State]
        """
        # 如果严格遵循 https://blog.hidva.com/2018/11/14/EngineeringACompiler/ 中记录的 Thompson 构造法所遵循的性质,
        # 那么 len(froms) <= 2 + len(字母表). 所以应该不需要为 froms 整个索引, 常规遍历应该就足够了.
        ret = []
        for move in self.froms:
            if move.label == ch:
                ret.append(move.to_state)
        return ret  # 如果遵循 Thompson 构造法定义的性质, len(ret) <= 2.

    def __cls_def_end(self):
        return


class Move(object):
    def __init__(self, from_state, to, label):
        self.from_state = from_state
        self.to_state = to
        self.label = label
        return

    def __cls_def_end(self):
        return


class FA(object):
    EPSILON = 'ϵ'  # 感谢 unicode~

    def __init__(self):
        self.start = None
        self.accepts = []
        self.alphabet = set()  # EPSILON 并不是字母表一部分.
        return

    @staticmethod
    def build_from_letter(ch):
        """
        :rtype: FA
        """
        retfa = FA()
        s0 = retfa.new_state()
        s0.is_start = True
        s1 = retfa.new_state()
        s1.is_accept = True
        retfa.new_move(s0, s1, ch)
        retfa.start = s0
        retfa.accepts = [s1]
        return retfa

    def alternate(self, right):
        """
        :type right: FA
        :rtype: FA
        """
        # 参考 https://blog.hidva.com/2018/11/14/EngineeringACompiler/ 中记录的 Thompson 构造法所遵循的性质
        assert len(self.accepts) == 1
        assert len(right.accepts) == 1

        s0 = self.new_state()
        s0.is_start = True
        sn = self.new_state()
        sn.is_accept = True
        self.new_move(s0, self.start, FA.EPSILON)
        self.new_move(s0, right.start, FA.EPSILON)
        self.new_move(self.accepts[0], sn, FA.EPSILON)
        self.new_move(right.accepts[0], sn, FA.EPSILON)
        self.start.is_start = False
        self.accepts[0].is_accept = False
        right.start.is_start = False
        right.accepts[0].is_accept = False
        right.start = None
        right.accepts = None
        self.start = s0
        self.accepts[0] = sn
        self.alphabet.update(right.alphabet)
        return self

    def concat(self, right):
        """
        :type right: FA
        :rtype: FA
        """
        assert len(self.accepts) == 1
        assert len(right.accepts) == 1

        self.new_move(self.accepts[0], right.start, FA.EPSILON)
        self.accepts[0].is_accept = False
        right.start.is_start = False
        self.accepts[0] = right.accepts[0]
        self.alphabet.update(right.alphabet)
        right.start = None
        right.accepts = None
        return self

    def closure(self):
        """
        :rtype: FA
        """
        assert len(self.accepts) == 1

        s0 = self.new_state()
        sn = self.new_state()
        s0.is_start = True
        sn.is_accept = True
        self.new_move(s0, sn, FA.EPSILON)
        self.new_move(s0, self.start, FA.EPSILON)
        self.new_move(self.accepts[0], sn, FA.EPSILON)
        self.new_move(self.accepts[0], self.start, FA.EPSILON)
        self.start.is_start = False
        self.accepts[0].is_accept = False
        self.start = s0
        self.accepts[0] = sn
        return self

    @staticmethod
    def new_state_from(fa, slist):
        """
        :type fa: FA
        :type slist: list[State]
        :rtype: State
        """
        s = fa.new_state()
        for state in slist:
            if state.is_start:
                s.is_start = True
            if state.is_accept:
                s.is_accept = True
        if s.is_start:
            fa.start = s
        if s.is_accept:
            fa.accepts.append(s)
        return s

    def to_dfa(self):
        self.normalize_states_id()
        newfa = FA()
        # key 为 frozenset[state_id], 对应着 self 的一个有效配置. value 为该有效配置在新 dfa 中对应的状态.
        oldnew_map = {}
        slist, idset = FA.e_closure((self.start,))
        idset = frozenset(idset)
        oldnew_map[idset] = FA.new_state_from(newfa, slist)
        worklist = collections.deque(((slist, idset),))
        while len(worklist) > 0:
            q = worklist.popleft()
            for ch in self.alphabet:
                slist, idset = FA.e_closure(FA.delta(q[0], ch))
                if len(slist) <= 0:
                    continue
                idset = frozenset(idset)
                if idset not in oldnew_map:
                    oldnew_map[idset] = FA.new_state_from(newfa, slist)
                    worklist.append((slist, idset))
                newfa.new_move(oldnew_map[q[1]], oldnew_map[idset], ch)
        return newfa

    def new_state(self):
        return State(None, False, False, self)

    @staticmethod
    def e_closure(q):
        """
        :type q: list[State]|tuple[State]
        :rtype: tuple[list[State]]
        这里 type, rtype 只是用来给 IDE 自动完成, 并不是严格的实际类型.
        """
        ret = []
        idset = set()
        worklist = collections.deque(q)
        while len(worklist) > 0:
            state = worklist.popleft()
            if state.state_id in idset:
                continue
            ret.append(state)
            idset.add(state.state_id)
            worklist.extend(state.follow(FA.EPSILON))
        return ret, idset

    @staticmethod
    def delta(q, c):
        """
        :type q: list[State]
        :rtype: list[State]
        """
        ret = []
        for state in q:
            ret.extend(state.follow(c))
        return ret

    def new_move(self, from_state, to, label):
        """
        :type from_state: State
        :type to: State
        :rtype: Move
        """
        m = Move(from_state, to, label)
        from_state.froms.append(m)
        to.tos.append(m)
        if label != FA.EPSILON:
            self.alphabet.add(label)
        return m

    @staticmethod
    def dig_add_node(dig, state):
        """
        :type dig: Digraph
        :type state: State
        """
        dig.node(str(state.state_id), peripheries='2' if state.is_accept else '1')
        return

    @staticmethod
    def dig_add_edge(dig, move):
        """
        :type dig: Digraph
        :type move: Move
        """
        dig.edge(str(move.from_state.state_id), str(move.to_state.state_id), label=move.label)
        return

    def normalize_states_id(self):
        worklist = collections.deque()
        worklist.append(self.start)
        next_id = 1
        self.start.state_id = next_id
        next_id += 1
        while len(worklist) > 0:
            state = worklist.popleft()
            for move in state.froms:
                if move.to_state.state_id is None:
                    move.to_state.state_id = next_id
                    next_id += 1
                    worklist.append(move.to_state)
        return

    def to_dotsource(self):
        self.normalize_states_id()

        dig = Digraph(comment="Generated by hidva.com", body=['rankdir=LR'])
        dig.node('0', label='', peripheries='0')
        FA.dig_add_node(dig, self.start)
        dig.edge('0', str(self.start.state_id))

        # indig 记录着已经在 dig 中的 state id,
        # worklist 是 indig 的子集, 记录着哪些尚未处理 state.froms 的 state.
        # 再把一个状态加入到 indig 的同时也会根据该状态 froms 是否已被处理的情况选择性加入到 worklist 中.
        indig = set()
        indig.add(0)
        indig.add(self.start.state_id)
        worklist = collections.deque()
        worklist.append(self.start)
        while len(worklist) > 0:
            state = worklist.popleft()
            for move in state.froms:
                if move.to_state.state_id not in indig:
                    FA.dig_add_node(dig, move.to_state)
                    indig.add(move.to_state.state_id)
                    worklist.append(move.to_state)
                FA.dig_add_edge(dig, move)
        return dig.source

    def __cls_def_end(self):
        return
