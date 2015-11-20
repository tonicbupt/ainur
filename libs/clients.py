# coding: utf-8

from gitlab import Gitlab
from eruhttp import EruClient

from config import GITLAB_TOKEN, ERU_URL

gitlab = Gitlab('http://git.hunantv.com', token=GITLAB_TOKEN, verify_ssl=False)
eru = EruClient(ERU_URL)
