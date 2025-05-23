from fastapi import APIRouter, Depends
from app.schemas.encryption import EncodeRequest, EncodeResponse, DecodeRequest, DecodeResponse
from app.services.encryption import (
    build_huffman_tree, get_codes, huffman_encode, huffman_decode,
    xor_encrypt, xor_decrypt
)

router = APIRouter()

@router.post("/encode", response_model=EncodeResponse)
def encode(req: EncodeRequest):
    # Step 1: build Huffman tree and codes
    tree = build_huffman_tree(req.text)
    codes = get_codes(tree)
    # Step 2: encode text by Huffman
    encoded_huff, padding = huffman_encode(req.text, codes)
    # Step 3: XOR encrypt the bytes of base64-decoded data
    huff_bytes = base64.b64decode(encoded_huff)
    xored = xor_encrypt(huff_bytes, req.key)
    # Step 4: base64 encode final data
    final_encoded = base64.b64encode(xored).decode()
    return EncodeResponse(
        encoded_data=final_encoded,
        key=req.key,
        huffman_codes=codes,
        padding=padding
    )

@router.post("/decode", response_model=DecodeResponse)
def decode(req: DecodeRequest):
    # Step 1: base64 decode, then XOR-decrypt
    xored_bytes = base64.b64decode(req.encoded_data)
    huff_bytes = xor_decrypt(xored_bytes, req.key)
    # Step 2: base64 encode back to string for huffman_decode
    huff_encoded = base64.b64encode(huff_bytes).decode()
    # Step 3: Huffman decode
    decoded_text = huffman_decode(huff_encoded, req.huffman_codes, req.padding)
    return DecodeResponse(decoded_text=decoded_text)
