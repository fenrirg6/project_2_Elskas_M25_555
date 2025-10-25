from pathlib import Path

# current work dir
ALLOWED_DATA_TYPES = {'int', 'str', 'bool'}
DATA_DIR = Path.cwd() / 'src' / 'primitive_db' / 'data'
METADATA_FILE = Path.cwd() / 'src' / 'primitive_db' / 'db_meta.json'