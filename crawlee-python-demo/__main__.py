import asyncio

from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler

from .routes import router


async def main() -> None:
    """The crawler entry point."""
    crawler = BeautifulSoupCrawler(
        request_handler=router,
        max_requests_per_crawl=15,
    )

    await crawler.run(
        [
            'https://www.zappos.com/men/OgL9CsABAuICAhgH.zso',
        ]
    )
    
    await crawler.export_data('output.csv')


if __name__ == '__main__':
    asyncio.run(main())
