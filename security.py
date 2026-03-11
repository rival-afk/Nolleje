from passlib.context import CryptoContext

pwd_context = CryptoContext(
  schemes=["bcrypt"],
  deprecated="auto"
)

def hash_password (password: str):
  return pwd_context.hash(password)

def verify_password (password: str, hash: str):
  return pwd_context.verify(password, hash)