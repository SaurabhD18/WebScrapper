import sys
import os
from bs4 import BeautifulSoup
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


# URL of the webpage you want to scrape
link_url = "https://radheshyamdas.com/senior-vaishnavas-vani/hh-radhanath-swami-maharaj/level-4---7-8th-semester"

# Reconfigure the standard output to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Send a GET request to the webpage
response = requests.get(link_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the webpage content
    soup = BeautifulSoup(response.text, 'lxml')

    # Print the parsed HTML text (or perform further operations with BeautifulSoup)
    # print(soup.prettify())
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")



# Find all <h3> tags
h3_tags = soup.find_all('h3')

audio_links_dict = {}

# Iterate through each h3 tag
for h3_tag in h3_tags:
    # Find all <a> tags with target="_blank" within the current <h3> tag
    target_blank_a_tags = h3_tag.find_all('a', target='_blank')
    # Extract href attribute values for all found <a> tags
    for a_tag in target_blank_a_tags:
        # Get the text of the <a> tag
        text = h3_tag.text.strip()
        # Get the value of the href attribute
        href_value = a_tag.get('href')
        # Store the text and href_value in the dictionary
        audio_links_dict[text] = href_value


# Find the <div> with class "breadcrumbs"
breadcrumbs_div = soup.find('div', class_='breadcrumbs')

# Find all <a> tags within the breadcrumbs_div
a_tags = breadcrumbs_div.find_all('a')

# Extract text from <a> tags and join them with ' || ' to create the directory name
directory_name = '_'.join([a.get_text(strip=True) for a in a_tags])

os.makedirs(directory_name, exist_ok=True)



# Function to download a file
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(requests.exceptions.RequestException))
def download_file(url, output_path):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    f.write(chunk)



for text, url in audio_links_dict.items():
    filename = f"{text}.mp3"  # Use the text as filename
    output_path = os.path.join(directory_name, filename)
    print(f"Downloading {text} from {url} to {output_path}")
    download_file(url, output_path)

