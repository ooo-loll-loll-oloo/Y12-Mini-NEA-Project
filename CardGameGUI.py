import random
import pygame  # may not be be default in python
import gmpy2  # definitely not default in python

# initialize pygame window and clock
pygame.init()
screen = pygame.display.set_mode([1080, 720])
clock = pygame.time.Clock()
pygame.display.set_caption("Card Game")


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
        else:                                               # to decrypt it takes the ascii value of c and subtracts
            k.append(chr(ord(c) - int(key[n % len(key)])))  # the value of key at index n
    return "".join(k)                                   # to avoid, it errors loops to beginning if larger than len(key)


def encrypt(message):  # encrypts a message that will be written to an external file
    key = key_gen()  # gets the key from key_gen
    k = []
    for n, c in enumerate(message):  # to encrypt it takes the ascii value of c and adds the value of the key at index n
        k.append(chr(ord(c) + int(key[n % len(key)])))  # to avoid errors, it loops to beginning if larger than len(key)
    return "".join(k)


# Data Base setup: read from CSV file
try:
    with open("DataBase.CSV", "r") as f:  # attempts to open the DataBase file to get the data from it
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
    DataBase["Names"][player_one.name]["Score"] += player_one.score  # updates dictionary score
    DataBase["Names"][player_two.name]["Score"] += player_two.score  # updates dictionary score
    file = open("DataBase.CSV", "w")  # rewrites file
    for name in DataBase["Names"].keys():  # iterates through profile names
        line = f"{name},{DataBase['Names'][name]['Password']},{DataBase['Names'][name]['Score']}"  # makes line segment
        file.write(encrypt(line) + "\n")  # encrypts and then writes to file making sure not to encrypt "\n"
    file.close()  # closes file


def sign_in():
    global player_one, player_two, logged
    menu_button = ImpButtons("Menu.png", (100, 70), (20, 20))
    base_font = pygame.font.Font(None, 32)
    username1 = ""
    password1 = ""
    username_rect1 = pygame.Rect(200, 200, 140, 32)
    password_rect1 = pygame.Rect(200, 262, 140, 32)
    divider_rect = pygame.Rect(530, 0, 20, 720)
    colour_active = pygame.Color("lightskyblue3")
    colour_passive = pygame.Color("chartreuse4")
    u1colour = colour_passive
    p1colour = colour_passive
    u1active = False
    p1active = False

    username2 = ""
    password2 = ""
    username_rect2 = pygame.Rect(720, 200, 140, 32)
    password_rect2 = pygame.Rect(720, 262, 140, 32)
    u2colour = colour_passive
    p2colour = colour_passive
    u2active = False
    p2active = False

    login1_rect = pygame.Rect(250, 324, 120, 32)
    login2_rect = pygame.Rect(770, 324, 120, 32)

    player1_login = False
    player2_login = False

    while not (player1_login and player2_login):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if username_rect1.collidepoint(event.pos):
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
                elif login1_rect.collidepoint(event.pos):
                    if username1 in DataBase["Names"] and DataBase["Names"][username1]["Password"] == password1:
                        player1_login = True
                elif login2_rect.collidepoint(event.pos):
                    if username2 in DataBase["Names"] and DataBase["Names"][username2]["Password"] == password2:
                        player2_login = True
                else:
                    u1active = False
                    p1active = False
                    u2active = False
                    p2active = False
                if menu_button.rect.collidepoint(event.pos):
                    return "stop program"

            if event.type == pygame.KEYDOWN and u1active:
                if event.key == pygame.K_BACKSPACE:
                    username1 = username1[:-1]
                elif event.key == pygame.K_RETURN:
                    if username1 in DataBase["Names"] and DataBase["Names"][username1]["Password"] == password1 and not \
                            DataBase["Names"][username1]["Logged_In"]:
                        print("hooray")
                        player1_login = True
                else:
                    username1 += event.unicode.lower()
            if event.type == pygame.KEYDOWN and p1active:
                if event.key == pygame.K_BACKSPACE:
                    password1 = password1[:-1]
                elif event.key == pygame.K_RETURN:
                    if username1 in DataBase["Names"] and DataBase["Names"][username1]["Password"] == password1 and not \
                            DataBase["Names"][username1]["Logged_In"]:
                        print("hooray")
                        player1_login = True
                else:
                    password1 += event.unicode
            if event.type == pygame.KEYDOWN and u2active:
                if event.key == pygame.K_BACKSPACE:
                    username2 = username2[:-1]
                elif event.key == pygame.K_RETURN:
                    if username2 in DataBase["Names"] and DataBase["Names"][username2]["Password"] == password2 and not \
                            DataBase["Names"][username2]["Logged_In"]:
                        print("hooray")
                        player2_login = True
                else:
                    username2 += event.unicode.lower()
            if event.type == pygame.KEYDOWN and p2active:
                if event.key == pygame.K_BACKSPACE:
                    password2 = password2[:-1]
                elif event.key == pygame.K_RETURN:
                    if username2 in DataBase["Names"] and DataBase["Names"][username2]["Password"] == password2 and not \
                            DataBase["Names"][username2]["Logged_In"]:
                        print("hooray")
                        player2_login = True
                else:
                    password2 += event.unicode

        screen.fill((50, 50, 50))
        u1colour = colour_active if u1active else colour_passive
        u2colour = colour_active if u2active else colour_passive
        p1colour = colour_active if p1active else colour_passive
        p2colour = colour_active if p2active else colour_passive

        if not player1_login:
            pygame.draw.rect(screen, u1colour, username_rect1)
            users_surf = base_font.render(username1, True, (255, 255, 255))
            screen.blit(users_surf, (username_rect1.x + 5, username_rect1.y + 5))
            username_rect1.w = 250

            pygame.draw.rect(screen, p1colour, password_rect1)
            pass_surf = base_font.render(password1, True, (255, 255, 255))
            screen.blit(pass_surf, (password_rect1.x + 5, password_rect1.y + 5))
            password_rect1.w = 250

            text_u = base_font.render("Username:", True, (255, 255, 255))
            screen.blit(text_u, (username_rect1.x - 150, username_rect1.y + 5))
            text_p = base_font.render("Password:", True, (255, 255, 255))
            screen.blit(text_p, (password_rect1.x - 150, password_rect1.y + 5))

            pygame.draw.rect(screen, colour_passive, login1_rect)
            login1_text = base_font.render("Login", True, (255, 255, 255))
            screen.blit(login1_text, (login1_rect.x + 35, login1_rect.y + 5))
        else:
            waiting_text1 = base_font.render("Waiting for player 2 login", True, (255, 255, 255))
            screen.blit(waiting_text1, (150, 300))
            DataBase["Names"][username1]["Logged_In"] = True
            player_one = Player(username1)

        if not player2_login:
            pygame.draw.rect(screen, u2colour, username_rect2)
            users_surf2 = base_font.render(username2, True, (255, 255, 255))
            screen.blit(users_surf2, (username_rect2.x + 5, username_rect2.y + 5))
            username_rect2.w = 250

            pygame.draw.rect(screen, p2colour, password_rect2)
            pass_surf2 = base_font.render(password2, True, (255, 255, 255))
            screen.blit(pass_surf2, (password_rect2.x + 5, password_rect2.y + 5))
            password_rect2.w = 250

            text_u2 = base_font.render("Username:", True, (255, 255, 255))
            screen.blit(text_u2, (username_rect2.x - 150, username_rect2.y + 5))
            text_p2 = base_font.render("Password:", True, (255, 255, 255))
            screen.blit(text_p2, (password_rect2.x - 150, password_rect2.y + 5))

            pygame.draw.rect(screen, colour_passive, login2_rect)
            login2_text = base_font.render("Login", True, (255, 255, 255))
            screen.blit(login2_text, (login2_rect.x + 35, login2_rect.y + 5))
        else:
            waiting_text2 = base_font.render("Waiting for player 1 login", True, (255, 255, 255))
            screen.blit(waiting_text2, (700, 300))
            DataBase["Names"][username2]["Logged_In"] = True
            player_two = Player(username2)

        pygame.draw.rect(screen, (0, 0, 0), divider_rect)
        screen.blit(menu_button.imp, (menu_button.x, menu_button.y))
        pygame.display.flip()
        clock.tick(60)
    logged = True


def print_cards():
    i = 0
    display_cards = []
    for ver in range(360, 720, 45):
        for hor in range(20, 195, 35):
            if i < len(player_one.cards):
                display_cards.append(MiniCard(hor, ver, player_one.cards[i][0], player_one.cards[i][1]))
            i += 1
    for card in display_cards:
        card.draw()
    i = 0
    display_cards = []
    for ver in range(360, 720, 45):
        for hor in range(680, 855, 35):
            if i < len(player_two.cards):
                display_cards.append(MiniCard(hor, ver, player_two.cards[i][0], player_two.cards[i][1]))
            i += 1
    for card in display_cards:
        card.draw()


def end_cond():
    menu_button = ImpButtons("Menu.png", (100, 70), (20, 20))
    if player_one.score > player_two.score:
        player = player_one
    else:
        player = player_two

    viewing = True
    while viewing:
        screen.fill((50, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.rect.collidepoint(event.pos):
                    return "stop program"

        i = 0
        display_cards = []
        for ver in range(360, 720, 45):
            for hor in range(200, 375, 35):
                if i < len(player.cards):
                    display_cards.append(MiniCard(hor, ver, player.cards[i][0], player.cards[i][1]))
                i += 1
        for card in display_cards:
            card.draw()

        base_font = pygame.font.Font(None, 40)
        win_text = base_font.render(f"You Won {player.name}, with {player.score} cards", True, (255, 255, 0))
        screen.blit(win_text, (150, 100))
        screen.blit(menu_button.imp, (menu_button.x, menu_button.y))
        pygame.display.flip()


def play_game():
    menu_button = ImpButtons("Menu.png", (100, 70), (20, 20))
    imp_deck = ImpButtons("Deck icon.png", (104, 150), (488, 40))
    imp_check = ImpButtons("check_icon.png", (80, 80), (500, 200))
    playing = True
    reset_deck()
    divider_rect = pygame.Rect(530, 300, 20, 420)
    turn = True
    fighting = False
    base_font = pygame.font.Font(None, 40)
    win_text = base_font.render("Winner!", True, (0, 255, 0))
    lose_text = base_font.render("Loser!", True, (255, 0, 0))
    winner = ""
    while playing:
        if len(DataBase["Deck"]) == 0:
            stopped = end_cond()
            return "stop program"
        screen.fill((50, 50, 50))
        turn = not turn
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if imp_deck.rect.collidepoint(event.pos) and not fighting:
                    winner = ""
                    fighting = True
                    if turn:
                        first_card = Card(300, 200, DataBase["Deck"][0][0], DataBase["Deck"][0][1])
                        second_card = Card(700, 200, DataBase["Deck"][1][0], DataBase["Deck"][1][1])
                    else:
                        first_card = Card(300, 200, DataBase["Deck"][1][0], DataBase["Deck"][1][1])
                        second_card = Card(700, 200, DataBase["Deck"][0][0], DataBase["Deck"][0][1])

                if imp_check.rect.collidepoint(event.pos) and fighting:
                    fighting = False
                    if DataBase["Colours"][DataBase["Deck"][0][0]] == DataBase["Deck"][1][0]:
                        player_one.score += 2
                        player_one.cards.append(DataBase["Deck"][0])
                        player_one.cards.append(DataBase["Deck"][1])
                        DataBase["Deck"].pop(0)
                        DataBase["Deck"].pop(0)
                        winner = "one"
                    else:
                        player_two.score += 2
                        player_two.cards.append(DataBase["Deck"][0])
                        player_two.cards.append(DataBase["Deck"][1])
                        DataBase["Deck"].pop(0)
                        DataBase["Deck"].pop(0)
                        winner = "two"

                if menu_button.rect.collidepoint(event.pos):
                    return "stop program"

        if fighting:
            second_card.draw()
            first_card.draw()
        if winner == "one":
            screen.blit(win_text, (200, 50))
            screen.blit(lose_text, (800, 50))
        elif winner == "two":
            screen.blit(lose_text, (200, 50))
            screen.blit(win_text, (800, 50))
        print_cards()
        pygame.draw.rect(screen, (0, 0, 0), divider_rect)
        screen.blit(imp_deck.imp, (imp_deck.x, imp_deck.y))
        screen.blit(imp_check.imp, (imp_check.x, imp_check.y))
        screen.blit(base_font.render(("Player One: " + player_one.name), True, (255, 255, 255)), (50, 10))
        screen.blit(base_font.render(("Player Two: " + player_two.name), True, (255, 255, 255)), (700, 10))
        screen.blit(menu_button.imp, (menu_button.x, menu_button.y))
        pygame.display.flip()
        clock.tick(60)


def leaderboard():
    in_leaderboard = True
    base_font = pygame.font.Font(None, 50)
    names = []
    scores = []
    menu_button = ImpButtons("Menu.png", (100, 70), (20, 20))
    for name in DataBase["LeaderBoard"]:
        names.append(base_font.render(name, True, (200, 200, 200)))
        scores.append(base_font.render(str(DataBase["Names"][name]["Score"]), True, (200, 200, 200)))
    while in_leaderboard:
        screen.fill((50, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.rect.collidepoint(event.pos):
                    return "stop program"

        for num in range(5):
            screen.blit(names[num], (200, 20 + (70 * num)))
            screen.blit(scores[num], (700, 20 + (70 * num)))
        screen.blit(menu_button.imp, (menu_button.x, menu_button.y))
        pygame.display.flip()


def edit_profiles():
    global logged
    menu_button = ImpButtons("Menu.png", (100, 70), (20, 20))
    username = ""
    password = ""
    base_font = pygame.font.Font(None, 32)
    large_font = pygame.font.Font(None, 50)
    colour_active = pygame.Color("lightskyblue3")
    colour_passive = pygame.Color("chartreuse4")
    u_colour = colour_passive
    p_colour = colour_passive
    u_active = False
    p_active = False
    username_rect = pygame.Rect(200, 200, 140, 32)
    password_rect = pygame.Rect(200, 262, 140, 32)
    create_rect = pygame.Rect(600, 150, 300, 70)
    delete_rect = pygame.Rect(600, 250, 300, 70)
    create_text = large_font.render("Create Profile", True, (0, 0, 0))
    delete_text = large_font.render("Delete Profile", True, (0, 0, 0))
    editing = True
    error = False
    error_message = ""

    while editing:
        screen.fill((50, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "stop program"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if username_rect.collidepoint(event.pos):
                    u_active = True
                    p_active = False
                if password_rect.collidepoint(event.pos):
                    p_active = True
                    u_active = False
                if create_rect.collidepoint(event.pos):
                    if username not in DataBase["Names"]:
                        DataBase["Names"][username] = {"Password": password, "Score": 0, "Logged_In": False}
                        DataBase["LeaderBoard"] = sorted(list(DataBase["Names"].keys()),
                                                         key=lambda m: DataBase["Names"][m]["Score"], reverse=True)[:5]
                        error = True
                        error_message = "Profile Created"
                        print(DataBase["Names"].keys())
                        save()
                    else:
                        error = True
                        error_message = "Username already taken"
                if delete_rect.collidepoint(event.pos):
                    try:
                        if DataBase["Names"][username]["Password"] == password:
                            del DataBase["Names"][username]
                            try:
                                DataBase["LeaderBoard"].remove(username)
                            except ValueError:
                                pass
                            error = True
                            error_message = "Deleted Profile"
                            save()
                            logged = False
                        else:
                            error = True
                            error_message = "Password does not match"
                    except KeyError:
                        error = True
                        error_message = "Username does not exist"
                if menu_button.rect.collidepoint(event.pos):
                    return "stop program"
            if event.type == pygame.KEYDOWN and u_active:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode.lower()
            if event.type == pygame.KEYDOWN and p_active:
                if event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                else:
                    password += event.unicode.lower()

        u_colour = colour_active if u_active else colour_passive
        p_colour = colour_active if p_active else colour_passive

        pygame.draw.rect(screen, u_colour, username_rect)
        users_surf = base_font.render(username, True, (255, 255, 255))
        screen.blit(users_surf, (username_rect.x + 5, username_rect.y + 5))
        username_rect.w = 250

        pygame.draw.rect(screen, p_colour, password_rect)
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

        if error:
            screen.blit(base_font.render(error_message, True, (255, 0, 0)), (100, 100))
        screen.blit(menu_button.imp, (menu_button.x, menu_button.y))
        pygame.display.flip()


def main_menu():
    in_menu = True
    error = False
    base_font = pygame.font.Font(None, 70)
    small_font = pygame.font.Font(None, 50)
    error_display = small_font.render("", True, (255, 0, 0))
    sign_rect = pygame.Rect(370, 100, 350, 70)
    play_rect = pygame.Rect(370, 200, 350, 70)
    leaderboard_rect = pygame.Rect(370, 300, 350, 70)
    edit_rect = pygame.Rect(370, 400, 350, 70)
    exit_rect = pygame.Rect(370, 500, 350, 70)
    sign_text = base_font.render("Sign In", True, (0, 0, 0))
    play_text = base_font.render("Play", True, (0, 0, 0))
    leaderboard_text = base_font.render("Leaderboard", True, (0, 0, 0))
    edit_text = base_font.render("Edit Profiles", True, (0, 0, 0))
    exit_text = base_font.render("Exit", True, (0, 0, 0))
    while in_menu:
        screen.fill((50, 50, 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sign_rect.collidepoint(event.pos):
                    sign_in()
                    error = False
                if play_rect.collidepoint(event.pos) and logged:
                    play_game()
                    save()
                    player_one.cards = []
                    player_two.cards = []
                elif play_rect.collidepoint(event.pos):
                    error_display = small_font.render("You need to log in first", True, (255, 0, 0))
                    error = True
                if leaderboard_rect.collidepoint(event.pos):
                    leaderboard()
                if edit_rect.collidepoint(event.pos):
                    edit_profiles()
                if exit_rect.collidepoint(event.pos):
                    pygame.quit()

        pygame.draw.rect(screen, (200, 200, 200), sign_rect)
        pygame.draw.rect(screen, (200, 200, 200), play_rect)
        pygame.draw.rect(screen, (200, 200, 200), leaderboard_rect)
        pygame.draw.rect(screen, (200, 200, 200), edit_rect)
        pygame.draw.rect(screen, (200, 200, 200), exit_rect)
        screen.blit(sign_text, (sign_rect.x + 90, sign_rect.y + 10))
        screen.blit(play_text, (play_rect.x + 120, play_rect.y + 10))
        screen.blit(leaderboard_text, (leaderboard_rect.x + 10, leaderboard_rect.y + 10))
        screen.blit(edit_text, (edit_rect.x + 35, edit_rect.y + 10))
        screen.blit(exit_text, (exit_rect.x + 120, exit_rect.y + 10))
        if error:
            screen.blit(error_display, (530 - (error_display.get_width() // 2), 50))
        pygame.display.flip()


logged = False
main_menu()
pygame.quit()
