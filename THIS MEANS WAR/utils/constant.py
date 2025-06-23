import arcade

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 800
CARD_WIDTH = 80
CARD_HEIGHT = 120

CURSOR_BLINK_RATE = 0.5  # seconds

PROFILE_EMOJIS = [
    r"UwU", r":D", r":^D", r"OwO", r">_<", r"^_^", r"T_T", r"¯\_(ツ)_/¯",
    r":3", r"o_O", r"¬_¬", r"-_-", r"(＾▽＾)", r"(｡♥‿♥｡)", r"(╯°□°）╯︵ ┻━┻", r"(>_<)", 
    r"(ಠ_ಠ)", r"(づ｡◕‿‿◕｡)づ", r"(ಥ﹏ಥ)", r"(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", r"（￣へ￣）", r"ʕ•ᴥ•ʔ", 
    r"(°ロ°)☝", r"(∩^o^)⊃━☆", r"(≧◡≦)", r"(☞ﾟヮﾟ)☞", r"(✿´‿`)", r"(*^‿^*)", 
    r"ヽ(・∀・)ﾉ", r"(ノಠ益ಠ)ノ彡┻━┻", r"ʕノ•ᴥ•ʔノ ︵ ┻━┻", r"（　ﾟДﾟ）", r"(╥﹏╥)", 
    r"(๑>ᴗ<๑)", r"(^人^)", r"＼(￣▽￣)／", r"(*≧ω≦)", r"(⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)", 
    r"(✧ω✧)", r"(¬‿¬)", r"(¬‿¬ )", r"(•̀ᴗ•́)و ̑̑", r"(>人<)", r"(^_~)", r"(´｡• ω •｡`)", 
    r"(＾ｖ＾)", r"(T⌓T)", r"(ノД`)・゜・。", r"(☞ﾟ∀ﾟ)☞", r"(*≧▽≦)", r"(*￣▽￣)b"
]

swap_sound = arcade.load_sound(":resources:sounds/coin1.wav")
select_sound = arcade.load_sound(":resources:sounds/upgrade1.wav")

# Add near other constants
SAVE_BUTTON_X = SCREEN_WIDTH - 140
LOAD_BUTTON_X = SCREEN_WIDTH - 240
BUTTON_Y = 50
BUTTON_WIDTH = 80
BUTTON_HEIGHT = 30


HIGH_CONTRAST = {
    "text_primary": arcade.color.WHITE,
    "text_secondary": arcade.color.LIGHT_GRAY,
    "suit_spade": arcade.color.BLACK,
    "suit_club": arcade.color.BLUE,
    "suit_diamond": arcade.color.PINE_GREEN,
    "suit_heart": arcade.color.RED,
    "arrow": arcade.color.YELLOW,
    "background": arcade.color.BLACK,
}

LOW_CONTRAST = {
    "text_primary": arcade.color.DARK_GRAY,
    "text_secondary": arcade.color.GRAY,
    "suit_spade": arcade.color.GRAY,
    "suit_club": arcade.color.DARK_GRAY,
    "suit_diamond": arcade.color.BRICK_RED,
    "suit_heart": arcade.color.INDIAN_RED,
    "arrow": arcade.color.LIGHT_GRAY,
    "background": arcade.color.LIGHT_GRAY,
}

# Mapping from Unicode symbols to theme keys
suit_map = {
    "♠": "suit_spade",
    "♣": "suit_club",
    "♦": "suit_diamond",
    "♥": "suit_heart"
}

# Enhanced color scheme
color_strong_win = arcade.color.GREEN
color_weak_win = arcade.color.LIME_GREEN
color_neutral = arcade.color.LIGHT_GRAY
color_weak_loss = arcade.color.ORANGE
color_strong_loss = arcade.color.RED
color_suit_boost = arcade.color.SKY_BLUE
color_suit_penalty = arcade.color.LIGHT_SALMON

