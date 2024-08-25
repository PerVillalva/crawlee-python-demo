import asyncio

from crawlee.playwright_crawler.playwright_crawler import PlaywrightCrawler

from .routes import router


async def main() -> None:
    """The crawler entry point."""
    crawler = PlaywrightCrawler(
        browser_type='firefox',
        headless=True,
        request_handler=router,
    )

    await crawler.run(
        [
            'https://phones.mintmobile.com/',
        ]
    )
    
    await crawler.export_data('mintmobile_output.csv')


if __name__ == '__main__':
    asyncio.run(main())
