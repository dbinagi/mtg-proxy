
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
DEFAULT_IMAGES_FOLDER = 'images'

card_file = DEFAULT_CARD_FILE
out_file = DEFAULT_OUT_FILE
images_folder = DEFAULT_IMAGES_FOLDER


class Card:

    def __init__(self, name, amount, set, image):
        self.name = name
        self.amount = amount
        self.set = set
        self.image = image


def get_image_by_name(card):

    api_url = "https://api.scryfall.com/cards/search?q=name=\"" + card.name + "\"&unique=prints"

    if (card.set is not None):
        api_url = "https://api.scryfall.com/cards/search?q=name=\"" + card.name + "\"+e:" + card.set + "&unique=prints"

    data = {}
    headers = {}

    response = requests.get(api_url, json=data, headers=headers)

    if (response.status_code == 200):
        for i in range(len(response.json()["data"])):
            double_face = False
            if "card_faces" in response.json()["data"][i]:
                double_face = True

            if(response.json()["data"][i]["highres_image"] is True):
                if double_face:
                    if response.json()["data"][i]["card_faces"][0]["name"].upper() == card.name.upper():
                        return response.json()["data"][i]["card_faces"][0]["image_uris"]["large"]
                else:
                    if response.json()["data"][i]["name"].upper() == card.name.upper():
                        return response.json()["data"][i]["image_uris"]["large"]

    return None


def process_arguments():
    parser = argparse.ArgumentParser(description='Generates a PDF for proxy print of MTG.')

    parser.add_argument('--cards', help='File with card names.')
    parser.add_argument('--out', help='Name of the file to export.')
    parser.add_argument('--images', help='Path to images folders.')

    args = parser.parse_args()

    if (args.cards is not None):
        global card_file
        card_file = args.cards

    if (args.out is not None):
        global out_file
        out_file = args.out

    if (args.images is not None):
        global images_folder
        images_folder = args.images


def read_card_file():

    cards = []

    if(path.exists(os.getcwd() + "/" + card_file)):
        f = open(card_file, "r")
        lines = f.read().splitlines()
        for line in lines:
            has_set = False
            set = None

            if ('[' in line):
                has_set = True
                set = line[line.index("[") + 1:len(line) - 1]

            name = line[line.index(' ') + 1: line.index('[') if has_set else len(line)]
            amount = line[0: line.index(' ')]

            card = Card(name, amount, set, None)
            cards.append(card)

        f.close()
        return cards
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
        image_path = os.getcwd() + "/" + images_folder + "/" + name + ext
        if(path.exists(image_path)):
            image = Image.open(image_path)
            return resize_image(image)
    return None


def get_images_from_cards(cards):
    card_index = 1
    for card in cards:
        image = get_image_from_directory(card.name)
        if(image is not None):
            card.image = image
            print("%03d" % (card_index,) + "/" + "%03d" % (len(cards),) + "  From Directory:  " + card.name)
        else:
            # Not found image on directory
            image_url = get_image_by_name(card)
            if image_url is not None:
                image = Image.open(requests.get(image_url, stream=True).raw)
                img = resize_image(image)
                card.image = img
                print("%03d" % (card_index,) + "/" + "%03d" % (len(cards),) + "  From Scryfall:   " + card.name)
            else:
                print("%03d" % (card_index,) + "/" + "%03d" % (len(cards),) + "  Card not found: ", card.name)
        card_index += 1

    # Remove cards without images
    card_tmp = []
    for card in cards:
        if(card.image is not None):
            card_tmp.append(card)

    cards = card_tmp.copy()

    return cards


def generate_output(cards):
    all_images = []

    card_index = 0

    card_remaining = 0

    for card in cards:
        card_remaining += int(card.amount)

    total_cards = card_remaining

    copies_left = int(cards[0].amount)

    while card_remaining > 0:
        dst = Image.new('RGB', (pageWidth, pageHeight), "white")
        for i in range(3):
            for j in range(3):
                if(copies_left > 0):
                    copies_left -= 1
                else:
                    card_index += 1
                    if(card_index < len(cards)):
                        copies_left = int(cards[card_index].amount) - 1

                if(card_index < len(cards)):
                    dst.paste(cards[card_index].image, (j*cardWidth + leftOffset, i*cardHeight + topOffset))
                    card_remaining -= 1
                else:
                    break

        all_images.append(dst.copy())

    all_images[0].save(out_file, "PDF", resolution=300.0, save_all=True, append_images=all_images[1:])

    print("==================================")
    print("FINISH:        " + str(total_cards) + " cards exported")
    print("==================================")


def main():

    process_arguments()

    print("==================================")
    print("STARTS with:")
    print("     Cards File    : " + os.getcwd() + "/" + card_file)
    print("     Images Folder : " + os.getcwd() + "/" + images_folder + "/")
    print("     Output File   : " + os.getcwd() + "/" + out_file)
    print("==================================")

    cards = read_card_file()

    cards = get_images_from_cards(cards)

    generate_output(cards)


if __name__ == "__main__":
    main()
