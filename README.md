## 文件结构


### CryptoManager 功能概述

`CryptoManager` 提供 RSA 加密和解密功能，核心方法如下：

1. **密钥管理** ：

* `generate_rsa_keys()`: 生成并保存公钥和私钥。
* `load_rsa_keys()`: 加载现有密钥。

1. **数据加密与解密** ：

* `encrypt_data(data: bytes)`: 使用公钥加密数据。
* `decrypt_data(ciphertext: bytes)`: 使用私钥解密数据。
