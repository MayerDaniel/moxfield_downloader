import stealth_requests as requests
import os
import re
import argparse
import random

# Headers from the original cURL request
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "dnt": "1",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "macOS",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

# Function to fetch deck data from Moxfield
def get_deck_data(moxfield_deck_id):
    url = f"https://api.moxfield.com/v2/decks/all/{moxfield_deck_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch deck: {response.status_code}")

# Function to clean up the folder name (remove invalid characters)
def clean_folder_name(name):
    return re.sub(r'[^\w\s]', '', name).strip()

# Function to download image
def download_image(url, filename, folder):
    filename = filename.replace('/', '|')
    if not os.path.exists(folder):
        os.makedirs(folder)
    img_data = requests.get(url, headers=HEADERS).content
    with open(os.path.join(folder, filename), 'wb') as handler:
        handler.write(img_data)
    print(f"Downloaded {filename} to {folder}")

# Extract Moxfield deck ID from URL
def extract_deck_id(moxfield_url):
    pattern = r"/decks/([\w-]+)"
    match = re.search(pattern, moxfield_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Moxfield URL format. Could not extract deck ID.")

# Main function to download all card arts for a deck
def download_deck_card_images(moxfield_deck_id):
    deck_data = get_deck_data(moxfield_deck_id)
    deck_name = clean_folder_name(deck_data['name'])
    for location in ['mainboard', 'sideboard', 'commanders', 'companions']:
        if location in deck_data:
            card_slots = deck_data[location]
            for card_name, card in card_slots.items():
                card_id = card['card']['scryfall_id']
                get_card_image(card_id, card_name, deck_name, location)
    

# Function to get card art from Scryfall API
def get_card_image(id, card_name, deck_name, location):
    search_url = f"https://api.scryfall.com/cards/{id}"
    folder = os.path.join(deck_name, location)
    response = requests.get(search_url, headers=HEADERS)
    if response.status_code == 200:
        card_data = response.json()
        if 'image_uris' not in card_data:
            if 'card_faces' in card_data:
                for face in card_data['card_faces']:
                    download_image(face['image_uris']['png'], f"{face['name']}.png", folder=folder)
            else:
                print(f"No image found for {id}")
        else:
            download_image(card_data['image_uris']['png'], f"{card_name}.png", folder=folder)
    else:
        print(f"Failed to fetch card: {id}, {response.status_code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download MTG card art for a Moxfield deck.")
    parser.add_argument("moxfield_url", type=str, help="The URL of the Moxfield deck")
    args = parser.parse_args()
    moxfield_deck_id = extract_deck_id(args.moxfield_url)
    download_deck_card_images(moxfield_deck_id)
