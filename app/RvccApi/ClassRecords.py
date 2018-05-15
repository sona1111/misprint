from pymongo import MongoClient
from datetime import datetime, timedelta

class ClassRecords(object):

    def __init__(self, host, port, database, collection):
        self.client = MongoClient(host, port)
        self.db = self.client[database]
        self.coll = self.db[collection]

    def insertRecords(self, records, term=None):
        if term:
            print "Existing records for %s will be removed" % term
            self.coll.remove({'term':term}, multi=True)
            records = [dict(x, term=term) for x in records]
        self.coll.insert(records)

    def getClassesNow(self, room=None):
        # find any objects where the room matches, and
        # the current time is after the start time, and the current time is before
        # the end time
        now = datetime.now()
        #now = datetime(2016, 1, 28, 18)
        query = {'start':{'$lte':now}, 'end':{'$gte':now}}

        if room:
            query['room'] = room
        results = self.coll.find(query, {'_id':0})
        return results

    def getClassesBeginning(self, room=None):
        # find any objects where the room matches, and
        # the current time is after the start time, and the current time is before
        # the end time
        now = datetime.now()
        future = now + timedelta(hours=1)

        query = {'start':{'$lte':future, '$gte':now}}

        if room:
            query['room'] = room

        results = self.coll.find(query, {'_id':0})
        return results

    def getAllRoomNames(self):
        results = self.coll.distinct('room')
        return results

    def getClassesRange(self, start, end, room=None):
        # find any objects between the specified start and end dates
        start = datetime.strptime(start, "%Y-%m-%d")
        end = datetime.strptime(end, "%Y-%m-%d")
        # now = datetime(2016, 1, 28, 18)
        query = {'start': {'$gte': start}, 'end': {'$lte': end}}

        if room:
            query['room'] = room
        results = self.coll.find(query, {'_id': 0, 'term':0, 'day':0})
        return results









