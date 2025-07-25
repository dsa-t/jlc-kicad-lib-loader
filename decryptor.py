import gzip
import io
import platform

try:
    from Crypto.Cipher import AES
except ImportError:
    if platform.system() == "Windows":
        raise Exception("Please install PyCryptodome in KiCad Command Prompt using: pip install pycryptodome")
    else:
        raise Exception("Please install PyCryptodome using: pip install pycryptodome")

def decryptDataStrIdData(encoded_data, key_hex, iv_hex):
    # Convert hex strings to bytes
    key = bytes.fromhex(key_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Create AES-GCM cipher
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    
    # In AES-GCM, typically the last 16 bytes are the authentication tag
    tag = encoded_data[-16:]
    actual_ciphertext = encoded_data[:-16]
    
    # Decrypt data
    plaintext = cipher.decrypt_and_verify(actual_ciphertext, tag)
    
    # Decompress with gzip
    with io.BytesIO(plaintext) as compressed_data:
        with gzip.GzipFile(fileobj=compressed_data, mode='rb') as f:
            decompressed_data = f.read()
    
    return decompressed_data.decode('utf-8')