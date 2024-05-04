import heapq


class Node:
    def __init__(self, ch, freq):
        self.ch = ch
        self.freq = freq
        self.leftChild = None
        self.rightChild = None

    def __lt__(self, other):
        return self.freq < other.freq#5444
#!

def create_huffman_tree(message):
    char_freq = {}
    for ch in message:
        if ch in char_freq:
            char_freq[ch] += 1
        else:
            char_freq[ch] = 1

    prior_queue = []
    for key in char_freq:
        heapq.heappush(prior_queue, Node(key, char_freq[key]))

    while len(prior_queue) > 1:
        left = heapq.heappop(prior_queue)
        right = heapq.heappop(prior_queue)

        internal_node = Node('\0', left.freq + right.freq)
        internal_node.leftChild = left
        internal_node.rightChild = right

        heapq.heappush(prior_queue, internal_node)

    return heapq.heappop(prior_queue)


def encode(root, string, huffman_code):
    if root is None:
        return

    if root.leftChild is None and root.rightChild is None:
        huffman_code[root.ch] = string
        return

    encode(root.leftChild, string + "0", huffman_code)
    encode(root.rightChild, string + "1", huffman_code)


def encode_message(message, huffman_code):
    encoded_message = ""
    for ch in message:
        encoded_message += huffman_code[ch]

    return encoded_message


n = int(input())
numbers = [input().strip() for _ in range(n)]
max_len = 0
min_len = 10 ** 10

for message in numbers:
    root = create_huffman_tree(message)

    huffman_code = {}
    encode(root, "", huffman_code)

    encoded_message = encode_message(message, huffman_code)
    len_code = len(encoded_message)
    if len_code > max_len:
        max_len = len_code
    if len_code < min_len:
        min_len = len_code

print(max_len)
print(min_len)