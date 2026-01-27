import time
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger("app")

def encrypt_timestamp(password:str):
    # 生成密钥
    salt = b'salt_'  # 使用一个固定的盐，或者随机生成
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=10000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    # 创建Fernet实例
    f = Fernet(key)
    
    # 获取当前时间戳并加密
    current_timestamp = str(int(time.time())).encode()
    encrypted_timestamp = f.encrypt(current_timestamp)
    
    return encrypted_timestamp.decode()

def decrypt_and_validate(encrypted_string:str, password:str):
    # 生成密钥
    salt = b'salt_'  # 使用与加密时相同的盐
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=10000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    # 创建Fernet实例
    f = Fernet(key)
    
    try:
        # 解密时间戳
        decrypted_timestamp = f.decrypt(encrypted_string.encode())
        original_timestamp = int(decrypted_timestamp.decode())
        
        # 获取当前时间戳
        current_timestamp = int(time.time())
        
        # 检查时间间隔
        time_difference = current_timestamp - original_timestamp
        
        if time_difference < 60:
            return True
    except Exception as e:
        logger.warn(f"task deliver error: unknow worker attempt to get task. {e}")
        return False

if __name__ == '__main__':


    # 使用示例
    encrypted = encrypt_timestamp('qsar')
    print("Encrypted timestamp:", encrypted)

    # # 等待一些时间（例如，5秒）
    # time.sleep(5)

    valid = decrypt_and_validate(encrypted,"qsar")
    print("Validation result:", valid)