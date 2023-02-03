from bs4 import BeautifulSoup
import requests
import csv

base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1'
csv_header = ['Product URL', 'Product name ', 'Product Price', 'Rating', 'No.Of Reviews', 'Description', 'Manufacturer', 'ASIN']

def getPage(url):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    page = requests.get(url, headers=headers)

    # retry if page retrieval failed
    if(page.status_code != 200):
        return getPage(url)

    return page

def getProductDescription(soup_prettify):
    div_description = soup_prettify.find("div", {"id": "feature-bullets"})
    ul = div_description.find("ul")
    product_description = ""
    for li in ul.find_all("li"):
        span = li.find("span")
        if span:
            li_text = span.text.strip()
            product_description = product_description + li_text + ". "
    print(product_description)
    return product_description


def getProductDetails(url):
    try:
        page = getPage(url)
        soup_content = BeautifulSoup(page.content, "html.parser")
        soup_prettify = BeautifulSoup(soup_content.prettify(), "html.parser")

        div_description = soup_prettify.find("div", {"id": "feature-bullets"})
        ul = div_description.find("ul")
        product_description = ""
        for li in ul.find_all("li"):
            span = li.find("span")
            if span:
                li_text = span.text.strip()
                product_description = product_description + li_text + ". "

        manufacturer = ""
        asin = ""
        div_manufacturer = soup.find("div", {"id": "detailBullets_feature_div"})
        span_list = div_manufacturer.find_all("span", class_="a-list-item")
        for span in span_list:
            if "Manufacturer" in span.find("span", class_="a-text-bold").get_text():
                span_details = span.find_all("span")
                manufacturer = span_details[1].get_text()
            if "ASIN" in span.find("span", class_="a-text-bold").get_text():
                span_details = span.find_all("span")
                asin = span_details[1].get_text()
        return product_description, manufacturer, asin
    except Exception as e:
        return getProductDetails(url)


def generateProductInsights(url, csv_writer):
    try: 
        page = getPage(url)
        soup_content = BeautifulSoup(page.content, "html.parser")
        soup_prettify = BeautifulSoup(soup_content.prettify(), "html.parser")
        div_lists = soup_prettify.find_all('div', class_="sg-col-inner")
        data = []
        for div in div_lists:
            if div.find('span', class_ = "a-size-medium a-color-base a-text-normal") and div.find('span', class_ = "a-offscreen") and div.find('i', class_ = "a-icon a-icon-star-small a-star-small-4-5 aok-align-bottom") and div.find('span', class_ = "a-size-base s-underline-text"):
                product_url = "https://www.amazon.in" + div.find('a', class_ = "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal").get('href')
                product_name = div.find('span', class_ = "a-size-medium a-color-base a-text-normal").get_text()
                product_price = div.find('span', class_ = "a-offscreen").get_text()
                rating = div.find('i', class_ = "a-icon a-icon-star-small a-star-small-4-5 aok-align-bottom").get_text()
                no_of_reviews = div.find('span', class_ = "a-size-base s-underline-text").get_text()

                product_name = product_name.strip()
                product_price = product_price.strip()[1:]
                rating = rating.strip()
                no_of_reviews = no_of_reviews.strip()

                product_description, manufacturer, asin = getProductDetails(product_url)
                print(product_description, manufacturer, asin)
                data.append([product_url, product_name, product_price, rating, no_of_reviews, product_description, manufacturer, asin])

        csv_writer.writerows(data)
        print(data)

        # finding out the next page from pagination bar and fetching data using recursion
        next_page_url = ""
        if soup_prettify.find('a', class_ = "s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"):
            next_page_url = "https://www.amazon.in" + soup_prettify.find('a', class_ = "s-pagination-item s-pagination-next s-pagination-button s-pagination-separator").get('href')
        if next_page_url:
            generateProductInsights(next_page_url, csv_writer)
        
    except Exception as e:
        generateProductInsights(url, csv_writer)


if __name__ == "__main__":
    fp = open('product.csv', 'w') 

    csv_writer = csv.writer(fp)
    csv_writer.writerow(csv_header)
    
    generateProductInsights(base_url, csv_writer)
    # getProductDetails()
    fp.close()