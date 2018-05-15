from threading import Thread
import time

#this class keeps track of the current users who are logged in
#it adds them through connected signals and removes then through timeouts
#(soon it will also remove them from clean disconnects)
class trackMain(object):
    
    def __init__(self, app):
        self.loggedIn = {}
        self.socket = app
        self.checkTime = 3
        self.timeoutThreshhold = 2
        @app.on('heartbeat')
        def heartbeat(name):
            self.loggedIn[name] = True
    
    
    def addUser(self, user):
        
        Thread(target=self.heartbeat_thread, args=(user,)).start()
        self.loggedIn[user] = True
        
        
    def heartbeat_thread(self, user):
    
        while True:
            #time between checks
            time.sleep(self.checkTime)
            
            self.loggedIn[user] = False
            self.socket.emit('heartbeat')
                            

            #time before timeout after sending signal       
            time.sleep(self.timeoutThreshhold)
            if self.loggedIn[user] == False:
                self.userLeft(user)
                break
                
    def userLeft(self, user):  
        
        del self.loggedIn[user]
        self.socket.emit('left', {'user':user,'users':self.getUsers()})   
        
    def getUsers(self):
        return self.loggedIn.keys()
        
class trackAlt(object):
    
    def __init__(self, io):
        self.loggedIn = []
        self.highPing = []
        self.socket = io
        self.checkTime = 10
        self.timeoutThreshhold = 2
        self.flag = False
        
        @io.on('heartbeat')
        def heartbeat(name):
            
            if self.flag == True:
                if name in self.highPing:
                    
                    self.highPing.remove(name)
                else:
                    print "heartbeat error for user: " + str(name)
        
        
        Thread(target=self.heartbeat_thread).start()
    
    
    def addUser(self, user):
        
        
        self.loggedIn.append(user)
        
        
    def heartbeat_thread(self):
    
        
    
        while True:
            #time between checks
            time.sleep(self.checkTime)
            
            self.highPing[:] = self.loggedIn
            self.flag = True
            
            self.socket.emit('heartbeat')
                            

            #time before timeout after sending signal       
            time.sleep(self.timeoutThreshhold)
            self.flag = False
                        
            for user in self.highPing:
                self.userLeft(user)
                
            
                
    def userLeft(self, user):  
        
        self.loggedIn.remove(user)
        self.socket.emit('left', {'user':user,'users':self.getUsers()})  
        
        
    def getUsers(self):
        return self.loggedIn
        
    
