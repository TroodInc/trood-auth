import hashlib


class AuthenticationService:
    @classmethod
    def get_password_hash(cls, password, unique_token):
        """
        Creates salted password hash
        """
        salted_str = password + unique_token
        return hashlib.sha512(salted_str.encode('utf-8')).hexdigest()

    @classmethod
    def authenticate(cls, account, password):
        password_hash = cls.get_password_hash(password, account.unique_token)
        return password_hash == account.pwd_hash
