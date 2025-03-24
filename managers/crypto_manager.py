import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    load_pem_private_key,
)
from managers.config_manager import ConfigManager


class CryptoManager:
    """
    RSA 加密工具类

    提供生成密钥对、加载密钥、加密数据和解密数据的功能。
    """

    def __init__(self):
        """
        初始化 RSAEncryptor 类，确保密钥存储路径存在。
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
        使用公钥加密数据。

        Args:
            data (bytes): 要加密的明文数据。

        Returns:
            bytes: 加密后的密文数据。
        """
        public_key, _ = self.load_rsa_keys()
        ciphertext = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return ciphertext

    def decrypt_data(self, ciphertext: bytes) -> bytes:
        """
        使用私钥解密数据。

        Args:
            ciphertext (bytes): 要解密的密文数据。

        Returns:
            bytes: 解密后的明文数据。
        """
        _, private_key = self.load_rsa_keys()
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return plaintext
