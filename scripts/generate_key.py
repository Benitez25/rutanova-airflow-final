"""Generate an unencrypted PKCS8 key for this local lab; never commit it."""
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
root = Path('/opt/airflow/secrets')
root.mkdir(exist_ok=True)
key_path = root / 'snowflake_key.p8'
if key_path.exists():
    raise SystemExit('Key exists. Register the existing public key; do not rotate accidentally.')
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
key_path.chmod(0o600)
public = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
(root / 'snowflake_public_key.txt').write_text(''.join(line for line in public.splitlines() if not line.startswith('---')) + '\n')
print('Generated key. Register the contents of secrets/snowflake_public_key.txt in Snowflake.')
