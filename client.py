import requests, datetime, threading, sys
from tkinter import *
from datetime import timedelta

def user_login(base_url, username, password):
    data = {"username":username, "password":password} 
    response = requests.post(f"{base_url}/login", json = data) 
    return response.json(), response.status_code

def create_user(base_url, username, password):
    data =  {"username":username, "password":password}
    response = requests.post(f"{base_url}/create_user", json = data)
    return response.json(), response.status_code

def create_item(base_url, owner, name, description):
    data = {"owner":owner, "name":name, "description":description}
    response = requests.post(f"{base_url}/create_item", json = data)
    return response.json(), response.status_code

def create_auction(base_url, itemID, seller, price, TTL):
    data =  {"item_id":itemID, "seller_id":seller, "price":price, "ttl":TTL}
    response = requests.post(f"{base_url}/create_auction", json = data)
    return response.json(), response.status_code

def place_bid(base_url, bid_amount, user_id, auction_id):
    data = {"bid_amount":bid_amount,"user_id":user_id,"auction_id":auction_id}
    response = requests.post(f"{base_url}/place_bid", json=data)
    return response.json(), response.status_code

def seen_notification(base_url, notif_id):
    data = {"notif_id":notif_id}
    response = requests.post(f"{base_url}/seen_notification", json=data)
    return response.json(), response.status_code

def update_chat(base_url, user1, user2, data):
    data = {"user1":user1,"user2":user2, "data":data}
    response = requests.post(f"{base_url}/update_chat", json=data)
    return response.json(), response.status_code

def get_ended_auctions(base_url):
    response = requests.get(f"{base_url}/ended_auctions")
    return response.json(), response.status_code

def get_running_auctions(base_url):
    response = requests.get(f"{base_url}/running_auctions")
    return response.json(), response.status_code

def get_all_auctions(base_url):
    response = requests.get(f"{base_url}/all_auctions")
    return response.json(), response.status_code

def get_user(base_url, user_id):
    response = requests.get(f"{base_url}/user", params={"user_id":user_id})
    return response.json(), response.status_code

def get_item(base_url, item_id):
    response = requests.get(f"{base_url}/item", params={"item_id":item_id})
    return response.json(), response.status_code

def get_inventory(base_url, user_id):
    response = requests.get(f"{base_url}/inventory", params={"user_id":user_id})
    return response.json(), response.status_code

def check_new_notifications(base_url, user_id):
    response = requests.get(f"{base_url}/check_new_notifications", params={"user_id":user_id})
    return response.json(), response.status_code

def get_notifications(base_url, user_id):
    response = requests.get(f"{base_url}/get_notifications", params={"user_id":user_id})
    return response.json(), response.status_code

def get_chat(base_url, user1, user2):
    response = requests.get(f"{base_url}/get_chat", params={"user1":user1,"user2":user2})
    return response.json(), response.status_code

def get_all_chats(base_url, user_id):
    response = requests.get(f"{base_url}/get_all_chats", params={"user_id":user_id})
    return response.json(), response.status_code

def get_chat_updates(base_url, user1, user2, oldCount):
    response = requests.get(f'{base_url}/get_chat_updates', params={'user1': user1, 'user2': user2, 'oldCount': oldCount})
    return response.json(), response.status_code



_done = False
_login = False
_user = None
BASE_URL = 'N/A' # middle ware server
#BASE_URL = 'http://127.0.0.1:5000' 


def _new_notifications(user_id):
    result, code = get_notifications(BASE_URL, user_id)
    if code == 200:
        for notif in result:
            if notif.get('seen') == False:
                return True
        return False
    if code == 400:
        print(result.get('msg'))
        return False
    if code == 404:
        return False
    
def _doLogin():
        u = input('username> ')
        p = input('password> ')
        result, code = user_login(BASE_URL, u, p)
        if code == 200:
            globals()['_user'] = result
            globals()['_login'] = True
        else:
            print(result.get('msg'))

def _doLogout():
        globals()['_user'] = None
        globals()['_login'] = False

def _doExit():
    globals()['_done'] = True
    globals()['_user'] = None
    globals()['_login'] = False
    print('Goodbye')

def _doCreateuser():
    u = input('username> ')
    p = input('password> ')
    result, code = create_user(BASE_URL, u, p)
    print(result.get('msg'))

def run():
    print('Welcome')
    while (_done == False):
        if (_login == False):
            _doMainMenu()
        else:
            _doLoggedInMenu()
        
def _doMainMenu():
    menu = ['1.   Login',
            '2.   Register',
            '99.  Exit']
    choices = {'1': _doLogin,
               '2': _doCreateuser,
                '99': _doExit}
    print('\nMenu:')
    print('\n'.join(menu))
    print('\n', end='')
    choice = input('> ')
    if choice in choices:
        m = choices[choice]
        m()

def _doLoggedInMenu():
    menu = ['1.   Create Item',
                '2.   Create Auction',
                '3.   Check Inventory',
                '4.   Check Items For Sale',
                '5.   Bid',
                '6.   Auction History',
                '7.   Notifications',
                '8.   Chats',
                '98.  Logout',
                '99.  Exit']
    choices = {'1': _doCreateItem,
                '2': _doCreateAuction,
                '3': _doCheckInventory,
                '4': _doItemsForSale,
                '5': _doUserBid,
                '6': _doAuctionHistoryMenu,
                '7': _doCheckNotifications,
                '8': _doChats,
                '98': _doLogout,
                '99': _doExit}
    if _new_notifications(_user.get('id')):
        menu[6] = '7.   Notifications (New!)'
    print('\nMenu:')
    print('\n'.join(menu))
    print('\n', end='')
    choice = input(_user.get('username') + '> ')
    if choice in choices:
        m = choices[choice]
        m()    

def _doCheckInventory():
    result, code = get_inventory(BASE_URL, _user.get('id'))
    if code != 200:
        print(result.get('msg'))
        return

    if result:
        print("Inventory:")
        for i, item in enumerate(result):
            print(str(i + 1) + ". " + item.get('name') + ": " + item.get('description')) 
    else:
        print("Inventory is empty")
    
def _doAuctionHistoryMenu():
    menu = ['1.   Items Sold',
            '2.   Auctions Won']
    choices = {'1': _doItemsSold,
                '2': _doAuctionsWon}
    print('\nMenu:')
    print('\n'.join(menu))
    print('\n', end='')
    choice = input(_user.get('username') + '> ')
    if choice in choices:
        m = choices[choice]
        m()

def _doItemsSold():
    result, code = get_ended_auctions(BASE_URL)
    if code != 200:
        print(result.get('msg'))
        return
    
    itemsSold = []
    bidders = []
    for auc in result:
        if auc.get('seller') == _user.get('id') and auc.get('highestBidder') != None:
            itemsSold.append(auc.get('itemID'))
            bidders.append(auc.get('highestBidder'))

    if itemsSold:
        print("Items Sold:")
        for i, item in enumerate(itemsSold):
            item, code = get_item(BASE_URL, item)
            if code != 200:
                print(result.get('msg'))
                return
            buyer, code = get_user(BASE_URL, bidders[i])
            if code != 200:
                print(result.get('msg'))
                return
            print("Item:", item.get('name'), "|", "Description:", item.get('description'), "|", "Bought by:", buyer.get('username'))
    else:
        print("No Items Sold")
    
def _doAuctionsWon():
    result, code = get_ended_auctions(BASE_URL)
    if code != 200:
        print(result.get('msg'))
        return
    
    aucsWon = []
    for auc in result:
        if auc.get('highestBidder') == _user.get('id'):
            aucsWon.append(auc)

    if aucsWon:
        print("Auctions Won:")
        for auc in aucsWon:
            item, code = get_item(BASE_URL,auc.get('itemID'))
            if code != 200:
                print(result.get('msg'))
                return
            seller, code = get_user(BASE_URL,auc.get('seller'))
            if code != 200:
                print(result.get('msg'))
                return
            print("Auctioned Item:", item.get('name'), "|", "Description:", item.get('description'), "|", "Price:", auc.get('price'), 
                "|", "Date:", auc.get('date'), "|", "Sold By:", seller.get('username'))
    else:
        print("No Auctions Won")

def _doCheckNotifications():
    result, code = get_notifications(BASE_URL, _user.get('id'))
    if code != 200:
        print(result.get('msg'))
        return 

    choices = dict()
    print("Notifications:")
    for i, notif in enumerate(result):
        choices.update({i+1:notif})
        if notif.get('seen') == True:
            print(f"{i+1}. Date:{notif.get('date')} | Subject: Auction Results")
        else:
            print(f"{i+1}. Date:{notif.get('date')} | Subject: Auction Results (New!)")
        
    choice = input(f"{_user.get('username')}> Select to read notification: ")
    while True:
        if int(choice) in choices:
            notification = choices[int(choice)] 
            break
        else:
            choice = input(_user.get('username') + "> Invalid input, please try again: ")

    print(f"{choice}. Date:{notification.get('date')} | Subject: Auction Results")
    print(f"\tMessage: {notification.get('message')}")

    result, code = seen_notification(BASE_URL, notification.get('id'))
    print(result.get('msg'))


class ChatUpdater(threading.Thread):
    def __init__(self, user1, user2):
        super().__init__()
        self.user1 = user1
        self.user2 = user2
        self.stop_event = threading.Event()
        self.data = ''

    def run(self):

        # get previous chat logs
        result, code = get_chat(BASE_URL, self.user1, self.user2)
        if code != 200:
            print(result.get('msg'))
            self.stop()
            return
        
        logs = result.get('logs')
        oldCount = logs.count('\\n')

        formatted_logs = logs.replace("\\n", '\n')
        print(formatted_logs)
        
        while not self.stop_event.is_set():
            result, code = get_chat_updates(BASE_URL, self.user1, self.user2, oldCount)

            if code != 200:
                print(result.get('msg'))
                self.stop()
                return
            
            if result.get('logs') != '':
                print(f"{result.get('logs')}")

            oldCount = result.get('newCount')

    def stop(self):
        self.stop_event.set()

class InputHandler(threading.Thread):
    def __init__(self, user1, user2):
        super().__init__()
        self.user1 = user1
        self.user2 = user2
        self.stop_event = threading.Event()

    def run(self):
        print("Press quit on tk terminal to leave the chat")
        while not self.stop_event.is_set():
            user_input = input()
            user_input = f"{_user.get('username')}: " + user_input
            result, code = update_chat(BASE_URL, self.user1, self.user2, user_input)
            if code != 200:
                print(result.get('msg'))
                return

    def stop(self):
        self.stop_event.set()

def _doChats():
    result, code = get_all_chats(BASE_URL, _user.get('id'))
    if code != 200:
        print(result.get('msg'))
        return

    choices = dict()
    print("Chats:")
    for i, chat in enumerate(result):
        choices.update({i+1:chat})
        
        if chat.get('user1') == _user.get('id'):
            result, code = get_user(BASE_URL, chat.get('user2'))
        else:
            result, code = get_user(BASE_URL, chat.get('user1'))
        
        if code != 200:
            print(result.get('msg'))
            return 
        
        print(f"{i+1}. User: {result.get('username')}")

    choices.update({len(choices)+1: 'Exit'})
    print(f"{len(choices)}. Exit")

    choice = input(f"{_user.get('username')}> Select chat to open: ")
    while True:
        if int(choice) in choices:
            chat = choices[int(choice)] 
            break
        else:
            choice = input(_user.get('username') + "> Invalid input, please try again: ")

    if chat == 'Exit':
        return
    
    chat_updater = ChatUpdater(chat.get('user1'), chat.get('user2'))
    input_handler = InputHandler(chat.get('user1'), chat.get('user2'))

    chat_updater.start()
    input_handler.start()

    orig_stdout = sys.stdout

    class window(Tk):
        def __init__(self):
            Tk.__init__(self)
            toolbar = Frame(self)
            toolbar.pack(side="top", fill="x")
            Button(self, text="Quit", command=self.destroy).pack() 
            self.text = Text(self, wrap="word")
            self.text.pack(side="top", fill="both", expand=True)
            sys.stdout = TextRedirector(self.text, "Chat")

    class TextRedirector(object):
        def __init__(self, widget, tag="stdout"):
            self.widget = widget
            self.tag = tag

        def write(self, string):
            self.widget.configure(state="normal")
            self.widget.insert("end", string, (self.tag,))
            self.widget.configure(state="disabled")

        def flush(self):
            pass
                    
    win = window()
    win.mainloop()

    sys.stdout = orig_stdout
    
    chat_updater.stop()
    input_handler.stop()

        
def _doCreateItem():
    name = input(_user.get('username') + '> Item Name: ')
    description = input(_user.get('username') + '> Item Description: ')
    result, code = create_item(BASE_URL, _user.get('id'), name, description)
    print(result.get('msg'))

def _doCreateAuction():
    result, code = get_inventory(BASE_URL, _user.get('id'))
    if code != 200:
        print(result.get('msg'))
        return

    if result:
        choices = dict()
        print("Inventory:")
        for i, item in enumerate(result):
            choices.update({i+1: item})
            print(str(i + 1) + ". " + item.get('name') + ": " + item.get('description'))
        choice = input(_user.get('username') + "> Select item from inventory: ")
        while True:
            if int(choice) in choices:
                item = choices[int(choice)] 
                break
            else:
                choice = input(_user.get('username') + "> Invalid input, please try again: ")
    else:
        print("Please create a new Item first")
        return

    price = input(_user.get('username') + '> Enter starting Price: ')
    while(True):
        try:
            float(price)
            break
        except ValueError:
            price = input(_user.get('username') + "> Invalid input, enter a floating point number: ")

    TTL = input('Enter length of auction (in seconds)> ')
    while(True):
        try:
            int(TTL)
            if int(TTL) < 0:
                TTL = input(_user.get('username') + ">Invalid input, enter a positive integer: ")
            elif int(TTL) >= 0 and int(TTL) < 60:
                TTL = input(_user.get('username') + "> Invalid input, must be at least 60 seconds: ")
            else:
                break
        except ValueError:
            TTL = input(_user.get('username') + "> Invalid input, enter an integer: ")
        
    result, code = create_auction(BASE_URL, item.get('id'), _user.get('id'), price, int(TTL))
    print(result.get('msg'))
    
def _doItemsForSale():
    result, code = get_running_auctions(BASE_URL)
    if code != 200:
        print(result.get('msg'))
        return

    if result:
        print("Items For Sale:")
        for auc in result:
            item, code = get_item(BASE_URL,auc.get('itemID'))
            if code != 200:
                print(result.get('msg'))
                return
            seller, code = get_user(BASE_URL,auc.get('seller'))
            if code != 200:
                print(result.get('msg'))
                return
            date = datetime.datetime.strptime(auc.get('date'), '%a, %d %b %Y %H:%M:%S %Z')
            ttl = timedelta(seconds=int(auc.get('TTL')))
            td = date + ttl - datetime.datetime.now()
            hours = td.seconds // 3600
            minutes = (td.seconds % 3600) // 60
            seconds = td.seconds % 60

            print("Auctioned Item:", item.get('name'), "|", "Description:", 
                  item.get('description'), "|", "Price:", auc.get('price'), "|", 
                  "Sold By:", seller.get('username'), "|", 
                  "Time Left:",  hours, "Hours", minutes, "Minutes", seconds, "Seconds"
            )
    else:
        print("No items for sale")

def _doUserBid():
    result, code = get_running_auctions(BASE_URL)
    if code != 200:
        print(result.get('msg'))
        return

    choices = dict()
    if result:
        print("Available Auctions:")
        counter = 0
        for i, auc in enumerate(result):
            if auc.get('seller') != _user.get('id'):
                choices.update({i + 1 - counter: auc})
                item, code = get_item(BASE_URL,auc.get('itemID'))
                if code != 200:
                    print(result.get('msg'))
                    return
                seller, code = get_user(BASE_URL,auc.get('seller'))
                if code != 200:
                    print(result.get('msg'))
                    return
                date = datetime.datetime.strptime(auc.get('date'), '%a, %d %b %Y %H:%M:%S %Z')
                ttl = timedelta(seconds=int(auc.get('TTL')))
                td = date + ttl - datetime.datetime.now()
                hours = td.seconds // 3600
                minutes = (td.seconds % 3600) // 60
                seconds = td.seconds % 60

                print(str(i+1 - counter) + ". Auctioned Item:", item.get('name'), "|", "Description:", 
                    item.get('description'), "|", "Price:", auc.get('price'), "|", 
                    "Sold By:", seller.get('username'), "|", 
                    "Time Left:",  hours, "Hours", minutes, "Minutes", seconds, "Seconds"
                )   
            else:
                counter+=1
        if len(choices) == 0:
            print("No auctions available for bidding (Cannot bid on your own auctions)")
            return
    else:
        print("No auctions currently running")
        return

    choice = input(_user.get('username') + "> Select auction: ")
    while True:
        if int(choice) in choices:
            auction = choices[int(choice)] 
            break
        else:
            choice = input(_user.get('username') + "> Invalid input, please try again: ")

    price = input(_user.get('username') + '> Enter bid amount: ')
    while(True):
        try:
            float(price)
            break
        except ValueError:
            price = input(_user.get('username') + "> Invalid input, enter a floating point number: ")

    result, code = place_bid(BASE_URL, float(price), _user.get('id'), auction.get('id'))
    print(result.get('msg'))

run()