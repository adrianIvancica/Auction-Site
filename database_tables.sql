-- Create User table
CREATE TABLE [User] (
    id VARCHAR(256) PRIMARY KEY,
    username VARCHAR(100),
    [password] VARCHAR(100)
);

-- Create Item table
CREATE TABLE Item (
    id VARCHAR(256) PRIMARY KEY,
    [owner] VARCHAR(256),  -- Assuming owner is the User's ID
    name VARCHAR(255),
    description TEXT,
    FOREIGN KEY ([owner]) REFERENCES [User](id)
);

-- Create Auction table
CREATE TABLE Auction (
    id VARCHAR(256) PRIMARY KEY,
    itemID VARCHAR(256),
    seller VARCHAR(256),  -- Assuming seller is the User's ID
    price FLOAT,
    highestBidder VARCHAR(256),  -- Assuming highestBidder is the User's ID
    TTL INT,
    [date] DATETIME,
    endedF BIT,
    FOREIGN KEY (itemID) REFERENCES Item(id),
    FOREIGN KEY (seller) REFERENCES [User](id),
    FOREIGN KEY (highestBidder) REFERENCES [User](id)
);

-- Create Notifications table
CREATE TABLE Notifications (
    id VARCHAR(256) PRIMARY KEY,
    userID VARCHAR(256),
    message TEXT,
    date DATETIME,
    FOREIGN KEY (userID) REFERENCES [User](id)
);

--Create Chats table
CREATE TABLE Chats (
    User1 VARCHAR(256),
    User2 VARCHAR(256),
    logs TEXT,
    PRIMARY KEY (User1, User2),
    FOREIGN KEY (User1) REFERENCES [User](id),
    FOREIGN KEY (User2) REFERENCES [User](id)
);
