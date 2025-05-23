import heapq
import base64
from collections import Counter
from typing import Dict, Tuple

class HuffmanNode:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text: str) -> HuffmanNode:
    freq = Counter(text)
    heap = [HuffmanNode(ch, fr) for ch, fr in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = HuffmanNode(freq=node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)
    return heap[0] if heap else None

def get_codes(node: HuffmanNode, prefix="", codebook=None) -> Dict[str, str]:
    if codebook is None:
        codebook = {}
    if node:
        if node.char is not None:
            codebook[node.char] = prefix or "0"
        get_codes(node.left, prefix + "0", codebook)
        get_codes(node.right, prefix + "1", codebook)
    return codebook

def huffman_encode(text: str, codes: Dict[str, str]) -> Tuple[str, int]:
    bit_string = ''.join(codes[ch] for ch in text)
    padding = (8 - len(bit_string) % 8) % 8
    bit_string += "0" * padding
    b = bytearray()
    for i in range(0, len(bit_string), 8):
        b.append(int(bit_string[i:i+8], 2))
    return base64.b64encode(bytes(b)).decode(), padding

def huffman_decode(encoded_data: str, codes: Dict[str, str], padding: int) -> str:
    rev_codes = {v: k for k, v in codes.items()}
    data = base64.b64decode(encoded_data)
    bit_string = ''.join(f"{byte:08b}" for byte in data)
    if padding:
        bit_string = bit_string[:-padding]
    decoded = []
    code = ""
    for bit in bit_string:
        code += bit
        if code in rev_codes:
            decoded.append(rev_codes[code])
            code = ""
    return "".join(decoded)

def xor_encrypt(data: bytes, key: str) -> bytes:
    key_bytes = key.encode()
    return bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data)])

def xor_decrypt(data: bytes, key: str) -> bytes:
    return xor_encrypt(data, key)  # XOR is symmetric
