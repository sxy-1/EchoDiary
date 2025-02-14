import os
import pickle
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from utils import config


def get_rsa_keys():

    generate_rsa_keys()

    key_path = config.get_config_value("key_path")
    public_key_path = os.path.join(key_path,"public_key.pem")
    private_key_path = os.path.join(key_path,"private_key.pem")


    with open(public_key_path, "rb") as key_file:
        public_key = load_pem_public_key(key_file.read())
    with open(private_key_path, "rb") as key_file:
        private_key = load_pem_private_key(key_file.read(), password=None)

    return  public_key,private_key

def generate_rsa_keys():


    key_path = config.get_config_value("key_path")
    public_key_path = os.path.join(key_path, "public_key.pem")
    private_key_path = os.path.join(key_path, "private_key.pem")


    if  os.path.exists(public_key_path) and os.path.exists(private_key_path):
        return


    # if not os.path.exists(public_key_path):
    #     os.makedirs(public_key_path)
    #
    # # 如果目录不存在,则创建
    # if not os.path.exists(private_key_path):
    #     os.makedirs(private_key_path)


    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # 如果目录不存在,则创建


    # 保存公钥和私钥到指定路径
    with open(public_key_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))


def encrypt_data(data):
    public_key, private_key = get_rsa_keys()
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def decrypt_data(ciphertext):
    public_key, private_key = get_rsa_keys()
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext