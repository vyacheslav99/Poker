import argparse
import rsa
import base64
import hashlib

from configs import config


def gen_keys():
    print('Begin generate keys...')
    pubkey, prvkey = rsa.newkeys(4096)
    print('Saving keys...')

    with open('./configs/publickey.pem', 'wb') as f:
        f.write(pubkey.save_pkcs1(format='PEM'))

    with open('./configs/privatekey.pem', 'wb') as f:
        f.write(prvkey.save_pkcs1(format='PEM'))

    print('Done! Saved to configs folder: privatekey.pem, publickey.pem')

    print('Testing keys...')
    test(pubkey=pubkey, prvkey=prvkey)


def test(pubkey=None, prvkey=None):
    passphrase = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit.'

    if not pubkey or not prvkey:
        print('Loading keys from config file...')
        pubkey = rsa.PublicKey.load_pkcs1(config.RSA_PUBLIC_KEY.encode())
        prvkey = rsa.PrivateKey.load_pkcs1(config.RSA_PRIVATE_KEY.encode())

    print('Process encoding...')
    cipher = rsa.encrypt(passphrase.encode(), pubkey)
    print(f'Success! Raw length: {len(cipher)}')

    print('Process base64 encoding...')
    b64 = base64.urlsafe_b64encode(cipher)
    print(f'Success! encoded:\n{b64.hex()}\n{b64}')

    print('Process base64 decoding...')
    encrypted = base64.urlsafe_b64decode(b64)
    print(f'Success! Raw length: {len(encrypted)}')

    print('Process decoding...')
    decrypted = rsa.decrypt(encrypted, prvkey).decode()

    if decrypted == passphrase:
        print(f'Success! Phrase: {decrypted}')
    else:
        print(f'Failed! Result: {decrypted}')
        return

    print('Calc sha3_224 hash')
    hash_ = hashlib.sha3_224(decrypted.encode())
    print(f'Success! Hash: {hash_.hexdigest()}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--test', '-t', action='store_true', help='Выполнить тестовый цикл шифрования-расшифровки, '
                                                              'используя текущие ключи')
    args = ap.parse_args()

    if args.test:
        test()
    else:
        gen_keys()