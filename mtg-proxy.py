
from PIL import Image
import os
import requests
import os.path
from os import path
import argparse

pageWidth = 2480
pageHeight = 3508
cardWidth = 750
cardHeight = 1038
leftOffset = 115
topOffset = 197

DEFAULT_CARD_FILE = 'cards.txt'
DEFAULT_OUT_FILE = 'out.pdf'

card_file = DEFAULT_CARD_FILE
out_file = DEFAULT_OUT_FILE


def get_image_by_name(name):
    api_url = "https://api.scryfall.com/cards/search?q=name=!\"" + name + "\"&unique=prints"

    data = {}
    headers = {}

    response = requests.get(api_url, json=data, headers=headers)

    if (response.status_code == 200):
        for i in range(response.json()["total_cards"]):
            if(response.json()["data"][i]["highres_image"] is True):
                return response.json()["data"][i]["image_uris"]["large"]

    return None


def process_arguments():
    parser = argparse.ArgumentParser(description='Generates a PDF for proxy print of MTG.')

    parser.add_argument('--cards', help='File with card names.')
    parser.add_argument('--out', help='Name of the file to export.')

    args = parser.parse_args()

    if (args.cards is not None):
        global card_file
        card_file = args.cards

    if (args.out is not None):
        global out_file
        out_file = args.out


def read_card_file():
    if(path.exists(os.getcwd() + "/" + card_file)):
        f = open(card_file, "r")
        lines = f.read().splitlines()
        f.close()
        return lines
    else:
        print(card_file + " not found")
        exit()


def resize_image(image):
    basewidth = cardWidth
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    img = image.resize((basewidth, hsize), Image.Resampling.LANCZOS)
    return img


def get_image_from_directory(name):
    for ext in [".jpg", ".png", ".jpeg"]:
        image_path = os.getcwd() + "/" + name + ext
        if(path.exists(image_path)):
            image = Image.open(image_path)
            return resize_image(image)
    return None


def get_images_from_cards(cards):
    images = []
    for card in cards:
        image = get_image_from_directory(card)
        if(image is not None):
            images.append(image)
        else:
            # Not found image on directory
            image_url = get_image_by_name(card)
            if image_url is not None:
                image = Image.open(requests.get(image_url, stream=True).raw)
                img = resize_image(image)
                images.append(img)
            else:
                print("Card not found: ", card)

    return images


def generate_output(images):
    all_images = []

    card_remaining = len(images)
    card_index = 0

    while card_remaining > 0:
        dst = Image.new('RGB', (pageWidth, pageHeight), "white")
        for i in range(3):
            for j in range(3):
                if(card_index < len(images)):
                    dst.paste(images[card_index], (j*cardWidth + leftOffset, i*cardHeight + topOffset))
                    card_remaining -= 1
                else:
                    break
                card_index += 1

        all_images.append(dst.copy())

    all_images[0].save(out_file, "PDF", resolution=300.0, save_all=True, append_images=all_images[1:])

    print(len(images), " cards exported")


def main():

    process_arguments()

    cards = read_card_file()

    images = get_images_from_cards(cards)

    generate_output(images)


if __name__ == "__main__":
    main()
