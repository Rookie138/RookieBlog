from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


class PwdHashUtil:

    @staticmethod
    def hash_password(password):
        hash_password = password_hash.hash(password)
        return hash_password

    @staticmethod
    def verify_password(password, hashed_password):
        return password_hash.verify(password, hashed_password)