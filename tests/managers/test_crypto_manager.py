import os
import pickle
from unittest.mock import patch
from cryptography.hazmat.primitives.asymmetric import rsa
from managers.crypto_manager import CryptoManager


class TestCryptoManager:
    """
    测试 CryptoManager 类的功能，包括密钥生成、加载、加密和解密。
    """

    def setup_method(self):
        """
        测试前的初始化操作。
        创建测试密钥存储目录，并初始化 CryptoManager 实例。
        如果密钥不存在，则生成密钥。
        """
        self.test_dir = os.path.abspath("./tests/mock_data/test_keys")
        print(f"Test directory: {self.test_dir}")  # 打印路径，确认是否正确

        os.makedirs(self.test_dir, exist_ok=True)

        # Mock _get_key_paths 方法以使用测试路径
        with patch("utils.config.get_config_value", return_value=self.test_dir), \
             patch.object(CryptoManager, "_get_key_paths", return_value=(
                 os.path.join(self.test_dir, "public_key.pem"),
                 os.path.join(self.test_dir, "private_key.pem")
             )):
            self.crypto_manager = CryptoManager()

            # 如果密钥不存在，则生成密钥
            public_key_path, private_key_path = self.crypto_manager._get_key_paths()
            if not (os.path.exists(public_key_path) and os.path.exists(private_key_path)):
                self.crypto_manager.generate_rsa_keys()

    def test_generate_rsa_keys(self):
        """
        测试生成 RSA 密钥对。
        验证公钥和私钥文件是否正确生成。
        """
        self.crypto_manager.generate_rsa_keys()
        public_key_path, private_key_path = self.crypto_manager._get_key_paths()
        assert os.path.exists(public_key_path)
        assert os.path.exists(private_key_path)

    def test_load_rsa_keys(self):
        """
        测试加载 RSA 公钥和私钥。
        验证加载的密钥是否为正确的 RSA 密钥对象。
        """
        public_key, private_key = self.crypto_manager.load_rsa_keys()
        assert isinstance(public_key, rsa.RSAPublicKey)
        assert isinstance(private_key, rsa.RSAPrivateKey)

    def test_encrypt_decrypt(self):
        """
        测试加密和解密功能。
        验证加密后的密文能正确解密为原始明文。
        """
        data = b"Hello, World!"
        ciphertext = self.crypto_manager.encrypt_data(data)
        plaintext = self.crypto_manager.decrypt_data(ciphertext)
        assert plaintext == data

    def test_encrypt_decrypt_with_mock_data(self):
        """
        测试加密和解密功能，使用模拟的日记数据。
        验证加密后的密文能正确解密为原始数据。
        """
        data = {
            "date": "2025-03-23",
            "time": "12:00:00",
            "note": "这是一个示例备注",
            "weather": "晴天",
            "content": "这是日记内容"
        }
        serialized_data = pickle.dumps(data)
        ciphertext = self.crypto_manager.encrypt_data(serialized_data)
        plaintext = pickle.loads(self.crypto_manager.decrypt_data(ciphertext))
        assert plaintext == data
