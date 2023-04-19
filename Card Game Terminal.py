import random
import gmpy2


def key_gen():
    key = ""
    for key_tmp in range(10, 100_000, 123):
        key += str(gmpy2.next_prime(key_tmp))
    return key


def decrypt(message):
    key = key_gen()
    k = []
    for n, c in enumerate(message):
        if c == "\n":
            k.append("\n")
        else:
            k.append(chr(ord(c) - int(key[n % len(key)])))
    return "".join(k)


def encrypt(message):
    key = key_gen()
    k = []
    for n, c in enumerate(message):
        k.append(chr(ord(c) + int(key[n % len(key)])))
    return "".join(k)


# Data Base setup: read from CSV file
try:
    with open("DataBase.txt", "r") as f:
        contents = f.readlines()
except FileNotFoundError:
    with open("DataBase", "w") as f:
        contents = []

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


# take user inputs and make sure they "login"
def authorize():
    auth_username = str(input("Username: ")).lower()
    auth_password = str(input("Password: "))
    if auth_username in DataBase["Names"] and DataBase["Names"][auth_username]["Password"] == auth_password and not \
            DataBase["Names"][auth_username]["Logged_In"]:

        DataBase["Names"][auth_username]["Logged_In"] = True
        print("Signed in player: " + auth_username + "\n")
        return auth_username
    else:
        print("invalid username or password, please try again\n")
        return False


# PLayer object holds data for each player (can easily be expanded)
class Player:
    def __init__(self, p_name):
        self.name = p_name
        self.play = DataBase["LeaderBoard"].index(p_name)
        self.score = 0
        self.cards = []


# initialise player objects
def sign_in():
    for m in DataBase["Names"].keys():
        DataBase["Names"][m]["Logged_In"] = False

    global Player_one, Player_two
    while True:
        if one := authorize():
            Player_one = Player(one)
            break

    while True:
        if two := authorize():
            Player_two = Player(two)
            if Player_one.play >= Player_two.play:
                Player_one.play = 0
                Player_two.play = 1
            else:
                Player_one.play = 1
                Player_two.play = 0
            break


def reset_players():
    Player_one.score = 0
    Player_one.cards = []
    Player_two.score = 0
    Player_two.cards = []


# after deck = 0 gives points to correct player and prints appropriate message
def win_cond():
    if Player_one.score > Player_two.score:
        print(f"Congratulations {Player_one.name}, you won with {Player_one.score} cards!")
        print(f"they had: {Player_one.cards}\n")
        DataBase["Names"][Player_one.name]["Score"] += Player_one.score
    else:
        print(f"Congratulations {Player_two.name}, you won with {Player_two.score} cards!")
        print(f"they had: {Player_two.cards}\n")
        DataBase["Names"][Player_two.name]["Score"] += Player_two.score
    DataBase["LeaderBoard"] = sorted(list(DataBase["Names"].keys()), key=lambda m: DataBase["Names"][m]["Score"],
                                     reverse=True)[:5]
    save_game()


def randomize_deck():
    deck = []
    for c in list(DataBase["Colours"].keys()):
        for k in range(DataBase["CardsCount"]):
            deck.append((c, k + 1))
    random.shuffle(deck)
    DataBase["Deck"] = deck


def save_game():
    file = open("DataBase.txt", "w")
    for s_name in DataBase["Names"].keys():
        tmp_out = f"{s_name},{DataBase['Names'][s_name]['Password']},{DataBase['Names'][s_name]['Score']}"
        file.write(encrypt(tmp_out) + "\n")
    print("Saved\n")


def checker(player):
    player.score += 2
    print(f"{player.name} Won!\nThey had {DataBase['Deck'][player.play][0]} {DataBase['Deck'][player.play][1]}\n")
    player.cards.append(DataBase["Deck"][0])
    player.cards.append(DataBase["Deck"][1])
    DataBase["Deck"].pop(0)
    DataBase["Deck"].pop(0)


def play():
    wait = input("enter to pick cards: ")
    if wait == "cancel":
        raise "Cancel"
    if DataBase["Deck"][1][0] == DataBase["Colours"][DataBase["Deck"][0][0]]:
        checker(Player_one)
    elif DataBase["Deck"][0][0] == DataBase["Colours"][DataBase["Deck"][1][0]]:
        checker(Player_two)
    else:
        if DataBase["Deck"][0][1] > DataBase["Deck"][1][1]:
            checker(Player_one)
        else:
            checker(Player_two)
    if len(DataBase["Deck"]) > 0:
        play()
    else:
        win_cond()


# driver code
# print(DataBase)
while True:
    if len(DataBase["Names"]) < 2:
        print("You need to Create Profile(s):")
        name = input("Please Enter A Username: ")
        password = input("Please Enter A Password: ")
        DataBase["Names"][name] = {"Password": password, "Score": 0, "Logged_In": True}
        DataBase["LeaderBoard"] = sorted(list(DataBase["Names"].keys()), key=lambda m: DataBase["Names"][m]["Score"],
                                         reverse=True)[:5]
        if len(DataBase["Names"]) < 1:
            Player_one = Player(name)
        else:
            Player_two = Player(name)
        save_game()
        print("\n")
        continue

    sign_in_check = [DataBase["Names"][x]["Logged_In"] for x in DataBase["Names"].keys()]
    if not any(sign_in_check):
        print("You need to sign in\n")
        sign_in()

    option = input("1.New Game\n"
                   "2.Leader Board\n"
                   "3.Change User\n"
                   "4.Save Game\n"
                   "5.Create New Player\n"
                   "6.Delete Profile\n"
                   "7.Exit\n"
                   "Option: ").lower()

    if option == "1" or option == "new game":
        randomize_deck()
        reset_players()
        print("\n")
        play()

    elif option == "2" or option == "leader board":
        print("\nLeader Board: ")
        for L_iter in range(len(DataBase["LeaderBoard"])):
            print(DataBase["LeaderBoard"][L_iter] + ": " + str(
                DataBase["Names"][DataBase["LeaderBoard"][L_iter]]["Score"]))
        print("\n")

    elif option == "3" or option == "change user":
        print("Logged Out\n")
        sign_in()

    elif option == "4" or option == "save game":
        save_game()
        print("\n")

    elif option == "5" or option == "create new player":
        print("\n")
        name = input("Please Enter A Username: ")
        password = input("Please Enter A Password: ")
        DataBase["Names"][name] = {"Password": password, "Score": 0, "Logged_In": False}
        DataBase["LeaderBoard"] = sorted(list(DataBase["Names"].keys()), key=lambda m: DataBase["Names"][m]["Score"],
                                         reverse=True)[:5]

    elif option == "6" or option == "Delete Profile":
        confirm = input("Deleting a profile will require you to sign in again\nAre You Sure (Y/N): ").lower()
        if confirm in DataBase["KeyWords"]["Accept"]:
            print(list(DataBase["Names"].keys()))
            prof = input("\nEnter which user you would like to delete\nusername: ").lower()
            password = input("enter user's password: ")
            try:
                if DataBase["Names"][prof]["Password"] == password:
                    del DataBase["Names"][prof]
                    DataBase["LeaderBoard"].remove(prof)
                    print("Profile Deleted\n")
                else:
                    print("Incorrect Password\n")
            except KeyError:
                print("User Does Not Exist\n")
        else:
            continue

    elif option == "7" or option == "exit":
        print("\n")
        break

    else:
        print("Invalid Option\n")

save_game()
