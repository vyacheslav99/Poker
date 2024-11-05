import argparse
import rsa
import base64
import hashlib

from api import config


def gen_keys():
    print('Begin generate keys...')
    pubkey, prvkey = rsa.newkeys(4096)
    print('Saving keys...')

    with open('./publickey.pem', 'wb') as f:
        f.write(pubkey.save_pkcs1(format='PEM'))

    with open('./privatekey.pem', 'wb') as f:
        f.write(prvkey.save_pkcs1(format='PEM'))

    print('Done! Saved to api folder: privatekey.pem, publickey.pem')

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
    print(f'Success! encoded:\n{b64.hex()}\n{b64.decode()}')

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


def encode(passphrase: str):
    print('Process encoding...')
    pubkey = rsa.PublicKey.load_pkcs1(config.RSA_PUBLIC_KEY.encode())
    cipher = rsa.encrypt(passphrase.encode(), pubkey)
    print(f'Success! Raw length: {len(cipher)}')

    print('Process base64 encoding...')
    b64 = base64.urlsafe_b64encode(cipher)
    print(f'Success! encoded:\n{b64.hex()}\n{b64.decode()}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--gen_keys', '-g', action='store_true',
                    help='Сгенерить новую пару ключей. Текущие файлы будут перезаписаны!')
    ap.add_argument('--test', '-t', action='store_true', default=True,
                    help='Выполнить тестовый цикл шифрования-расшифровки, используя текущие ключи')
    ap.add_argument('--enc', '-e', help='Зашифровать переданный пароль')
    args = ap.parse_args()

    if args.gen_keys:
        gen_keys()
    elif args.enc:
        encode(args.enc)
    else:
        test()
