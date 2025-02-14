import unittest
import os
import shutil
from unittest.mock import patch
from cryptography.hazmat.primitives.asymmetric import rsa
from utils.crypter import generate_rsa_keys, get_rsa_keys, encrypt_data, decrypt_data

class TestRSAKeys(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test_keys"
        os.makedirs(self.test_dir, exist_ok=True)
        with patch("your_module.config.get_config_value", return_value=self.test_dir):
            generate_rsa_keys()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_generate_rsa_keys(self):
        public_key_path = os.path.join(self.test_dir, "public_key.pem")
        private_key_path = os.path.join(self.test_dir, "private_key.pem")
        self.assertTrue(os.path.exists(public_key_path))
        self.assertTrue(os.path.exists(private_key_path))

    def test_get_rsa_keys(self):
        with patch("your_module.config.get_config_value", return_value=self.test_dir):
            public_key, private_key = get_rsa_keys()
            self.assertIsInstance(public_key, rsa.RSAPublicKey)
            self.assertIsInstance(private_key, rsa.RSAPrivateKey)

    def test_encrypt_decrypt(self):
        data = b"Hello, World!"
        ciphertext = encrypt_data(data)
        plaintext = decrypt_data(ciphertext)
        self.assertEqual(plaintext, data)

    def test_keys_not_exist(self):
        shutil.rmtree(self.test_dir)
        with patch("your_module.config.get_config_value", return_value=self.test_dir):
            public_key, private_key = get_rsa_keys()
            self.assertIsInstance(public_key, rsa.RSAPublicKey)
            self.assertIsInstance(private_key, rsa.RSAPrivateKey)

if __name__ == '__main__':
    unittest.main()