# Import required libraries
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

# Initialize a Flask web application
app = Flask(__name__)

# Define a function to extract metadata from a URL
def extract_metadata(url):
    try:
        # Send an HTTP GET request to the provided URL
        response = requests.get(url, headers={"User-Agent": "Your User-Agent"}) #To mimic the web browser
        response.raise_for_status()  # Raise an error for invalid HTTP responses

        # Parse the HTML content of the URL using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize metadata variables with default values
        title = 'No title found'
        description = 'No description found'
        thumbnail = ''

        # Extract the title from the page's title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text

        # Extract the description from standard meta tags or Open Graph meta tags
        description_tag = soup.find('meta', attrs={'name': 'description'})
        if description_tag:
            description = description_tag['content']
        elif (og_description := soup.find('meta', attrs={'property': 'og:description'})):
            description = og_description['content']

        # Extract the thumbnail (you might need to adjust this depending on the website's structure)
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        if og_image:
            thumbnail = og_image['content']

        # Return the extracted title, description, and thumbnail
        return title, description, thumbnail

    except requests.exceptions.RequestException as e:
        # Handle HTTP request errors
        return str(e), '', ''
    except Exception as e:
        # Handle other exceptions during the extraction process
        return 'An error occurred while extracting metadata.', '', ''

# Initialize a list to store the search history
search_history = []

# Define a Flask route for the root URL ('/') with support for GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def index():
    error = ''

    if request.method == 'POST':
        url = request.form['url']

        if not is_valid_url(url):
            error = 'Invalid URL. Please enter a valid URL.'
        else:
            title, description, thumbnail = extract_metadata(url)
            
            # Append the valid URL to the search history
            search_history.append(url)

            return render_template('result.html', title=title, description=description, thumbnail=thumbnail, error=error, search_history=search_history)

    return render_template('index.html', error=error, search_history=search_history)

def is_valid_url(url):
    # Use a simple validation logic to check if the URL starts with 'http://' or 'https://'
    return url.startswith('http://') or url.startswith('https://')

# Run the Flask application if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True)