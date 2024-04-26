from selenium import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor

def get_reviews(review_url):
    #chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Ensure GUI is off to prevent unnecessary resource usage
    driver = webdriver.Chrome()#options=chrome_options)  # Create a new driver instance for each thread
    driver.get(review_url)
    print ("\n\nFetching reviews from --> ", review_url)
    # Find the review elements
    review_elements = driver.find_elements(By.XPATH, '//div[starts-with(@id, "customer_review-")]//div[@class="a-row a-spacing-small review-data"]//span[@data-hook="review-body"]/span')
    # Get the text from the first 5 review elements, or all of them if there are less than 5
    reviews = [review.text.strip() for review in review_elements[:5]]
    driver.quit()  # Don't forget to quit the driver when you're done
    return reviews

def get_product_name_and_reviews(url):
    #chrome_options = Options()
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome()#options=chrome_options)
    driver.get(url)
    content = ""

    try:
        # Wait until the element with ID 'productTitle' is located
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "productTitle")))
        title_element = driver.find_element(By.ID, "productTitle")
        product_name = title_element.text.strip()
        content = f'PRODUCT NAME: {product_name} \n\n'
        print ("\nProduct Name --> ", product_name)
        # Now that the main page is loaded, open the review pages
        base_url = url.rsplit('/dp/', 1)[0]
        product_id = url.split('/')[-1]
        review_urls = [f'{base_url}/product-reviews/{product_id}?filterByStar={i}_star' for i in ['one', 'two', 'three', 'four', 'five']]
        # print (review_urls)
        with ThreadPoolExecutor() as executor:
            review_texts = list(executor.map(get_reviews, review_urls))
        return product_name, list(review_texts), content

    except:
        return "Product name not found", [], ""

    finally:
        driver.quit()

def sanitizeURL (url):
    parts = url.split("/")
    # Assign the variables
    baseURL = parts[2]
    productName = parts[3]
    productID = parts[5][:10]
    return (f"https://{baseURL}/{productName}/dp/{productID}")