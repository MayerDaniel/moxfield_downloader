import requests
import os
import re
import argparse
import random

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
    "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; Trident/5.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; MDDCJS)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
]

# Function to fetch deck data from Moxfield
def get_deck_data(moxfield_deck_id):
    url = f"https://api.moxfield.com/v2/decks/all/{moxfield_deck_id}"
    response = requests.get(url, headers = {'User-agent': random.choice(user_agent_list)})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch deck: {response.status_code}")

# Function to get card art from Scryfall API
def get_card_image_url(id, card_name):
    search_url = f"https://api.scryfall.com/cards/{id}"
    response = requests.get(search_url)
    if response.status_code == 200:
        card_data = response.json()
        return card_data['image_uris']['normal']  # You can choose other image sizes
    else:
        print(f"Failed to fetch card: {id}, {response.status_code}. Trying to search by name - MAKE SURE THE ART IS RIGHT FOR {card_name.upper()}!")
        search_url = f"https://api.scryfall.com/cards/named?exact={card_name}"
        response = requests.get(search_url)
        if response.status_code == 200:
            card_data = response.json()
            return card_data['image_uris']['normal']  # You can choose other image sizes
        else:
            print(f"Failed to fetch card: {card_name}, {response.status_code}")
            return None

# Function to clean up the folder name (remove invalid characters)
def clean_folder_name(name):
    # Remove any characters that are not alphanumeric or spaces
    return re.sub(r'[^\w\s]', '', name).strip()

# Function to download image
def download_image(url, filename, folder):
    filename = filename.replace('/', '|')
    if not os.path.exists(folder):
        os.makedirs(folder)
    img_data = requests.get(url).content
    with open(os.path.join(folder, filename), 'wb') as handler:
        handler.write(img_data)
    print(f"Downloaded {filename} to {folder}")

# Extract Moxfield deck ID from URL
def extract_deck_id(moxfield_url):
    # The deck ID typically comes after "decks/" in the Moxfield URL
    pattern = r"/decks/([\w-]+)"
    match = re.search(pattern, moxfield_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Moxfield URL format. Could not extract deck ID.")

# Main function to download all card arts for a deck
def download_deck_card_images(moxfield_deck_id):
    # Get the deck data from Moxfield
    deck_data = get_deck_data(moxfield_deck_id)

    # Extract the deck name and clean it up
    deck_name = clean_folder_name(deck_data['name'])

    # Extract card names from the mainboard (adjust if you need sideboard, commanders, etc.)
    card_slots = deck_data['mainboard']

    # For each card, get the image URL from Scryfall and download the image
    for card_name, card in card_slots.items():
        card_id = card['card']['scryfall_id']
        card_image_url = get_card_image_url(card_id, card_name)
        if card_image_url:
            # Use the deck name as the folder
            download_image(card_image_url, f"{card_name}.jpg", folder=deck_name)

if __name__ == "__main__":
    # Setup argparse to take the Moxfield URL as an argument
    parser = argparse.ArgumentParser(description="Download Magic: The Gathering card art for a Moxfield deck.")
    parser.add_argument("moxfield_url", type=str, help="The URL of the Moxfield deck")

    args = parser.parse_args()

    # Extract deck ID from the provided URL
    moxfield_deck_id = extract_deck_id(args.moxfield_url)

    # Download card images
    download_deck_card_images(moxfield_deck_id)
