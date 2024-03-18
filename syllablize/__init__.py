import syllablize.graph
import random

vowels = ['a', 'e', 'i', 'o', 'u']


class ConsonantVowel:
    def __init__(self):
        self.consonant_cfs = graph.ChainForwardStar(100000)
        self.consonant_matrix = graph.AdjacencyMatrix(30, 30)
        self.consonant_cfs.connect(0, 27)
        self.consonant_matrix.connect(0, 27)

        self.vowel_cfs = graph.ChainForwardStar(1000)
        self.vowel_matrix = graph.AdjacencyMatrix(30, 30)

        self.pre_vowel_cfs = graph.ChainForwardStar(100000)
        self.pre_vowel_matrix = graph.AdjacencyMatrix(30, 30)

        self.post_vowel_cfs = graph.ChainForwardStar(100000)
        self.post_vowel_matrix = graph.AdjacencyMatrix(30, 30)

    def _train_vowel(self, text: str, nodes: list[int], lp: int) -> int:
        rp = lp
        rear_consonant = True
        while rp < len(text) and text[rp] in vowels:
            rp += 1
        if rp == len(text):
            rp -= 1
            rear_consonant = False
        if lp != 0:
            lp -= 1
            if not self.consonant_matrix[nodes[lp]][27]:
                self.consonant_cfs.connect(nodes[lp], 27)
                self.consonant_matrix.connect(nodes[lp], 27)
        if lp == rp:
            return rp
        if not self.pre_vowel_matrix[nodes[lp]][nodes[lp + 1]]:
            self.pre_vowel_cfs.connect(nodes[lp], nodes[lp + 1])
            self.pre_vowel_matrix.connect(nodes[lp], nodes[lp + 1])
        if not self.post_vowel_matrix[nodes[rp - 1]][nodes[rp]] and rear_consonant:
            self.post_vowel_cfs.connect(nodes[rp - 1], nodes[rp])
            self.post_vowel_matrix.connect(nodes[rp - 1], nodes[rp])
        if not self.consonant_matrix[0][nodes[rp]] and rear_consonant:
            self.consonant_cfs.connect(0, nodes[rp])
            self.consonant_matrix.connect(0, nodes[rp])
        for i in range(lp + 2, rp):
            if not self.vowel_matrix[nodes[i - 1]][nodes[i]]:
                self.vowel_cfs.connect(nodes[i - 1], nodes[i])
                self.vowel_matrix.connect(nodes[i - 1], nodes[i])
        if rear_consonant:
            if not self.vowel_matrix[nodes[rp - 1]][27]:
                self.vowel_cfs.connect(nodes[rp - 1], 27)
                self.vowel_matrix.connect(nodes[rp - 1], 27)
        else:
            if not self.vowel_matrix[nodes[rp]][27]:
                self.vowel_cfs.connect(nodes[rp], 27)
                self.vowel_matrix.connect(nodes[rp], 27)
        return rp

    def train(self, text: str):
        nodes = []
        for char in text:
            nodes.append(ord(char) - ord('a') + 1)
        sp = 1
        if not self.consonant_matrix[0][nodes[0]]:
            if text[0] not in vowels:
                self.consonant_cfs.connect(0, nodes[0])
                self.consonant_matrix.connect(0, nodes[0])
            else:
                sp = self._train_vowel(text, nodes, 0) + 1
        while sp < len(nodes):
            if not self.consonant_matrix[nodes[sp - 1]][nodes[sp]]:
                if text[sp] not in vowels:
                    self.consonant_cfs.connect(nodes[sp - 1], nodes[sp])
                    self.consonant_matrix.connect(nodes[sp - 1], nodes[sp])
                else:
                    sp = self._train_vowel(text, nodes, sp)
            sp += 1
        if not self.consonant_matrix[nodes[-1]][27]:
            if text[-1] not in vowels:
                self.consonant_cfs.connect(nodes[-1], 27)
                self.consonant_matrix.connect(nodes[-1], 27)

    def consonant(self, begin: int = 0) -> str:
        if random.randint(1, 20) == 1:
            return ""
        ret: str = chr(begin + ord('a') - 1) if begin != 0 else ""
        v = begin
        while v != 27:
            iterator = graph.ChainForwardStarIterator(self.consonant_cfs, v)
            edge_num = random.randint(1, self.consonant_matrix.o_deg[v])
            for i in range(edge_num - 1):
                next(iterator)
            v = next(iterator)
            v_char = chr(v + ord('a') - 1)
            while v_char in vowels:
                try:
                    v = next(iterator)
                    v_char = chr(v + ord('a') - 1)
                except StopIteration:
                    iterator = graph.ChainForwardStarIterator(self.consonant_cfs, 0)
                    v = next(iterator)
                    v_char = chr(v + ord('a') - 1)
            if v != 27:
                ret += v_char
        return ret

    def vowel(self, begin: int) -> str:
        ret: str = chr(begin + ord('a') - 1)
        v = begin
        while v != 27:
            iterator = graph.ChainForwardStarIterator(self.vowel_cfs, v)
            edge_num = random.randint(1, self.vowel_matrix.o_deg[v])
            for i in range(edge_num - 1):
                next(iterator)
            v = next(iterator)
            v_char = chr(v + ord('a') - 1)
            if v != 27:
                ret += v_char
        return ret

    def connect(self, mode: str, begin: int) -> str:
        v = begin
        if mode == "pre":
            iterator = graph.ChainForwardStarIterator(self.pre_vowel_cfs, v)
            edge_num = random.randint(1, self.pre_vowel_matrix.o_deg[v])
            for i in range(edge_num - 1):
                next(iterator)
            v = next(iterator)
            v_char = chr(v + ord('a') - 1)
        elif mode == "post":
            iterator = graph.ChainForwardStarIterator(self.post_vowel_cfs, v)
            edge_num = random.randint(1, self.post_vowel_matrix.o_deg[v])
            for i in range(edge_num - 1):
                next(iterator)
            v = next(iterator)
            v_char = chr(v + ord('a') - 1)
        else:
            v_char = ""
        return v_char

    def generate_syllable(self, begin: int = 0) -> str:
        pre_consonant = self.consonant(begin)
        vowel = self.connect("pre", ord(pre_consonant[-1]) - ord('a') + 1) \
            if pre_consonant != "" else random.choice(vowels)
        vowel = self.vowel(ord(vowel) - ord('a') + 1)
        if self.consonant() == "":
            post_consonant = ""
        else:
            post_connector = self.connect("post", ord(vowel[-1]) - ord('a') + 1)
            post_consonant = self.consonant(ord(post_connector) - ord('a') + 1)
        ret = pre_consonant + vowel + post_consonant
        return ret if begin == 0 else ret[1:]


class ConsonantVowelLarge(ConsonantVowel):
    def __init__(self):
        super().__init__()
        self.consonant_cfs = graph.ChainForwardStar(5000000)
        self.consonant_cfs.connect(0, 27)

        self.vowel_cfs = graph.ChainForwardStar(5000000)

        self.pre_vowel_cfs = graph.ChainForwardStar(5000000)

        self.post_vowel_cfs = graph.ChainForwardStar(5000000)

    def _train_vowel(self, text: str, nodes: list[int], lp: int) -> int:
        rp = lp
        rear_consonant = True
        while rp < len(text) and text[rp] in vowels:
            rp += 1
        if rp == len(text):
            rp -= 1
            rear_consonant = False
        if lp != 0:
            lp -= 1
            self.consonant_cfs.connect(nodes[lp], 27)
            self.consonant_matrix.connect(nodes[lp], 27)
        if lp == rp:
            return rp
        self.pre_vowel_cfs.connect(nodes[lp], nodes[lp + 1])
        self.pre_vowel_matrix.connect(nodes[lp], nodes[lp + 1])
        if rear_consonant:
            self.post_vowel_cfs.connect(nodes[rp - 1], nodes[rp])
            self.post_vowel_matrix.connect(nodes[rp - 1], nodes[rp])
            self.consonant_cfs.connect(0, nodes[rp])
            self.consonant_matrix.connect(0, nodes[rp])
        for i in range(lp + 2, rp):
            self.vowel_cfs.connect(nodes[i - 1], nodes[i])
            self.vowel_matrix.connect(nodes[i - 1], nodes[i])
        if rear_consonant:
            self.vowel_cfs.connect(nodes[rp - 1], 27)
            self.vowel_matrix.connect(nodes[rp - 1], 27)
        else:
            self.vowel_cfs.connect(nodes[rp], 27)
            self.vowel_matrix.connect(nodes[rp], 27)
        return rp

    def train(self, text: str):
        nodes = []
        for char in text:
            nodes.append(ord(char) - ord('a') + 1)
        sp = 1
        if text[0] not in vowels:
            self.consonant_cfs.connect(0, nodes[0])
            self.consonant_matrix.connect(0, nodes[0])
        else:
            sp = self._train_vowel(text, nodes, 0) + 1
        while sp < len(nodes):
            if text[sp] not in vowels:
                self.consonant_cfs.connect(nodes[sp - 1], nodes[sp])
                self.consonant_matrix.connect(nodes[sp - 1], nodes[sp])
            else:
                sp = self._train_vowel(text, nodes, sp)
            sp += 1
        if text[-1] not in vowels:
            self.consonant_cfs.connect(nodes[-1], 27)
            self.consonant_matrix.connect(nodes[-1], 27)
