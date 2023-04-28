import random
import pygame  # may not be be default in python
import gmpy2  # definitely not default in python

# initialize pygame window and clock
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode([1080, 720])
clock = pygame.time.Clock()
pygame.display.set_caption("Card Game")
player_one = None
player_two = None
audio = pygame.mixer.music  # song names in song folder
logged = False  # start with both player1 and 2 not logged in


def key_gen():  # generates the key used for encryption / decryption of DataBase file
    key = ""
    for key_tmp in range(10, 100_000, 123):  # iterates takes the next prime to key_temp, from 10 to 100,
        key += str(gmpy2.next_prime(key_tmp))  # 1000 increments in 123
    return key


def decrypt(message):  # decrypts the contents of the DataBase file into a format to be used to make the dictionary
    key = key_gen()  # gets the key from key_gen
    k = []
    for n, c in enumerate(message):
        if c == "\n":
            k.append("\n")  # if next line puts next line in decrypted, as the \n is not encrypted in the original file
        else:  # to decrypt it takes the ascii value of c and subtracts
            k.append(chr(ord(c) - int(key[n % len(key)])))  # the value of key at index n
    return "".join(k)  # to avoid, it errors loops to beginning if larger than len(key)


def encrypt(message):  # encrypts a message that will be written to an external file
    key = key_gen()  # gets the key from key_gen
    k = []
    for n, c in enumerate(message):  # to encrypt it takes the ascii value of c and adds the value of the key at index n
        k.append(chr(ord(c) + int(key[n % len(key)])))  # to avoid errors, it loops to beginning if larger than len(key)
    return "".join(k)


# Data Base setup: read from CSV file
try:
    with open("DataBase.txt", "r") as f:  # attempts to open the DataBase file to get the data from it
        contents = f.readlines()  # dump into contents, separated by lines
except FileNotFoundError:  # if it is not found it will make a new DataBase file
    with open("DataBase", "w") as f:
        contents = []  # makes sure contents is initialised

# Data Base setup: format data into dictionary
DataBase = {"Names": {}}
decrypt_list = []
for line in contents:
    decrypt_list.append(decrypt(line))
for x in decrypt_list:
    x = x.split(",")
    DataBase["Names"][x[0].lower()] = {"Password": x[1].strip(), "Score": int(x[2].strip()), "Logged_In": False}

# Data Base setup: make sorted leaderboard list
DataBase["LeaderBoard"] = sorted(list(DataBase["Names"].keys()), key=lambda m: DataBase["Names"][m]["Score"],
                                 reverse=True)[:5]
# Data Base setup: list of all colours used, in order of win against
DataBase["Colours"] = {"yellow": "red", "red": "black", "black": "yellow"}
DataBase["CardsCount"] = 10
DataBase["KeyWords"] = {"Accept": ["yes", "ok", "y"], "Deny": ["no", "nope", "n"]}
DataBase["Accepted_Chars"] = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r",
                              "x", "t", "u", "v", "w", "y", "s", "z", "1", "2", "3", "4", "5", "6",
                              "7", "8", "9", "0"]


class MusicController:
    def __init__(self):
        self.music = ["boots_are_made_for_walking.mp3", "break_my_stride.mp3",
                      "come_and_get_your_love.mp3", "dancing_in_the_moonlight.mp3", "footloose.mp3",
                      "gimme_gimme_gimme.mp3", "video_killed_the_radio_star.mp3",
                      "im_gonna_be_500.mp3", "our_house.mp3", "sh_boom.mp3", "smile.mp3",
                      "tide_is_high.mp3"]
        # ^^ holds all music file names
        random.shuffle(self.music)  # shuffle music list
        self.song = 0
        audio.load(("song_folder/" + self.music[self.song]))  # starts at song index 0
        audio.play()
        self.pause_play = ImpButtons("play-button.png", (30, 30), (560, 665))
        self.next = ImpButtons("next.png", (30, 30), (510, 665))
        self.paused = False

    def display_song(self):  # displays the current song playing
        font = pygame.font.Font(None, 30)
        song_text = font.render(str(self.music[self.song]).replace("_", " ")[:-4], True, (250, 250, 250))
        screen.blit(song_text, (600, 670))
        screen.blit(self.pause_play.imp, (self.pause_play.x, self.pause_play.y))
        screen.blit(self.next.imp, (self.next.x, self.next.y))

    def play_next(self):  # detects whether any song is playing or if skip
        if not (audio.get_busy() or self.paused):
            self.song += 1
            if self.song == len(self.music):
                self.song = 0
            audio.load(("song_folder/" + self.music[self.song]))
            audio.play()


def reset_deck():  # creates a "fresh" deck to be used
    deck = []
    for colour in DataBase["Colours"].keys():  # gets colours and iterates through
        for num in range(DataBase["CardsCount"]):  # iterates through the number of cards per colour
            deck.append((colour, num + 1))  # appends tuple of the colour and the number
    random.shuffle(deck)  # shuffles as deck is in ascending order
    DataBase["Deck"] = deck


class Player:  # player class to hold data for quick and easier referencing
    def __init__(self, name):
        self.name = name  # name of player
        self.score = 0  # total number of cards per game
        self.cards = []  # hold the cards that have been won


class ImpButtons:  # creates and holds data for easy use of images as buttons
    def __init__(self, imp, size, location):
        self.imp = pygame.image.load(imp)  # loads image with file name imp as self.imp
        self.imp = pygame.transform.scale(self.imp, size)  # scales to image to correct size
        self.imp.set_colorkey((255, 255, 255))  # makes parts of image which should be clear, clear
        self.x, self.y = location  # holds the location of the image
        self.rect = self.imp.get_rect()  # creates a rectangle for collision detection
        self.rect.x = self.x  # sets coordinates of the rectangle to the coordinates of the image
        self.rect.y = self.y


class Card:  # used for rapid drawing of cards from the deck
    def __init__(self, x, y, colour, number):
        if colour == "yellow":  # turns from text colour to RGB values
            colour = (255, 255, 0)
        elif colour == "black":
            colour = (0, 0, 0)
        elif colour == "red":
            colour = (255, 0, 0)

        self.rect = pygame.Rect(x, y, 70, 90)  # makes rectangle at location specified
        self.x = x  # hold coordinates of card
        self.y = y
        base_font = pygame.font.Font(None, 40)  # font used to render number
        self.text = base_font.render(str(number), True, (255, 255, 255))  # renders the number to be used on top of card
        self.colour = colour  # holds colour of card

    def draw(self):  # used to quickly draw the card
        pygame.draw.rect(screen, self.colour, self.rect)  # draws the rect to the screen
        screen.blit(self.text, (self.x + 25, self.y + 35))  # draws the number to the screen


class MiniCard:  # very similar to previous Card class but is overall smaller to avoid overlap/runoff the screen
    def __init__(self, x, y, colour, number):
        if colour == "yellow":
            colour = (255, 255, 0)
        elif colour == "black":
            colour = (0, 0, 0)
        elif colour == "red":
            colour = (255, 0, 0)

        self.rect = pygame.Rect(x, y, 30, 40)
        self.x = x
        self.y = y
        base_font = pygame.font.Font(None, 30)
        self.text = base_font.render(str(number), True, (255, 255, 255))
        self.colour = colour

    def draw(self):
        pygame.draw.rect(screen, self.colour, self.rect)
        screen.blit(self.text, (self.x + 5, self.y + 10))


def save():  # saves data stored in DataBase dictionary to DataBase file
    DataBase["LeaderBoard"] = sorted(list(DataBase["Names"].keys()), key=lambda m: DataBase["Names"][m]["Score"],
                                     reverse=True)[:5]
    file = open("DataBase.txt", "w")  # rewrites file
    for name in DataBase["Names"].keys():  # iterates through profile names
        line = f"{name},{DataBase['Names'][name]['Password']},{DataBase['Names'][name]['Score']}"  # makes line segment
        file.write(encrypt(line) + "\n")  # encrypts and then writes to file making sure not to encrypt "\n"
    file.close()  # closes file


def sign_in():  # allows 2 users to sign in
    global player_one, player_two, logged  # access variables from outside function
    menu_button = ImpButtons("Menu.png", (100, 70), (20, 20))  # creates the menu button
    base_font = pygame.font.Font(None, 32)  # creates the font
    username1 = ""
    password1 = ""
    username_rect1 = pygame.Rect(200, 200, 140, 32)  # creates rectangles
    password_rect1 = pygame.Rect(200, 262, 140, 32)
    divider_rect = pygame.Rect(530, 0, 20, 720)
    colour_active = pygame.Color("lightskyblue3")  # creates and sets colours
    colour_passive = pygame.Color("chartreuse4")
    u1colour = colour_passive
    p1colour = colour_passive
    u1active = False
    p1active = False
    hidden1 = True
    hidden_text1 = ""
    view1 = ImpButtons("View_password.png", (32, 32), (470, 262))  # creates view password button

    username2 = ""
    password2 = ""
    username_rect2 = pygame.Rect(720, 200, 140, 32)
    password_rect2 = pygame.Rect(720, 262, 140, 32)
    u2colour = colour_passive
    p2colour = colour_passive
    u2active = False
    p2active = False
    hidden2 = True
    hidden_text2 = ""
    view2 = ImpButtons("View_password.png", (32, 32), (990, 262))

    login1_rect = pygame.Rect(250, 324, 120, 32)
    login2_rect = pygame.Rect(770, 324, 120, 32)

    player1_login = False  # whether player 1 or 2 have logged in yet
    player2_login = False

    while not (player1_login and player2_login):
        Music.play_next()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # exit login screen
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if username_rect1.collidepoint(event.pos):  # only true when username one box clicked
                    u1active = True
                    p1active = False
                    u2active = False
                    p2active = False
                elif password_rect1.collidepoint(event.pos):
                    u1active = False
                    p1active = True
                    u2active = False
                    p2active = False
                elif username_rect2.collidepoint(event.pos):
                    u1active = False
                    p1active = False
                    u2active = True
                    p2active = False
                elif password_rect2.collidepoint(event.pos):
                    u1active = False
                    p1active = False
                    u2active = False
                    p2active = True
                elif login1_rect.collidepoint(event.pos):  # on login button clicked
                    if username1 in DataBase["Names"] and DataBase["Names"][username1]["Password"] == password1 and not \
                            DataBase["Names"][username1]["Logged_In"]:
                        player1_login = True  # sets player to have logged in if the username is in database and passwords match
                elif login2_rect.collidepoint(event.pos):
                    if username2 in DataBase["Names"] and DataBase["Names"][username2]["Password"] == password2 and not \
                            DataBase["Names"][username2]["Logged_In"]:
                        player2_login = True
                else:
                    u1active = False
                    p1active = False
                    u2active = False
                    p2active = False
                if menu_button.rect.collidepoint(event.pos):
                    return None  # return to menu once menu button clicked
                if view1.rect.collidepoint(event.pos):
                    hidden1 = not hidden1  # swaps visibility of password
                if view2.rect.collidepoint(event.pos):
                    hidden2 = not hidden2
                if Music.pause_play.rect.collidepoint(event.pos) and not Music.paused:
                    audio.pause()
                    Music.paused = True
                elif Music.pause_play.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                if Music.next.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                    audio.stop()

            if event.type == pygame.KEYDOWN and u1active:
                if event.key == pygame.K_BACKSPACE:
                    username1 = username1[:-1]  # removes last character
                elif event.key == pygame.K_RETURN:
                    if username1 in DataBase["Names"] and DataBase["Names"][username1]["Password"] == password1 and not \
                            DataBase["Names"][username1]["Logged_In"]:
                        player1_login = True  # same as if they pressed login
                else:
                    if (char := event.unicode.lower()) in DataBase["Accepted_Chars"] and len(username1) < 14:
                        username1 += char  # appends the new character only if it is a character in the whitelist
            if event.type == pygame.KEYDOWN and p1active:
                if event.key == pygame.K_BACKSPACE:
                    password1 = password1[:-1]
                    hidden_text1 = hidden_text1[:-1]
                elif event.key == pygame.K_RETURN:
                    if username1 in DataBase["Names"] and DataBase["Names"][username1]["Password"] == password1 and not \
                            DataBase["Names"][username1]["Logged_In"]:
                        player1_login = True
                else:
                    if (char := event.unicode.lower()) in DataBase["Accepted_Chars"] and len(password1) < 14:
                        password1 += char
                        hidden_text1 += "*"  # makes makes the number of "*" the same length as the password
            if event.type == pygame.KEYDOWN and u2active:
                if event.key == pygame.K_BACKSPACE:
                    username2 = username2[:-1]
                elif event.key == pygame.K_RETURN:
                    if username2 in DataBase["Names"] and DataBase["Names"][username2]["Password"] == password2 and not \
                            DataBase["Names"][username2]["Logged_In"]:
                        player2_login = True
                else:
                    if (char := event.unicode.lower()) in DataBase["Accepted_Chars"] and len(username2) < 14:
                        username2 += char
            if event.type == pygame.KEYDOWN and p2active:
                if event.key == pygame.K_BACKSPACE:
                    password2 = password2[:-1]
                    hidden_text2 = hidden_text2[:-1]
                elif event.key == pygame.K_RETURN:
                    if username2 in DataBase["Names"] and DataBase["Names"][username2]["Password"] == password2 and not \
                            DataBase["Names"][username2]["Logged_In"]:
                        player2_login = True
                else:
                    if (char := event.unicode.lower()) in DataBase["Accepted_Chars"] and len(password2) < 14:
                        password2 += char
                        hidden_text2 += "*"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # returns out of sign in screen

        screen.fill((50, 50, 50))
        u1colour = colour_active if u1active else colour_passive  # swaps colour if it is active
        u2colour = colour_active if u2active else colour_passive
        p1colour = colour_active if p1active else colour_passive
        p2colour = colour_active if p2active else colour_passive

        if not player1_login:  # checks whether they are signed in
            pygame.draw.rect(screen, u1colour, username_rect1)  # draw rect to screen
            users_surf = base_font.render(username1, True, (255, 255, 255))
            screen.blit(users_surf, (username_rect1.x + 5, username_rect1.y + 5))  # display text
            username_rect1.w = 250  # make rect certain width

            pygame.draw.rect(screen, p1colour, password_rect1)
            if hidden1:  # if hidden display the text of all "*" else show actual password
                pass_surf = base_font.render(hidden_text1, True, (255, 255, 255))
            else:
                pass_surf = base_font.render(password1, True, (255, 255, 255))
            screen.blit(pass_surf, (password_rect1.x + 5, password_rect1.y + 5))
            password_rect1.w = 250

            text_u = base_font.render("Username:", True, (255, 255, 255))
            screen.blit(text_u, (username_rect1.x - 150, username_rect1.y + 5))
            text_p = base_font.render("Password:", True, (255, 255, 255))
            screen.blit(text_p, (password_rect1.x - 150, password_rect1.y + 5))

            pygame.draw.rect(screen, colour_passive, login1_rect)
            login1_text = base_font.render("Login", True, (255, 255, 255))
            screen.blit(view1.imp, (view1.x, view2.y))
            screen.blit(login1_text, (login1_rect.x + 35, login1_rect.y + 5))
        else:
            waiting_text1 = base_font.render("Waiting for player 2 login", True, (255, 255, 255))
            screen.blit(waiting_text1, (150, 300))  # sets up screen for waiting on other player to log in, makes player
            DataBase["Names"][username1]["Logged_In"] = True
            player_one = Player(username1)

        if not player2_login:
            pygame.draw.rect(screen, u2colour, username_rect2)
            users_surf2 = base_font.render(username2, True, (255, 255, 255))
            screen.blit(users_surf2, (username_rect2.x + 5, username_rect2.y + 5))
            username_rect2.w = 250

            pygame.draw.rect(screen, p2colour, password_rect2)
            if hidden2:
                pass_surf2 = base_font.render(hidden_text2, True, (255, 255, 255))
            else:
                pass_surf2 = base_font.render(password2, True, (255, 255, 255))
            screen.blit(pass_surf2, (password_rect2.x + 5, password_rect2.y + 5))
            password_rect2.w = 250

            text_u2 = base_font.render("Username:", True, (255, 255, 255))
            screen.blit(text_u2, (username_rect2.x - 150, username_rect2.y + 5))
            text_p2 = base_font.render("Password:", True, (255, 255, 255))
            screen.blit(text_p2, (password_rect2.x - 150, password_rect2.y + 5))

            pygame.draw.rect(screen, colour_passive, login2_rect)
            login2_text = base_font.render("Login", True, (255, 255, 255))
            screen.blit(view2.imp, (view2.x, view2.y))
            screen.blit(login2_text, (login2_rect.x + 35, login2_rect.y + 5))
        else:
            waiting_text2 = base_font.render("Waiting for player 1 login", True, (255, 255, 255))
            screen.blit(waiting_text2, (700, 300))
            DataBase["Names"][username2]["Logged_In"] = True
            player_two = Player(username2)

        pygame.draw.rect(screen, (0, 0, 0), divider_rect)
        screen.blit(menu_button.imp, (menu_button.x, menu_button.y))  # display menu button
        Music.display_song()
        pygame.display.flip()  # update screen
        clock.tick(60)  # make sure program runs at 60fps
    logged = True


def print_cards():
    i = 0
    display_cards = []
    for ver in range(360, 720, 45):  # iterates through y coordinate
        for hor in range(20, 195, 35):  # iterates through x coordinate
            if i < len(player_one.cards):
                display_cards.append(
                    MiniCard(hor, ver, player_one.cards[i][0], player_one.cards[i][1]))  # creates cards
            i += 1
    for card in display_cards:
        card.draw()  # displays each card
    i = 0
    display_cards = []
    for ver in range(360, 720, 45):
        for hor in range(680, 855, 35):  # shifted to the right for player 2
            if i < len(player_two.cards):
                display_cards.append(MiniCard(hor, ver, player_two.cards[i][0], player_two.cards[i][1]))
            i += 1
    for card in display_cards:
        card.draw()


def end_cond():
    menu_button = ImpButtons("Menu.png", (100, 70), (20, 70))  # creates menu button
    if player_one.score > player_two.score:  # takes winner of 2 players
        player = player_one
    else:
        player = player_two
    DataBase["Names"][player_one.name]["Score"] += player_one.score  # updates dictionary score
    DataBase["Names"][player_two.name]["Score"] += player_two.score  # updates dictionary score
    viewing = True
    while viewing:
        Music.play_next()
        screen.fill((50, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                viewing = False  # return to main menu
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.rect.collidepoint(event.pos):
                    viewing = False  # return to main menu
                    continue
                if Music.pause_play.rect.collidepoint(event.pos) and not Music.paused:
                    audio.pause()
                    Music.paused = True
                elif Music.pause_play.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                if Music.next.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                    audio.stop()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    viewing = False
                    continue

        i = 0
        display_cards = []
        for ver in range(360, 720, 45):  # run through and display winners cards
            for hor in range(200, 375, 35):
                if i < len(player.cards):
                    display_cards.append(MiniCard(hor, ver, player.cards[i][0], player.cards[i][1]))
                i += 1
        for card in display_cards:
            card.draw()

        base_font = pygame.font.Font(None, 40)
        win_text = base_font.render(f"You Won {player.name}, with {player.score} cards", True, (255, 255, 0))
        screen.blit(win_text, (150, 100))  # draws win dialog
        screen.blit(menu_button.imp, (menu_button.x, menu_button.y))
        Music.display_song()
        pygame.display.flip()


def play_game():
    menu_button = ImpButtons("Menu.png", (100, 70), (20, 70))  # make buttons using images
    imp_deck = ImpButtons("Deck icon.png", (104, 150), (488, 40))
    imp_check = ImpButtons("check_icon.png", (80, 80), (500, 200))
    playing = True
    reset_deck()  # resets the deck list to be a complete deck
    divider_rect = pygame.Rect(530, 300, 20, 420)
    turn = True  # if true it is player ones turn elif false it is player twos turn
    fighting = False
    base_font = pygame.font.Font(None, 40)
    win_text = base_font.render("Winner!", True, (0, 255, 0))
    lose_text = base_font.render("Loser!", True, (255, 0, 0))
    winner = ""
    while playing:
        Music.play_next()
        if len(DataBase["Deck"]) == 0:  # check if the deck is empty
            end_cond()
            playing = False
            continue
        screen.fill((50, 50, 50))
        turn = not turn  # switch whos turn it is
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False  # exit to main menu
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    playing = False
                    continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if imp_deck.rect.collidepoint(event.pos) and not fighting:
                    winner = ""
                    fighting = True
                    if turn:  # take first and second card from deck (in order of player)
                        first_card = Card(300, 200, DataBase["Deck"][0][0], DataBase["Deck"][0][1])
                        second_card = Card(700, 200, DataBase["Deck"][1][0], DataBase["Deck"][1][1])
                    else:
                        first_card = Card(300, 200, DataBase["Deck"][1][0], DataBase["Deck"][1][1])
                        second_card = Card(700, 200, DataBase["Deck"][0][0], DataBase["Deck"][0][1])

                if imp_check.rect.collidepoint(event.pos) and fighting:
                    fighting = False
                    if DataBase["Colours"][DataBase["Deck"][0][0]] == DataBase["Deck"][1][0]:  # determines winner
                        player_one.score += 2  # adds score to winner
                        player_one.cards.append(DataBase["Deck"][0])
                        player_one.cards.append(DataBase["Deck"][1])
                        DataBase["Deck"].pop(0)  # removes first 2 cards from deck
                        DataBase["Deck"].pop(0)
                        winner = "one"  # tells which player won
                    else:
                        player_two.score += 2
                        player_two.cards.append(DataBase["Deck"][0])
                        player_two.cards.append(DataBase["Deck"][1])
                        DataBase["Deck"].pop(0)
                        DataBase["Deck"].pop(0)
                        winner = "two"

                if menu_button.rect.collidepoint(event.pos):
                    playing = False
                    continue
                if Music.pause_play.rect.collidepoint(event.pos) and not Music.paused:
                    audio.pause()
                    Music.paused = True
                elif Music.pause_play.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                if Music.next.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                    audio.stop()

        if fighting:
            second_card.draw()  # draw 2 playing cards
            first_card.draw()
        if winner == "one":  # draw winner/loser text
            screen.blit(win_text, (200, 50))
            screen.blit(lose_text, (800, 50))
        elif winner == "two":
            screen.blit(lose_text, (200, 50))
            screen.blit(win_text, (800, 50))
        print_cards()  # displays cards of each player
        pygame.draw.rect(screen, (0, 0, 0), divider_rect)  # displays all images / rectangles / buttons
        screen.blit(imp_deck.imp, (imp_deck.x, imp_deck.y))
        screen.blit(imp_check.imp, (imp_check.x, imp_check.y))
        screen.blit(base_font.render(("Player One: " + player_one.name), True, (255, 255, 255)), (50, 10))
        screen.blit(base_font.render(("Player Two: " + player_two.name), True, (255, 255, 255)), (700, 10))
        screen.blit(menu_button.imp, (menu_button.x, menu_button.y))
        Music.display_song()
        pygame.display.flip()  # refresh screen
        clock.tick(60)  # 60fps


def leaderboard():
    DataBase["LeaderBoard"] = sorted(list(DataBase["Names"].keys()),  # updates leaderboard
                                     key=lambda m: DataBase["Names"][m]["Score"], reverse=True)[:5]
    in_leaderboard = True
    base_font = pygame.font.Font(None, 50)
    names = []
    scores = []
    menu_button = ImpButtons("Menu.png", (100, 70), (20, 20))  # menu button
    for name in DataBase["LeaderBoard"]:  # iterate through leaderboard names
        names.append(base_font.render(name, True, (200, 200, 200)))  # render names
        scores.append(base_font.render(str(DataBase["Names"][name]["Score"]), True, (200, 200, 200)))  # render scores
    while in_leaderboard:
        Music.play_next()
        screen.fill((50, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                in_leaderboard = False  # exit to main menu
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.rect.collidepoint(event.pos):
                    in_leaderboard = False
                    continue
                if Music.pause_play.rect.collidepoint(event.pos) and not Music.paused:
                    audio.pause()
                    Music.paused = True
                elif Music.pause_play.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                if Music.next.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                    audio.stop()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_leaderboard = False
                    continue

        for num in range(len(names)):  # iterate through renders names / scores and display them
            screen.blit(names[num], (200, 20 + (70 * num)))
            screen.blit(scores[num], (700, 20 + (70 * num)))
        screen.blit(menu_button.imp, (menu_button.x, menu_button.y))
        Music.display_song()
        pygame.display.flip()  # refresh screen
        clock.tick(60)  # 60fps


def edit_profiles():
    global logged  # get global logged variable
    menu_button = ImpButtons("Menu.png", (100, 70), (20, 20))  # menu button
    username = ""
    password = ""
    base_font = pygame.font.Font(None, 32)  # fonts
    large_font = pygame.font.Font(None, 50)
    colour_active = pygame.Color("lightskyblue3")  # colour setup
    colour_passive = pygame.Color("chartreuse4")
    u_colour = colour_passive
    p_colour = colour_passive
    u_active = False
    p_active = False
    username_rect = pygame.Rect(200, 200, 140, 32)  # rectangle setup
    password_rect = pygame.Rect(200, 262, 140, 32)
    create_rect = pygame.Rect(600, 150, 300, 70)
    delete_rect = pygame.Rect(600, 250, 300, 70)
    create_text = large_font.render("Create Profile", True, (0, 0, 0))
    delete_text = large_font.render("Delete Profile", True, (0, 0, 0))
    editing = True
    error = False
    error_message = ""
    hidden = True
    hidden_text = ""
    view = ImpButtons("View_password.png", (32, 32), (460, 262))  # view password button

    while editing:
        Music.play_next()
        screen.fill((50, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editing = False  # exit to main menu
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if username_rect.collidepoint(event.pos):  # get when username box clicked
                    u_active = True
                    p_active = False
                if password_rect.collidepoint(event.pos):  # get when password box clicked
                    p_active = True
                    u_active = False
                if create_rect.collidepoint(event.pos):
                    if username not in DataBase["Names"]:
                        DataBase["Names"][username] = {"Password": password, "Score": 0,
                                                       "Logged_In": False}  # creates profile
                        DataBase["LeaderBoard"] = sorted(list(DataBase["Names"].keys()),  # updates leaderboard
                                                         key=lambda m: DataBase["Names"][m]["Score"], reverse=True)[:5]
                        error = True
                        error_message = "Profile Created"
                        save()  # saves changes to file
                        for name in DataBase["Names"].keys():
                            DataBase["Names"][name]["Logged_In"] = False
                    else:
                        error = True
                        error_message = "Username already taken"  # display error message
                if delete_rect.collidepoint(event.pos):
                    try:
                        if DataBase["Names"][username]["Password"] == password:
                            del DataBase["Names"][username]  # deletes from dictionary
                            try:
                                DataBase["LeaderBoard"].remove(username)  # try removing from leaderboard
                            except ValueError:
                                pass  # if cannot, doesnt need to do anything
                            error = True
                            error_message = "Deleted Profile"
                            save()  # saves changes to file
                            logged = False
                            for name in DataBase["Names"].keys():
                                DataBase["Names"][name]["Logged_In"] = False
                        else:
                            error = True
                            error_message = "Password does not match"  # display error message
                    except KeyError:
                        error = True
                        error_message = "Username does not exist"  # display error message
                if menu_button.rect.collidepoint(event.pos):
                    editing = False  # exit to main menu
                    continue
                if view.rect.collidepoint(event.pos):
                    hidden = not hidden
                if Music.pause_play.rect.collidepoint(event.pos) and not Music.paused:
                    audio.pause()
                    Music.paused = True
                elif Music.pause_play.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                if Music.next.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                    audio.stop()

            if event.type == pygame.KEYDOWN and u_active:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]  # remove last character
                else:
                    if (char := event.unicode.lower()) in DataBase["Accepted_Chars"] and len(username) < 14:
                        username += char  # append character to username
            if event.type == pygame.KEYDOWN and p_active:
                if event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                    hidden_text = hidden_text[:-1]  # make sure hidden text is the same length as password
                else:
                    if (char := event.unicode.lower()) in DataBase["Accepted_Chars"] and len(password) < 14:
                        password += char
                        hidden_text += "*"

        u_colour = colour_active if u_active else colour_passive  # swap colours if active
        p_colour = colour_active if p_active else colour_passive

        pygame.draw.rect(screen, u_colour, username_rect)  # draw everything to screen
        users_surf = base_font.render(username, True, (255, 255, 255))
        screen.blit(users_surf, (username_rect.x + 5, username_rect.y + 5))
        username_rect.w = 250

        pygame.draw.rect(screen, p_colour, password_rect)
        if hidden:
            pass_surf = base_font.render(hidden_text, True, (255, 255, 255))
        else:
            pass_surf = base_font.render(password, True, (255, 255, 255))
        screen.blit(pass_surf, (password_rect.x + 5, password_rect.y + 5))
        password_rect.w = 250

        text_u = base_font.render("Username:", True, (255, 255, 255))
        screen.blit(text_u, (username_rect.x - 150, username_rect.y + 5))
        text_p = base_font.render("Password:", True, (255, 255, 255))
        screen.blit(text_p, (password_rect.x - 150, password_rect.y + 5))

        pygame.draw.rect(screen, (200, 200, 200), create_rect)
        screen.blit(create_text, (create_rect.x + 40, create_rect.y + 20))
        pygame.draw.rect(screen, (200, 200, 200), delete_rect)
        screen.blit(delete_text, (delete_rect.x + 40, delete_rect.y + 20))

        if error:  # only if error message to display it displays
            screen.blit(base_font.render(error_message, True, (255, 0, 0)), (100, 100))
        screen.blit(menu_button.imp, (menu_button.x, menu_button.y))
        screen.blit(view.imp, (view.x, view.y))
        Music.display_song()
        pygame.display.flip()  # display update
        clock.tick(60)  # 60fps


class VolumeChanger:  # holds volume data
    def __init__(self):
        self.rect = pygame.Rect(900, 200, 30, 200)
        self.controller = pygame.Rect(905, 205, 20, 20)
        self.value = '{0:.2f}'.format(1 - ((self.controller.y - 205) / 170))


def main_menu():
    in_menu = True
    error = False
    base_font = pygame.font.Font(None, 70)  # fonts
    small_font = pygame.font.Font(None, 50)
    error_display = small_font.render("", True, (255, 0, 0))
    sign_rect = pygame.Rect(370, 100, 350, 70)  # rectangles
    play_rect = pygame.Rect(370, 200, 350, 70)
    leaderboard_rect = pygame.Rect(370, 300, 350, 70)
    edit_rect = pygame.Rect(370, 400, 350, 70)
    exit_rect = pygame.Rect(370, 500, 350, 70)
    sign_text = base_font.render("Sign In", True, (0, 0, 0))  # text rendering
    play_text = base_font.render("Play", True, (0, 0, 0))
    leaderboard_text = base_font.render("Leaderboard", True, (0, 0, 0))
    edit_text = base_font.render("Edit Profiles", True, (0, 0, 0))
    exit_text = base_font.render("Exit", True, (0, 0, 0))
    sound_text = small_font.render(f"Volume: {volume.value.replace('.', '').lstrip('0')}%", True, (200, 200, 200))
    # ^^ formats volume value to percentage
    while in_menu:
        Music.play_next()  # plays next song if nothing is playing / skip
        screen.fill((50, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                in_menu = False  # exit game
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sign_rect.collidepoint(event.pos):
                    sign_in()  # player 1 and 2 sign in
                    error = False
                if play_rect.collidepoint(event.pos) and logged:
                    play_game()  # plays game
                    save()  # saves changes to file
                    player_one.score = 0
                    player_two.score = 0
                    player_one.cards = []  # resets player 1 and 2 variables
                    player_two.cards = []
                elif play_rect.collidepoint(event.pos):
                    error_display = small_font.render("You need to log in first", True, (255, 0, 0))
                    error = True  # display whether player1 and player2 have not logged in yet
                if leaderboard_rect.collidepoint(event.pos):
                    leaderboard()  # display leaderboard
                if edit_rect.collidepoint(event.pos):
                    edit_profiles()  # enter edit profiles screen
                    for name in DataBase["Names"].keys():
                        DataBase["Names"][name]["Logged_In"] = False
                if exit_rect.collidepoint(event.pos):
                    in_menu = False  # exit game
                    continue
                if volume.rect.collidepoint(event.pos):  # get clicked on volume slider
                    volume.controller.y = event.pos[1] if 376 > event.pos[1] > 204 else (
                        375 if event.pos[1] > 364 else 205)
                    volume.value = '{0:.2f}'.format(1 - ((volume.controller.y - 205) / 170))
                    audio.set_volume(float(volume.value))
                    sound_text = small_font.render(
                        f"Volume: {volume.value.replace('.', '').lstrip('0') if float(volume.value) > 0 else '0'}%",
                        True, (200, 200, 200))
                if Music.pause_play.rect.collidepoint(event.pos) and not Music.paused:
                    audio.pause()
                    Music.paused = True
                elif Music.pause_play.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                if Music.next.rect.collidepoint(event.pos):
                    audio.unpause()
                    Music.paused = False
                    audio.stop()

        pygame.draw.rect(screen, (200, 200, 200), volume.rect)
        pygame.draw.rect(screen, (255, 0, 0), volume.controller)

        pygame.draw.rect(screen, (200, 200, 200), sign_rect)  # draw buttons
        pygame.draw.rect(screen, (200, 200, 200), play_rect)
        pygame.draw.rect(screen, (200, 200, 200), leaderboard_rect)
        pygame.draw.rect(screen, (200, 200, 200), edit_rect)
        pygame.draw.rect(screen, (200, 200, 200), exit_rect)
        screen.blit(sign_text, (sign_rect.x + 90, sign_rect.y + 10))  # draw buttons text
        screen.blit(play_text, (play_rect.x + 120, play_rect.y + 10))
        screen.blit(leaderboard_text, (leaderboard_rect.x + 10, leaderboard_rect.y + 10))
        screen.blit(edit_text, (edit_rect.x + 35, edit_rect.y + 10))
        screen.blit(exit_text, (exit_rect.x + 120, exit_rect.y + 10))
        screen.blit(sound_text, (800, 150))

        Music.display_song()
        if error:  # display error in middle of screen
            screen.blit(error_display, (530 - (error_display.get_width() // 2), 50))
        pygame.display.flip()  # display updates
        clock.tick(60)  # 60fps


def loading_tips():  # displays tips on how to play the game
    main_menu_screen = pygame.image.load("Main_Menu.png")  # get main menu image
    main_menu_screen = pygame.transform.scale(main_menu_screen, (1080, 720))  # change scale so it fits screen
    play_screen_start = pygame.image.load("Play_Sreen_Start.png")  # get first play screen image
    play_screen_start = pygame.transform.scale(play_screen_start, (1080, 720))  # change scale so it fits screen
    play_screen_second = pygame.image.load("Play_Screen_Second.png")
    play_screen_second = pygame.transform.scale(play_screen_second, (1080, 720))
    play_screen_third = pygame.image.load("Play_Screen_Third.png")
    play_screen_third = pygame.transform.scale(play_screen_third, (1080, 720))
    sign_in_screen = pygame.image.load("Sign_In.png")
    sign_in_screen = pygame.transform.scale(sign_in_screen, (1080, 720))
    images = [main_menu_screen, sign_in_screen, play_screen_start, play_screen_second, play_screen_third]
    for num in range(600):  # ^^^ adds all images to a list, in order of appearance
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # skip images
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # skip
                if event.key == pygame.K_SPACE:
                    return None  # skip

        screen.blit(images[num // 120], (0, 0))  # num//120 only increases by one every 120 ticks
        pygame.display.flip()  # refresh display
        clock.tick(60)  # 60fps


# driver code
loading_tips()  # gives tips on how to play
volume = VolumeChanger()  # initializes volume class
Music = MusicController()  # initializes music controller class
main_menu()  # starts game
audio.stop()  # stops any current music
pygame.mixer.quit()  # quits sound mixer
pygame.quit()  # quits pygame

# video testing, testing plan
# double check github with someone else, finish documentation of additional sound code and bug fixed code
# download more music, put in list
