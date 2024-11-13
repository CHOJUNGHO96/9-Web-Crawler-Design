from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncIterator
from redis import asyncio as aioredis
from urllib.parse import urlparse
import logging


class UncollectedUrlRepository:
    def __init__(self, logger: logging.Logger, rdb_session: AsyncSession, redis_db: AsyncIterator[aioredis.Redis]):
        self.logger = logger
        self.rdb_session = rdb_session
        self.redis_db = redis_db

    async def assign_to_domain_queue(self, url: str) -> None:
        """
        넘어온 URL 도메인만 추출하여 큐에 넣는 함수
        :param url: 큐에 넣을 URL
        :return: None
        """
        domain: str = urlparse(url).hostname
        if domain is None:
            self.logger.warning(f"Invalid URL: {url}")
            return

        async with self.redis_db as redis:
            self.logger.info(f"Assign to domain queue: {domain}")
            await redis.lpush(domain, url)
            await redis.sadd("domain_queue_list", domain)
