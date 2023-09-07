from os import path
import dotenv

dotenv_path = path.join(path.abspath(path.dirname(__file__)), '.env')
if not path.exists(dotenv_path):
    raise FileNotFoundError(('`.env` file not found. `.env` is added to .gitignore, so please add the '
                             '`.env` file manually containing the appropriate environment variables '
                             'next to the `project_config.py`. Check out project README for more info.'))
ENV_VARS = dotenv.dotenv_values(dotenv_path)

"""
Full project configuration for paths and other.
"""
# main code dir
BASE_CODE_DIR = path.abspath(ENV_VARS['CODE_DIR'])

# data dir
BASE_DATA_DIR = path.abspath(ENV_VARS['DATA_DIR'])
BASE_RAW_DATA_DIR = path.join(BASE_DATA_DIR, 'raw')
BASE_INTERIM_DATA_DIR = path.join(BASE_DATA_DIR, 'interim')
BASE_PROCESSED_DATA_DIR = path.join(BASE_DATA_DIR, 'processed')
BASE_EXTERNAL_DATA_DIR = path.join(BASE_DATA_DIR, 'external')
DATABASE_DIR = path.join(BASE_DATA_DIR, 'processed')

# artifact dirs
BASE_ARTIFACTS_DIR = path.abspath(ENV_VARS['ARTIFACTS_DIR'])
HUGGING_FACE_CACHE_DIR = path.join(BASE_ARTIFACTS_DIR, 'hugging_face_cache')