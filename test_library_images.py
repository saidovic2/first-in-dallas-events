import requests
from bs4 import BeautifulSoup

url = 'https://dallaslibrary.librarymarket.com/event/happy-holidays-479360'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')

print(f"Testing: {url}\n")

# Find all images
imgs = soup.find_all('img')
print(f"Found {len(imgs)} img tags:\n")

for i, img in enumerate(imgs[:15], 1):
    src = img.get('src', '')
    alt = img.get('alt', '')
    print(f"{i}. SRC: {src[:100]}")
    print(f"   ALT: {alt[:80]}")
    print()

# Check for field-items with images
field_images = soup.find_all('div', class_='field-type-image')
print(f"\nFound {len(field_images)} field-type-image divs")

# Check for event images
event_img = soup.find('div', class_='field-name-field-event-image')
if event_img:
    print("\nFound field-name-field-event-image!")
    img = event_img.find('img')
    if img:
        print(f"Image src: {img.get('src')}")
