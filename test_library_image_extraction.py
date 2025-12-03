import requests
from bs4 import BeautifulSoup

# Test a few library event URLs to see what images are available
test_urls = [
    'https://dallaslibrary.librarymarket.com/event/awkward-family-photos-469011',
    'https://dallaslibrary.librarymarket.com/event/booker-t-high-school-audition-workshops-443396',
    'https://dallaslibrary.librarymarket.com/event/christmas-book-flood-jolabokaflod-443397'
]

for url in test_urls:
    print(f"\n{'='*80}")
    print(f"Testing: {url.split('/')[-1]}")
    print('='*80)
    
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Method 1: Event image field
    event_image_div = soup.find('div', class_='field-name-field-event-image')
    if event_image_div:
        img = event_image_div.find('img')
        if img:
            print(f"✅ Method 1 (field-name-field-event-image): {img.get('src', 'NO SRC')}")
    
    # Method 2: Field type image
    image_field = soup.find('div', class_='field-type-image')
    if image_field:
        img = image_field.find('img')
        if img:
            print(f"✅ Method 2 (field-type-image): {img.get('src', 'NO SRC')}")
    
    # Method 3: All images
    all_imgs = soup.find_all('img')
    print(f"\n📊 Total images found: {len(all_imgs)}")
    for i, img in enumerate(all_imgs[:5], 1):
        src = img.get('src', '')
        alt = img.get('alt', '')
        width = img.get('width', 'auto')
        print(f"  {i}. SRC: {src[:80]}")
        print(f"     ALT: {alt[:60]}")
        print(f"     WIDTH: {width}")
    
    # Method 4: Meta image
    meta_image = soup.find('meta', property='og:image')
    if meta_image:
        print(f"\n🔍 Meta og:image: {meta_image.get('content', 'NO CONTENT')}")
