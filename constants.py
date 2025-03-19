import pygame

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Fonts
FONT_SIZE = 36
SMALL_FONT_SIZE = 24

# Define the deck
SUITS = ['♥', '♦', '♣', '♠']  # Hearts, Diamonds, Clubs, Spades
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# Seed for reproducibility
SEED = 42  # Default seed

# List of character-based emojis
PROFILE_EMOJIS = [
    ":D", "^_^", ">_<", "O_O", "T_T", "XD", ":P", ":)", ":(", ";)", ":/", 
    ">:(", "<3", "¬_¬", r"¯\_(ツ)_/¯", "(*^_^*)", "(╯°□°）╯︵ ┻━┻", "(⌐■_■)", 
    "ಠ_ಠ", "(づ｡◕‿‿◕｡)づ", "ʕ•ᴥ•ʔ", "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "(•_•)", "(•_•)>⌐■-■", 
    "(⌐■_■)", "(☞ﾟヮﾟ)☞", "☜(ﾟヮﾟ☜)", "(｡♥‿♥｡)", "(｡◕‿◕｡)", "(◕‿◕✿)", 
    "(✿◠‿◠)", "(◠‿◠✿)", "(◕ω◕)", "(◠ω◠)", "(◠△◠✿)", "(◕‿◕)", "(◕ω◕✿)", 
    "(◠‿◠)", "(◠△◠)", "(◕△◕✿)", "(◕△◕)", "(◠‿◠✿)", "(◠ω◠✿)", "(◠△◠✿)"
]

# Load a Unicode-compatible font
UNICODE_FONT = "./This-Means-War--proto/unifont_jp-16.0.02.otf"  # Replace with the path to your font file