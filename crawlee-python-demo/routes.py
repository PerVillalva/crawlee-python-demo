from crawlee.playwright_crawler import PlaywrightCrawlingContext
from crawlee.basic_crawler.router import Router
from crawlee.models import Request
from crawlee.storages import KeyValueStore

router = Router[PlaywrightCrawlingContext]()


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Default request handler."""
    
    # Select the last 'a' element from the list and get its text
    last_page_element = await context.page.query_selector('a.facetwp-page.last')
    last_page = await last_page_element.get_attribute('data-page') if last_page_element else None

    if last_page:
        last_page_number = int(last_page)
        # Enqueue all product links on the current page and label them as 'product'
        await context.add_requests(
            [
                Request.from_url(context.request.loaded_url + f'?_paged={i}', label='listing')
                for i in range(1, last_page_number + 1)
            ]
        )

@router.handler('listing')
async def listing_handler(context: PlaywrightCrawlingContext) -> None:
    """Listing request handler."""
    print(f'Processing {context.request.loaded_url}')
    
    # Enqueue all product links on the current page and label them as 'product'
    await context.enqueue_links(
        selector='a.button.product_type_variable', label='product'
    )
    

    
@router.handler('product')
async def product_handler(context: PlaywrightCrawlingContext) -> None:
    """Product request handler."""
    
    # Extract necessary elements
    page_title = await context.page.title()
    image_element = await context.page.query_selector('img.wp-post-image')
    name_element = await context.page.query_selector('h1.product_title')
    price_element = await context.page.query_selector('p.price > span > bdi')
    
    # Open the default key-value store.
    kvs = await KeyValueStore.open()
    
    # Capture the screenshot of the page using Playwright's API.
    screenshot = await context.page.screenshot()
    
    # Store the screenshot in the key-value store.
    await kvs.set_value(
        key = page_title,
        value = screenshot,
        content_type = 'image/png',
    )
    
    # Push the product data to Crawlee's data storage
    await context.push_data(
        {
            'url': context.request.loaded_url,
            'image': await image_element.get_attribute('src') if image_element else None,
            'name': await name_element.text_content() if name_element else None,
            'price': await price_element.text_content() if price_element else None,
        }
    )
