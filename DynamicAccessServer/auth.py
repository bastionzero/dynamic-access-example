from Crypto.Hash import SHA256, HMAC
from flask import Request
import json
from binascii import hexlify, unhexlify

# constants
KEY_PREFIX = 'BZERO'
SIG_SUFFIX = 'bzero_request'
ALGO_NAME  = 'HMAC-SHA256'


# HMAC a string with a particular key
def sign(key: bytes, msg: str) -> bytes:
    return HMAC.new(key, msg.encode('utf-8'), SHA256).digest()

# Generate key to sign canonical ordering string with
def generateSigningKey(sharedSecret: str, timestamp: str, action: str) -> bytes:
    sharedSecretBytes = sharedSecret.encode('utf-8')  # sharedSecret stored in utf-8 encoding, get bytes

    # prefix the sharedSecretBytes with KEY_PREFIX
    keyPrefixBytes = KEY_PREFIX.encode('utf-8') # generate prefix byte array
    prefixedKeyBytes = keyPrefixBytes + sharedSecretBytes # concatenate the two byte arrats

    # sign date
    kDate = sign(prefixedKeyBytes, timestamp)

    # sign action
    kAction = sign(kDate, action)

    # sign suffix
    kDerviedKey = sign(kAction, SIG_SUFFIX)

    return kDerviedKey 


def validateSignature(action: str, request: Request, sharedSecret: str) -> bool:
    timestamp = request.headers.get('X-Timestamp') # Unix epoch time in seconds 
    signatureReceived = unhexlify(request.headers.get('X-Signature')) # hex string to byte array
    signingKey = generateSigningKey(sharedSecret, timestamp, action)
    
    # The bytes of a json that is serialized with zero spaces/indents
    requestBytes = json.dumps(request.json, indent=None, separators=(',', ':')).encode('utf-8')
    requestBytesHex = SHA256.new(requestBytes).hexdigest()

    # Canonical Ordering:
    #   ALGO_NAME   + \n + 
    #   TIMESTAMP   + \n + 
    #   ACTION      + /  +  yes a forward slash here
    #   SIG_SUFFIX  + \n +
    #   REQUEST_BYTES_HASHED_IN_HEX
    canonicalOrdering = f'{ALGO_NAME}\n{timestamp}\n{action}/{SIG_SUFFIX}\n{requestBytesHex}'

    derivedSignature = sign(signingKey, canonicalOrdering)

    return signatureReceived == derivedSignature

