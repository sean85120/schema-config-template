import os
from models.DotenvSchema import DotenvSchema
from schematized_config.core import ConfigValidator
from fs.osfs import OSFS

Config = DotenvSchema(**ConfigValidator.load_dotenv(
    'schemas/dotenv.schema.json',
    '.env',
    storage_driver=OSFS(os.path.dirname(__file__))))

