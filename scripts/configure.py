"""Create local configuration without printing or committing secrets. Stdlib only."""
import base64
import os
from pathlib import Path
import secrets
ROOT = Path(__file__).resolve().parents[1]
def main():
    env = ROOT / '.env'
    if env.exists():
        raise SystemExit('.env already exists; edit it instead of regenerating secrets.')
    text = (ROOT / '.env.example').read_text()
    values = {
        'AIRFLOW_UID': str(os.getuid() if hasattr(os, 'getuid') else 50000),
        'POSTGRES_PASSWORD': secrets.token_hex(24),
        'AIRFLOW_FERNET_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
        'AIRFLOW_WEBSERVER_SECRET_KEY': secrets.token_hex(32),
        'AIRFLOW_ADMIN_PASSWORD': secrets.token_hex(16),
        'MINIO_ROOT_PASSWORD': secrets.token_hex(24),
        'MINIO_SECRET_KEY': secrets.token_hex(24),
    }
    lines = []
    for line in text.splitlines():
        key = line.split('=', 1)[0]
        lines.append(f'{key}={values[key]}' if key in values else line)
    env.write_text('\n'.join(lines) + '\n')
    if os.name != 'nt':
        env.chmod(0o600)
    for name in ['reports', 'secrets']:
        (ROOT / name).mkdir(exist_ok=True)
    if os.name != 'nt':
        (ROOT / 'reports').chmod(0o775)
    print('Created .env. Fill SNOWFLAKE_ACCOUNT. Local login values are in .env.')
if __name__ == '__main__':
    main()
