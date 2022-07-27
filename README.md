# Magic Proxy Generator

Simple script that generates a pdf file with Magic the Gathering proxies ready to print in A4 page.


## Dependencies

1) Install python3
1) Install dependencies for project: `python3 -m pip install -r requirements.txt`


## Usage

Run the program with: `python3 mtg-proxy.py`

Available arguments:

**--help**: Show usage and commands
**--cards**: Specify the location of the cards.txt file
**--out**: The name of the output PDF file
**--images**: Path where custom proxies are located

### cards.txt format

```
2 Blood Artist
1 Swamp[m21]
1 Swamp[m20]
2 Bolas's Citadel
1 Demonic Tutor[sta]
1 Path to Exile
2 Gamble
```

# TODO

1) Distribute as a pip package
