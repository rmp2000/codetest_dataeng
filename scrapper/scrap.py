import requests
from bs4 import BeautifulSoup
import json

def scrap_dress_page(url):
    
    data_dict = {}
    # Send a GET request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Initialize BeautifulSoup object with the response text
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        print("Failed to fetch the webpage. Status code:", response.status_code)

    # Using more specific CSS selectors to target the div correctly
    details_div = soup.select_one('.Collapsible.Collapsible--large .Collapsible__Content')

    data_dict['roduct_url']=url
    # Extracting the product name
    product_name = soup.find('h1', class_='ProductMeta__Title')
    if product_name:
        data_dict['product_name'] = product_name.text.strip()
    
    # Extracting the product price
    product_price = soup.find('span', class_='ProductMeta__Price')
    if product_price:
        data_dict['price'] = product_price.text.strip()

    # Extracting the product sku
    product_sku = soup.find('span', class_='ProductMeta__SkuNumber')
    if product_sku:
        data_dict['sku'] = product_sku.text.strip()

    # Extracting the product meta data   
    product_meta_data = soup.find('div', class_='ProductMeta__Description')
    # Extract the <li> elements
    li_elements = product_meta_data.find_all('li')
    # Extract the text from each <li> element and store in a list
    li_texts = [li.get_text() for li in li_elements]
    # Create the data dictionary
    data_dict['metadata']= li_texts

    # Extracting the product images url 
    images = []
    img_tags = soup.find_all('img', class_='Image--fadeIn')
    for img_tag in img_tags:
        img_src = img_tag.get('data-original-src')
        # add https if needed
        if img_src.startswith("//"):
            img_src = "https:" + img_src
        images.append(img_src)
    data_dict['images']= images

    # Extracting the product sizes
    labels_text = []
    num = 0
    while True:
        selector = f"label.SizeSwatch[for='option-product-template-1-{num}']" #selector to get the correct labels
        label_element = soup.select_one(selector)
        if label_element is None:
            break
        label_text = label_element.text.strip()
        if '*' in label_text:
            label_text = label_text.replace('*', '') # clean the sizes
        labels_text.append(label_text)
        num += 1
    data_dict['sizes']= labels_text

    return data_dict

if __name__ == "__main__":
    url_father='https://en.gb.scalperscompany.com/collections/woman-new-collection-skirts-2060'
    response = requests.get(url_father)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all <a> elements that have the specified class and href starting with '/products/'
    product_links = soup.find_all('a', class_='ProductItem__ImageWrapper', href=lambda href: href and href.startswith('/products/'))
    scraped_results=[]
    # Iterate over each found link
    for link in product_links:
        # Build the full URL
        full_url = 'https://en.gb.scalperscompany.com' + link['href']
        # Call the function to scrape the page for each dress
        
        scraped_data = scrap_dress_page(full_url)
        scraped_results.append(scraped_data)

    # Write all scraped results to a JSON file
    with open('scraped_data.json', 'a') as f:
        json.dump(scraped_results, f, indent=4)
        f.write('\n')
