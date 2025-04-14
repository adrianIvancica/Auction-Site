import urllib, hashlib, secrets, datetime, json
from flask import Flask, jsonify, request, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, desc, or_, and_, func
from sqlalchemy.orm import scoped_session, sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler

DATABASE_HOST = "N/A"
DATABASE_NAME = "N/A"
DATABASE_USERNAME = "N/A" 
DATABASE_PASSWORD = "N/A"

app = Flask(__name__)

# to elimate the error, if the password contains special characters like '@' 
DATABASE_PASSWORD_UPDATED = urllib.parse.quote_plus(DATABASE_PASSWORD)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://'+DATABASE_USERNAME+':'+DATABASE_PASSWORD_UPDATED+'@'+DATABASE_HOST+'/'+DATABASE_NAME
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
with app.app_context():
    db_session = scoped_session(sessionmaker(autocommit=False,
                                            autoflush=False,
                                            bind=db.engine))

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Define database model
class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.String(256), primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password
        }

class Item(db.Model):
    __tablename__ = 'Item'

    id = db.Column(db.String(256), primary_key=True)
    owner = db.Column(db.String(256), db.ForeignKey('User.id'))
    name = db.Column(db.String(255))
    description = db.Column(db.Text)

    owner_rel = db.relationship('User', backref='items')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'description': self.description
        }

class Auction(db.Model):
    __tablename__ = 'Auction'

    id = db.Column(db.String(256), primary_key=True)
    itemID = db.Column(db.String(256), db.ForeignKey('Item.id'))
    seller = db.Column(db.String(256), db.ForeignKey('User.id'))
    price = db.Column(db.Float)
    highestBidder = db.Column(db.String(256), db.ForeignKey('User.id'))
    TTL = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    endedF = db.Column(db.Boolean)

    item_rel = db.relationship('Item', backref='auctions')
    seller_rel = db.relationship('User', foreign_keys=[seller], backref='auctions_as_seller')
    highest_bidder_rel = db.relationship('User', foreign_keys=[highestBidder], backref='auctions_as_highest_bidder')
    
    def to_dict(self):
        return {
            'id': self.id,
            'itemID': self.itemID,
            'seller': self.seller,
            'price': self.price,
            'highestBidder': self.highestBidder,
            'TTL': self.TTL,
            'date': self.date,
            'endedF': self.endedF
        }

class Notification(db.Model):
    __tablename__ = 'Notifications'

    id = db.Column(db.String(256), primary_key=True)
    userID = db.Column(db.String(256), db.ForeignKey('User.id'))
    message = db.Column(db.Text)
    date = db.Column(db.DateTime)
    seen = db.Column(db.Boolean)

    user_rel = db.relationship('User', backref='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'userID': self.userID,
            'message': self.message,
            'date': self.date,
            'seen': self.seen
        }

class Chat(db.Model):
    __tablename__ = 'Chats'

    user1 = db.Column(db.String(256), db.ForeignKey('User.id'), primary_key=True)
    user2 = db.Column(db.String(256), db.ForeignKey('User.id'), primary_key=True)
    logs = db.Column(db.Text)

    user1_rel = db.relationship('User', foreign_keys=[user1], backref='chats_as_user1')
    user2_rel = db.relationship('User', foreign_keys=[user2], backref='chats_as_user2')

    def to_dict(self):
        return {
            'user1': self.user1,
            'user2': self.user2,
            'logs': self.logs
        }


# GET functions API
@app.route('/user', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')
    with db_session() as session:
        user = session.query(User).get(user_id)
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'msg': 'User does not exist'}), 404

@app.route('/inventory', methods=['GET'])
def get_user_inventory():
    user_id = request.args.get('user_id')
    with db_session() as session:
        user = session.query(User).get(user_id)
        if user:
            return jsonify([item.to_dict() for item in user.items]), 200
        else:
            return jsonify({'msg': 'User does not exist'}), 404
    
@app.route('/item', methods=['GET'])
def get_item():
    item_id = request.args.get('item_id')
    with db_session() as session:
        item = session.query(Item).get(item_id)
        if item:
            return jsonify(item.to_dict()), 200
        else:
            return jsonify({'msg': 'Item does not exist'}), 404
    
@app.route('/ended_auctions', methods=['GET'])
def get_ended_auctions():
    with db_session() as session:
        auctions = session.query(Auction).filter(Auction.endedF == 1).all()
        return jsonify([auction.to_dict() for auction in auctions]), 200

@app.route('/running_auctions', methods=['GET'])
def get_running_auctions():
    with db_session() as session:
        auctions = session.query(Auction).filter(Auction.endedF == 0).all()
        return jsonify([auction.to_dict() for auction in auctions]), 200
    
@app.route('/all_auctions', methods=['GET'])
def get_all_auctions():
    with db_session() as session:
        auctions = session.query(Auction).all()
        return jsonify([auction.to_dict() for auction in auctions]), 200

@app.route('/check_new_notifications', methods=['GET'])
def check_new_notifications():
    user_id = request.args.get('user_id')
    if user_id:
        with db_session() as session:
            count = session.query(func.count(Notification.id)).filter_by(userID=user_id, seen=False).scalar()
            return jsonify(count), 200
    else:
        return jsonify({'msg': 'Missing user_id'}), 400

@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    user_id = request.args.get('user_id')
    if user_id:
        with db_session() as session:
            notifications = session.query(Notification).filter_by(userID=user_id).order_by(desc(Notification.date)).all()
            if notifications:
                return jsonify([notif.to_dict() for notif in notifications]), 200
            else:
                return jsonify({'msg': 'No notifications found'}), 404
    else:
        return jsonify({'msg': 'Missing user_id'}), 400

@app.route('/get_chat', methods=['GET'])
def get_chat():
    user1 = request.args.get('user1')
    user2 = request.args.get('user2')

    if not all([user1, user2]):
        return jsonify({'msg': 'Missing user1 or user2'}), 400
    
    with db_session() as session:
        chat = session.query(Chat).filter(or_((Chat.user1 == user1) & (Chat.user2 == user2), (Chat.user1 == user2) & (Chat.user2 == user1))).first()
        if chat:
            return jsonify({'logs': chat.logs}), 200
        else:
            return jsonify({'msg': 'Chat not found'}), 404

@app.route('/get_chat_updates', methods=['GET'])
def get_chat_updates():

    user1 = request.args.get('user1')
    user2 = request.args.get('user2')
    oldCount = request.args.get('oldCount')

    with db_session() as session:
        chat = session.query(Chat).filter(
            ((Chat.user1 == user1) & (Chat.user2 == user2)) |
            ((Chat.user1 == user2) & (Chat.user2 == user1))
        ).first()

        if not chat:
            return jsonify({'msg': 'Chat not found'}), 404
        
        # check if there is new data and return it
        newCount = chat.logs.count('\\n')
        if ((newCount - oldCount) > 0):
            c = 0
            oldPos=0
            newPos=0
            for i in range(len(chat.logs)):
                j = i+1
                if j == len(chat.logs):
                    break
                if chat.logs[i] == '\\' and chat.logs[j] == 'n':
                    c += 1
                    if c == oldCount:
                        oldPos = i
                    if c == newCount:
                        newPos = i
                        newData = chat.logs[oldPos+2:newPos]
                        return jsonify({'logs': newData, 'newCount': newCount}), 200
        else:
            return jsonify({'logs': '', 'newCount': newCount}), 200

@app.route('/get_all_chats', methods=['GET'])
def get_all_chats():
    user_id = request.args.get('user_id')
    
    if user_id:
        with db_session() as session:
            chats = session.query(Chat).filter((Chat.user1 == user_id) | (Chat.user2 == user_id)).all()
            if chats:
                return jsonify([chat.to_dict() for chat in chats]), 200
            else:
                return jsonify({'msg': 'No chats found'}), 404
    else:
        return jsonify({'msg': 'Missing user_id'}), 400
    
    
# POST functions API
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'msg': 'Missing username or password'}), 400

    with db_session() as session:
        users = session.query(User).filter_by(username=username).all()
        for user in users:
            if user.password == password:
                return jsonify(user.to_dict()), 200
            
    return jsonify({'msg': 'Invalid username or password'}), 401

@app.route('/update_user', methods=['POST'])
def update_user():
    user_id = request.json.get('user_id')
    new_username = request.json.get('new_username')
    new_password = request.json.get('new_password')

    with db_session() as session:
        user = session.query(User).get(user_id)

        if user:
            if new_username:
                user.username = new_username
            if new_password:
                user.password = new_password

            session.commit()
            return jsonify({'msg': 'User updated successfully'}), 200
        else:
            return jsonify({'msg': 'User not found'}), 404

@app.route('/update_chat', methods=['POST'])
def update_chat():
    user1 = request.json.get('user1')
    user2 = request.json.get('user2')
    data = request.json.get('data')

    if not all([user1, user2, data]):
        return jsonify({'msg': 'Missing arguments'}), 400
    
    with db_session() as session:
        chat = session.query(Chat).filter(or_((Chat.user1 == user1) & (Chat.user2 == user2), (Chat.user1 == user2) & (Chat.user2 == user1))).first()
        if chat:
            if data[-1] == '\n':
                data[-1] = '\\'
                data += 'n'
                chat.logs += data
            elif len(data) == 1:
                data += "\\n"
            elif len(data) >= 2 and data[-2] != '\\' and data[-1] != 'n':
                data += "\\n"

            chat.logs += data

            session.commit()
            return jsonify({'msg': 'Chat updated successfully'}), 200
        else:
            return jsonify({'msg': 'Chat not found'}), 404
        

@app.route('/place_bid', methods=['POST'])
def place_bid():
    bid_amount = request.json.get('bid_amount')
    user_id = request.json.get('user_id')
    auction_id = request.json.get('auction_id')

    if not bid_amount or bid_amount <= 0:
        return jsonify({'msg': 'Invalid bid amount'}), 400
    
    with db_session() as session:
        auction = session.query(Auction).get(auction_id)
        if not auction:
            return jsonify({'msg': 'Auction not found'}), 404

        if bid_amount <= auction.price:
            return jsonify({'msg': 'Bid amount must be higher than current bid'}), 400

        auction.price = bid_amount
        auction.highestBidder = user_id
        session.commit()
        return jsonify({'msg': 'Bid placed successfully'}), 200

@app.route('/create_auction', methods=['POST'])
def create_auction():
    data = request.json
    item_id = data.get('item_id')
    seller_id = data.get('seller_id')
    price = data.get('price')
    ttl = data.get('ttl')

    if not all([item_id, seller_id, price, ttl]):
        return jsonify({'msg': 'Missing required data'}), 400

    with db_session() as session:
        item = session.query(Item).filter_by(id=item_id).first()
        if item:
            auctions = item.auctions
            if auctions:
                runningAuctions = [auction.id for auction in auctions if auction and not auction.endedF]
                if runningAuctions:
                    return jsonify({'msg': 'Item currently in auction', 'auction_ids': runningAuctions}), 409
        else:
            return jsonify({'msg': 'Item not found'}), 404

        salt = secrets.token_hex(16)
        combined_data = f"{item_id}-{seller_id}-{price}-{ttl}-{salt}"
        auction_id = hashlib.sha256(combined_data.encode()).hexdigest()

        new_auction = Auction(
                id=auction_id,
                itemID=item_id,
                seller=seller_id,
                price=price,
                highestBidder=None,
                TTL=ttl,
                date=datetime.datetime.now(),  
                endedF=False  
            )

        session.add(new_auction)
        session.commit()

        return jsonify({'msg': 'Auction created successfully'}), 201

@app.route('/create_item', methods=['POST'])
def create_item():
    data = request.json
    owner_id = data.get('owner')
    name = data.get('name')
    description = data.get('description')

    if not all([owner_id, name, description]):
        return jsonify({'error': True, 'msg': 'Missing required data'}), 400
    
    salt = secrets.token_hex(16)
    combined_data = f"{owner_id}-{name}-{description}-{salt}"
    item_id = hashlib.sha256(combined_data.encode()).hexdigest()

    new_item = Item(
        id=item_id,
        owner=owner_id,
        name=name,
        description=description
    )

    with db_session() as session:
        session.add(new_item)
        session.commit()
        return jsonify({'msg': 'Item created successfully'}), 201
    
@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'msg': 'Missing username or password'}), 400
    
    salt = secrets.token_hex(16)
    combined_data = f"{username}-{password}-{salt}"
    user_id = hashlib.sha256(combined_data.encode()).hexdigest()

    new_user = User(
        id=user_id,
        username=username, 
        password=password
        )
    
    with db_session() as session:
        session.add(new_user)
        session.commit()
        return jsonify({'msg': 'New user created successfully'}), 201
    
@app.route('/seen_notification', methods=['POST'])
def seen_notification():
    data = request.json
    notif_id = data.get('notif_id')
    if notif_id:
        with db_session() as session:
            notification = session.query(Notification).filter_by(id=notif_id).first()
            if notification:
                notification.seen = True
                session.commit()
                return jsonify({'msg': 'Notification updated successfully'}), 200
            else:
                return jsonify({'msg': 'Notification not found'}), 404
    else:
        return jsonify({'msg': 'Missing notification id'}), 400

# Async Functions
def send_notification(userID, message, session):
    salt = secrets.token_hex(16)
    combined_data = f"{userID}-{message}-{salt}"
    notif_id = hashlib.sha256(combined_data.encode()).hexdigest()

    new_notif = Notification(
            id=notif_id, 
            userID=userID, 
            message=message, 
            date=datetime.datetime.now(),
            seen=False
            )
    
    session.add(new_notif)
    #session.commit() must be done outside of the function

def create_chat(user1, user2, session):
    result = session.query(Chat).filter(or_((Chat.user1 == user1) & (Chat.user2 == user2), (Chat.user1 == user2) & (Chat.user2 == user1))).all()
    if result:
        if len(result) > 1:
            raise Exception(f"Multiple chats between {user1} and {user2}")
        else:
            return
    else:
        new_chat = Chat(user1=user1, user2=user2, logs='')
        session.add(new_chat)
        #session.commit() done outside of function

def auction_notifications(auction_id, session):
    
    auction = session.query(Auction).get(auction_id)
    if auction.highestBidder == None:
        message = f"Auction has ended. Item: {auction.item_rel.name} not sold"
        send_notification(auction.seller, message, session)
    else:
        # assign new item owner
        auction.item_rel.owner = auction.highestBidder

        # send notifications
        # To seller
        message = f"Item: {auction.item_rel.name} sold to {auction.highest_bidder_rel.username}"
        send_notification(auction.seller, message, session)
        # To buyer
        message = f"You won the Auction! Item: {auction.item_rel.name} is now in your inventory"
        send_notification(auction.highestBidder, message, session)

    #session.commit() done outside of function

def check_auction_ended():
    with db_session() as session:
        current_time = datetime.datetime.now()
        auctions = session.query(Auction).filter_by(endedF=False).all()
        for auction in auctions:
            if auction.date + datetime.timedelta(seconds=auction.TTL) <= current_time:
                auction.endedF = True
                auction_notifications(auction.id, session)
                create_chat(auction.seller, auction.highestBidder, session)
                session.commit()

scheduler.add_job(check_auction_ended, 'interval', seconds=1)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True, threaded=True)  
