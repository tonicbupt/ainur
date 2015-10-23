from gitlab import Gitlab
from eruhttp import EruClient

from config import GITLAB_TOKEN, ERU_URL

if not GITLAB_TOKEN:
    raise ValueError('Gitlab token not specified')
if not ERU_URL:
    raise ValueError('Eru url not specified')

gitlab = Gitlab('http://git.hunantv.com', token=GITLAB_TOKEN, verify_ssl=False)
eru = EruClient(ERU_URL)
