import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd
import base64
from io import BytesIO

def scrape_zomato_data(url):
    # Specify the path to the Chrome WebDriver executable
    webdriver_path = "{Webdriver_Location}"

    # Configure the Chrome WebDriver service
    service = Service(webdriver_path)

    # Launch the browser
    driver = webdriver.Chrome(service=service)

    # Open the webpage
    driver.get(url)

    # Wait for the page to load
    time.sleep(3)

    # Scroll to the bottom of the page
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.find_element_by_tag_name('body').send_keys(Keys.END)
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Get the page source after scrolling
    page_source = driver.page_source

    # Close the browser
    driver.quit()

    # Create BeautifulSoup object from the page source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all divs with class "jumbo-tracker"
    tracker_divs = soup.find_all('div', class_='jumbo-tracker')

    # Create a list to store the restaurant data dictionaries
    data_list = []

    # Iterate over the tracker divs
    for tracker_div in tracker_divs:
        restaurant_data = {}

        # Find the second A tag inside the tracker div for restaurant name
        a_tags = tracker_div.find_all('a')
        if len(a_tags) >= 2:
            second_a_tag = a_tags[1]

            # Find the first div inside the second A tag for restaurant name
            divs = second_a_tag.find_all('div')
            if len(divs) >= 1:
                first_div = divs[0]

                # Find the H4 tag inside the first div for restaurant name
                h4_tag = first_div.find('h4')
                if h4_tag:
                    restaurant_name = h4_tag.text.strip()
                    restaurant_data['Name'] = restaurant_name
                else:
                    restaurant_data['Name'] = "N/A"

            # Find the second A tag inside the tracker div for type of restaurant
            if len(a_tags) >= 2:
                second_a_tag = a_tags[1]

                # Find the P tags inside the second A tag for type of restaurant
                p_tags = second_a_tag.find_all('p')
                if len(p_tags) >= 1:
                    type_of_restaurant = p_tags[0].text.strip()
                    restaurant_data['Type of Restaurant'] = type_of_restaurant
                else:
                    restaurant_data['Type of Restaurant'] = "N/A"

            # Find the second A tag inside the tracker div for cost
            if len(a_tags) >= 2:
                second_a_tag = a_tags[1]

                # Find the P tags inside the second A tag for cost
                p_tags = second_a_tag.find_all('p')
                if len(p_tags) >= 2:
                    cost = p_tags[1].text.strip()
                    restaurant_data['Cost'] = cost
                else:
                    restaurant_data['Cost'] = "N/A"

            # Find the second A tag inside the tracker div for location
            if len(a_tags) >= 2:
                second_a_tag = a_tags[1]

                # Find the P tags inside the second A tag for location
                p_tags = second_a_tag.find_all('p')
                if len(p_tags) >= 3:
                    location = p_tags[2].text.strip()
                    restaurant_data['Location'] = location
                else:
                    restaurant_data['Location'] = "N/A"

            # Find the Div with class="sc-1q7bklc-1 cILgox" for ratings
            ratings_div = tracker_div.find('div', class_='sc-1q7bklc-1 cILgox')
            if ratings_div:
                ratings = ratings_div.text.strip()
                restaurant_data['Ratings'] = ratings
            else:
                restaurant_data['Ratings'] = "N/A"

        # Append the restaurant data dictionary to the list
        data_list.append(restaurant_data)

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data_list)

    return df

# Create a Streamlit app
def main():
    st.title("Zomato Restaurant Data Scraper")

    # Get the URL input from the user
    url = st.text_input("Enter the Zomato URL to scrape")

    if st.button("Scrape"):
        if url:
            st.info("Scraping in progress...")
            df = scrape_zomato_data(url)
            if not df.empty:
                st.success("Scraping completed successfully!")

                # Fill blank entries with "N/A"
                df.fillna("N/A", inplace=True)

                # Create a BytesIO buffer for Excel file
                excel_buffer = BytesIO()

                # Create Excel writer using the buffer
                excel_writer = pd.ExcelWriter(excel_buffer, engine="xlsxwriter")
                df.to_excel(excel_writer, index=False)
                excel_writer.close()
                excel_buffer.seek(0)

                # Create a button to download the Excel file
                button_label = "Download Excel File"
                button_text = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(excel_buffer.read()).decode()}" download="restaurant_data.xlsx">{button_label}</a>'
                st.markdown(button_text, unsafe_allow_html=True)
            else:
                st.warning("No data found. Please check the URL or try a different one.")
        else:
            st.error("Please enter a valid URL.")

# Run the Streamlit app
if __name__ == '__main__':
    main()
