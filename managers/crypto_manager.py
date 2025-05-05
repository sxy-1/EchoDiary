import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    load_pem_private_key,
)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
from managers.config_manager import ConfigManager


class CryptoManager:
    """
    RSA 加密工具类，支持混合加密

    提供生成密钥对、加载密钥、加密数据和解密数据的功能。
    """

    def __init__(self):
        """
        初始化 CryptoManager 类，确保密钥存储路径存在。
        """
        config = ConfigManager()
        self.key_path = config.get_config_value("key_path")
        if not self.key_path:
            raise ValueError("Key path is not set in config file.")
        os.makedirs(self.key_path, exist_ok=True)

    def _get_key_paths(self):
        """
        获取公钥和私钥的文件路径。

        Returns:
            tuple: 公钥路径和私钥路径。
        """
        public_key_path = os.path.join(self.key_path, "public_key.pem")
        private_key_path = os.path.join(self.key_path, "private_key.pem")
        return public_key_path, private_key_path

    def generate_rsa_keys(self):
        """
        生成 RSA 公钥和私钥，并保存到指定路径。
        如果密钥已存在，则跳过生成。
        """
        public_key_path, private_key_path = self._get_key_paths()

        # 如果密钥文件已存在，则不重新生成
        if os.path.exists(public_key_path) and os.path.exists(private_key_path):
            return

        # 生成密钥对
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        # 保存公钥
        with open(public_key_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

        # 保存私钥
        with open(private_key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

    def load_rsa_keys(self):
        """
        加载 RSA 公钥和私钥。

        Returns:
            tuple: 公钥对象和私钥对象。
        """
        self.generate_rsa_keys()  # 确保密钥已生成
        public_key_path, private_key_path = self._get_key_paths()

        # 加载公钥
        with open(public_key_path, "rb") as key_file:
            public_key = load_pem_public_key(key_file.read())

        # 加载私钥
        with open(private_key_path, "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)

        return public_key, private_key

    def encrypt_data(self, data: bytes) -> bytes:
        """
        使用混合加密加密数据：RSA 加密对称密钥，AES 加密数据。

        Args:
            data (bytes): 要加密的明文数据。

        Returns:
            bytes: 加密后的数据，包含 RSA 加密的对称密钥和 AES 加密的数据。
        """
        # 生成随机对称密钥和 IV
        symmetric_key = os.urandom(32)  # 256 位对称密钥
        iv = os.urandom(16)  # 128 位初始化向量

        # 使用 AES 加密数据
        cipher = Cipher(
            algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # 对数据进行填充
        padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()

        # 加密数据
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # 使用 RSA 加密对称密钥
        public_key, _ = self.load_rsa_keys()
        encrypted_key = public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # 返回组合后的加密数据
        return encrypted_key + iv + encrypted_data

    def decrypt_data(self, ciphertext: bytes) -> bytes:
        """
        使用混合加密解密数据：RSA 解密对称密钥，AES 解密数据。

        Args:
            ciphertext (bytes): 要解密的密文数据。

        Returns:
            bytes: 解密后的明文数据。
        """
        # 提取 RSA 加密的对称密钥、IV 和 AES 加密的数据
        encrypted_key = ciphertext[:256]  # RSA 加密的对称密钥长度为 256 字节
        iv = ciphertext[256:272]  # IV 长度为 16 字节
        encrypted_data = ciphertext[272:]  # 剩余部分为 AES 加密的数据

        # 使用 RSA 解密对称密钥
        _, private_key = self.load_rsa_keys()
        symmetric_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # 使用 AES 解密数据
        cipher = Cipher(
            algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # 去除填充
        unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        return data
