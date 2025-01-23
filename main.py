import base64
from functools import wraps
from flask import flash, redirect, render_template, session, request

MORSE_CODE_DICT = {
    'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.', 'F':'..-.',
    'G':'--.', 'H':'....', 'I':'..', 'J':'.---', 'K':'-.-', 'L':'.-..',
    'M':'--', 'N':'-.', 'O':'---', 'P':'.--.', 'Q':'--.-', 'R':'.-.', 'S':'...',
    'T':'-', 'U':'..-', 'V':'...-', 'W':'.--', 'X':'-..-', 'Y':'-.--', 'Z':'--..',
    '1':'.----', '2':'..---', '3':'...--', '4':'....-', '5':'.....', '6':'-....',
    '7':'--...', '8':'---..', '9':'----.', '0':'-----', ', ':'--..--', '.':'.-.-.-',
    '?':'..--..', '/':'-..-.', '-':'-....-', '(':'-.--.', ')':'-.--.-', ' ':'/'}
nato_alphabet = {
    'A': 'Alfa', 'B': 'Bravo', 'C': 'Charlie', 'D': 'Delta', 'E': 'Echo', 'F': 'Foxtrot',
    'G': 'Golf', 'H': 'Hotel', 'I': 'India', 'J': 'Juliett', 'K': 'Kilo', 'L': 'Lima',
    'M': 'Mike', 'N': 'November', 'O': 'Oscar', 'P': 'Papa', 'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra',
    'T': 'Tango','U': 'Uniform', 'V': 'Victor', 'W': 'Whiskey', 'X': 'X-ray', 'Y': 'Yankee', 'Z': 'Zulu',
    ' ': '(space)', '.': 'Stop', '0': 'Zero', '1': 'One', '2': 'Two', '3': 'Three', '4': 'Four',
    '5': 'Five', '6': 'Six', '7': 'Seven', '8': 'Eight', '9': 'Nine'
    }

def binary_encryption(text):
    encrypted = ''.join(format(ord(i), '08b') for i in text)
    return encrypted

def binary_decryption(text):
    decrypted = ""
    character = [text[i:i + 8] for i in range(0, len(text), 8)]
    ascii_characters = [chr(int(bv, 2)) for bv in character]
    return ''.join(ascii_characters)

def caesar_encryption(text, key):
    encrypted = ""
    key = int(key) % 26
    for i in text:
        if i == " ":
            encrypted = encrypted + i
        else:
            if i.isalpha():
                value = ord(i) + key
                if i.isupper():
                    if value > ord("Z"):
                        value = value - 26
                if i.islower():
                    if value > ord("z"):
                        value = value - 26
                char = chr(value)
                encrypted = encrypted + char
            else:
                encrypted = encrypted + i
    return encrypted

def caesar_decryption(text, key):
    decrypted = ""
    key = int(key) % 26
    for i in text:
        if i == " ":
            decrypted = decrypted + i
        else:
            if i.isalpha():
                value = ord(i) - key
                if i.islower():
                    if value < ord("a"):
                        value += 26
                if i.isupper():
                    if value < ord("A"):
                        value += 26
                char = chr(value)
                decrypted = decrypted + char
            else:
                decrypted = decrypted + i
    return decrypted

def morse_encryption(text):
    text = text.upper()
    encrypted = ""
    for i in text:
        encrypted =  encrypted + MORSE_CODE_DICT[i] + " "
    return encrypted

def morse_decryption(text):
    inv_MORSE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}
    decrypted = ""
    for i in text.split():
        decrypted = decrypted + inv_MORSE_DICT[i]
    return decrypted

def base64_encryption(text):
    message_bytes = text.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message

def base64_decryption(text):
    try:
        decoded_bytes = base64.b64decode(text)
        decoded_str = decoded_bytes.decode('utf-8')
        return decoded_str
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        return f"Error decoding: {e}"

def base32_encryption(text):
    message_bytes = text.encode('ascii')
    base32_bytes = base64.b32encode(message_bytes)
    base32_message = base32_bytes.decode('ascii')
    return base32_message

def base32_decryption(text):
    try:
        decoded_bytes = base64.b32decode(text)
        decoded_str = decoded_bytes.decode('utf-8')
        return decoded_str
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        return f"Error decoding: {e}"

def base16_encryption(text):
    message_bytes = text.encode('ascii')
    base16_bytes = base64.b16encode(message_bytes)
    base16_message = base16_bytes.decode('ascii')
    return base16_message

def base16_decryption(text):
    try:
        decoded_bytes = base64.b16decode(text)
        decoded_str = decoded_bytes.decode('utf-8')
        return decoded_str
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        return f"Error decoding: {e}"

def base85_encryption(text):
    message_bytes = text.encode('ascii')
    base85_bytes = base64.a85encode(message_bytes)
    base85_message = base85_bytes.decode('ascii')
    return base85_message

def base85_decryption(text):
    try:
        decoded_bytes = base64.a85decode(text)
        decoded_str = decoded_bytes.decode('utf-8')
        return decoded_str
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        return f"Error decoding: {e}"

def nato_spelling_alphabet_encoder(text):
    text = text.upper()
    encoded = ""
    for i in text:
        encoded = encoded + nato_alphabet[i] + " "
    return encoded

def nato_spelling_alphabet_decoder(text):
    inv_NATO_DICT = {v: k for k, v in nato_alphabet.items()}
    decoded = ""
    words = text.split()
    for word in words:
        decoded = decoded + inv_NATO_DICT[word]
    return decoded

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/choose-custom")
        return f(*args, **kwargs)
    return decorated_function
