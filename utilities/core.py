import base64

def bHaMyJr6Q5D4HEG(data):
    if isinstance(data, (str, int)):
        data_bytes = str(data).encode("utf-8")
    else:
        raise TypeError("Data must be a string or an integer")
    return base64.b64encode(data_bytes).decode("utf-8")

def gcfXryBAy3Jo6h1(encoded_data):
    decoded_bytes = base64.b64decode(encoded_data)
    return decoded_bytes.decode('utf-8')

def encode_data(data):
    encoded = bHaMyJr6Q5D4HEG(data)
    for _ in range(2):
        encoded = bHaMyJr6Q5D4HEG(encoded)
    return encoded

def decode_data(encoded_data):
    decoded = gcfXryBAy3Jo6h1(encoded_data)
    for _ in range(2):
        decoded = gcfXryBAy3Jo6h1(decoded)
    return decoded