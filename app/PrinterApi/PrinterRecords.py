from pymongo import MongoClient
from datetime import datetime
import json

class PrinterRecords(object):

    def __init__(self, host, port, database, collection):
        self.client = MongoClient(host, port)
        self.db = self.client[database]
        self.coll = self.db[collection]

    def insertOriginalRecords(self):
        with open("printers.json", "r") as f:
            printers = json.load(f)
        for printer in printers:
            if not 'disabled' in printer:
                printer['disabled'] = False
        self.coll.drop()
        self.coll.insert(printers)

    def updateFromStatusObj(self, statusObj):
        oid = statusObj['_id']
        del statusObj['_id']

        self.coll.update({'_id':oid}, statusObj)


    def getAllPrinterModels(self):
        cur = self.coll.find()
        return cur

    def getAllPrinterStatus(self, room=None):
        query = {}
        if room:
            query['room'] = room
        cur = self.coll.find(query, {'_id':0})
        return cur

    def getAllImportant(self):
        cur = self.coll.find({}, {'_id':0})
        important = []
        for printer in cur:
            if 'error' in printer:
                pass
            else:

                if 'panelMessage' in printer and printer['panelMessage'].upper() not in ['SLEEP MODE', 'READY', '']:
                    printer['warnLevel'] = 'high'
                    important.append(printer)
                    continue
                if 'tray1' in printer and 'tray2' in printer:

                    if printer['tray1'].upper() == "EMPTY" and printer['tray2'].upper() == "EMPTY":
                        printer['warnLevel'] = 'high'
                        important.append(printer)
                        continue
                    if (printer['tray2'].upper() == "EMPTY") or \
                       (printer['tray1'].upper() == "EMPTY"):
                        printer['warnLevel'] = 'med'
                        important.append(printer)
                        continue
                    if printer['tray1'].upper() == "LOW" and printer['tray2'].upper() == "LOW":
                        printer['warnLevel'] = 'low'
                        important.append(printer)
                        continue
                elif 'tray1' in printer:
                    if printer['tray1'].upper() == "EMPTY":
                        printer['warnLevel'] = 'high'
                        important.append(printer)
                        continue
                    elif printer['tray1'].upper() == 'LOW':
                        printer['warnLevel'] = 'med'
                        important.append(printer)
                        continue
                if 'tonerPercent' in printer:
                    if printer['tonerPercent'] < 1:
                        printer['warnLevel'] = 'high'
                        important.append(printer)
                        continue
                    if printer['tonerPercent'] < 2:
                        printer['warnLevel'] = 'med'
                        important.append(printer)
                        continue
                    if printer['tonerPercent'] < 3:
                        printer['warnLevel'] = 'low'
                        important.append(printer)
                        continue



        return important

    def getAllRoomNames(self):
        results = self.coll.distinct('room')
        return results