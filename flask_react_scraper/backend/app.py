from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import os
import zipfile
import io
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from the React front-end

# Configure stdout to handle UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    link_url = data['url']
    
    # Send a GET request to the webpage
    response = requests.get(link_url)
    
    # Check if the request was successful
    if response.status_code != 200:
        return jsonify({"error": f"Failed to retrieve the webpage. Status code: {response.status_code}"}), 400

    # Parse the webpage content
    soup = BeautifulSoup(response.text, 'html.parser')

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
    
    # Function to download a file
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def download_file(url, output_path):
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive new chunks
                        f.write(chunk)

    # Create a buffer for the zip file
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for text, url in audio_links_dict.items():
            filename = f"{text}.mp3"  # Use the text as filename
            output_path = os.path.join(directory_name, filename)
            try:
                print(f"Downloading {text} from {url}")
                audio_data = requests.get(url, stream=True).content
                zip_file.writestr(filename, audio_data)
            except requests.RequestException as e:
                print(f"Failed to download {url}: {e}")
                continue

    zip_buffer.seek(0)

    return send_file(zip_buffer, as_attachment=True, download_name=f"{directory_name}.zip", mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True)