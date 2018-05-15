import hmac
import random
import string
import hashlib
import pymongo


# The User Data Access Object handles all interactions with the User collection.
class userDAO(object):

    def __init__(self, db):
        self.db = db
        self.users = self.db.users
        self.SECRET = 'verysecret'

    # makes a little salt
    def make_salt(self):
        salt = ""
        for i in range(5):
            salt = salt + random.choice(string.ascii_letters)
        return salt

    # implement the function make_pw_hash(name, pw) that returns a hashed password
    # of the format:
    # HASH(pw + salt),salt
    # use sha256

    def make_pw_hash(self, pw,salt=None):
        if salt == None:
            salt = self.make_salt();
        return hashlib.sha256(pw + salt).hexdigest()+","+ salt
    
    #make a hash of the user name to use for the registration confirm email
    def make_user_hash(self, user_id, salt=None):        
        return hashlib.sha256(user_id).hexdigest()
    
    #make a hash of the user name slightly different to use for the administrator approval
    def make_user_hash_admin(self, user_id, salt=None):
        if salt == None:
            salt = self.make_salt();
        return hashlib.sha256(user_id).hexdigest()

    # Validates a user login. Returns user record or None
    def validate_login(self, username, password):
               
        user = None
        try:
            user = self.users.find_one({'_id': username.lower()})
        except:
            print "Unable to query database for user"

        if user is None:
            print "User not in database"
            return None

        salt = user['password'].split(',')[1]

        if user['password'] != self.make_pw_hash(password, salt):
            print "user password is not a match"
            return None

        # Looks good
        return user
    
    # levels: {0: reserved, 1:admin, 2:standard user, 3:verified email but not activated, 4:not verified email, 5:banned}
    # creates a new user in the users collection
    def add_user(self, username, password, email, level, additionalInfo={}):
        
        password_hash = self.make_pw_hash(password)        
        userHash = self.make_user_hash(username)
        userHashAdmin = self.make_user_hash_admin(username)

        user = {'_id': username.lower(), 'userHash':userHash, 'userHashAdmin':userHashAdmin, 'password': password_hash, 'email':email, 'level':level, 'clusters':[], 'glasses':[]}
        
        #remove the left over value of user name LATER I NEED TO REMEMBER WHERE THE PASSWORD WAS DONE LIKE THIS AND REMOVE IT THERE
        additionalInfo.pop('userName',None) 
        
        #username and password is all that is required, but we can provide more information optionally
        user.update(additionalInfo)
        
        try:
            self.users.insert(user)
        except pymongo.errors.OperationFailure:
            print "oops, mongo error"
            return 'The mongo driver has failed. Please contact the web-master immediately'
        except pymongo.errors.DuplicateKeyError as e:
            print "oops, username is already taken"
            return 'That username is already taken'

        return user
    
    #update a user's information in the database
    def update_user(self, username, updates={}):
        
        print updates
        
        for update in updates:
            
            if update == 'passwordReg':
                password_hash = self.make_pw_hash(updates['passwordReg'])
                
                self.users.update({'_id':username.lower()},{'$set':{'password':password_hash}})
                
            else:
                self.users.update({'_id':username.lower()},{'$set':{update:updates[update]}})
    
    #generate a new random password for a user and reset it            
    def reset_password(self, username):
        
        password = self.make_salt() + self.make_salt()
        self.update_user(username, {'passwordReg':password})
        return password
        
        

