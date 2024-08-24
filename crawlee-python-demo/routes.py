from crawlee.beautifulsoup_crawler import BeautifulSoupCrawlingContext
from crawlee.basic_crawler.router import Router
from crawlee.models import Request

router = Router[BeautifulSoupCrawlingContext]()


@router.default_handler
async def default_handler(context: BeautifulSoupCrawlingContext) -> None:
    """Default request handler."""
    
    # Select all 'a' elements with a title attribute containing the word "Page"
    elements = context.soup.select('#searchPagination div:nth-child(2) > span > a[title*="Page"]')

    # Select the last 'a' element from the list and get its text
    last_page_text = elements[-1].text if elements else None
    
    if last_page_text:
        last_page_number = int(last_page_text)
        
        # Enqueue all product links in the current page and label them as 'product'
        await context.add_requests(
            [
                Request.from_url(context.request.loaded_url + f'?p={i}', label='listing')
                for i in range(0, last_page_number)
            ]
        )

@router.handler('listing')
async def listing_handler(context: BeautifulSoupCrawlingContext) -> None:
    """Listing request handler."""
    print(f'Processing {context.request.loaded_url}')
    # Enqueue all product links in the current page and label them as 'product'
    await context.enqueue_links(
        selector='a[itemprop="url"]', label='product'
    )

    
@router.handler('product')
async def product_handler(context: BeautifulSoupCrawlingContext) -> None:
    """Product request handler."""
    
    # Extract necessary elements
    brand_element = context.soup.select_one('h1 > div > span[itemprop="brand"] > a[itemprop="url"]')
    name_element = context.soup.select_one('h1 > div > span[itemprop="brand"] + span')
    price_element = context.soup.select_one('span[itemprop="price"]')
    
    # Push the product data to Crawlee's data storage
    await context.push_data(
        {
            'url': context.request.loaded_url,
            'brand': brand_element.text if brand_element else None,
            'name': name_element.text if name_element else None,
            'current_price': price_element.attrs['content'] if price_element else None,
        }
    )
