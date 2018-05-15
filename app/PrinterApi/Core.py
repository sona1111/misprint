from WebAPI import *
from PrinterRecords import PrinterRecords


MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'misprint'
MONGO_PRINTERS_COLL = "printers"

def getPrinterRecords():
    try:
        from app import app
        mh = app.config['MONGO_HOST']
        mp = app.config['MONGO_PORT']
        md = app.config['MONGO_DATABASE']
    except:
        mh = MONGO_HOST
        mp = MONGO_PORT
        md = MONGO_DB
    PR = PrinterRecords(mh, mp, md, MONGO_PRINTERS_COLL)
    return PR



def updateAll():
    PR = getPrinterRecords()


    for printer in PR.getAllPrinterModels():
        if not printer.get('disabled', False):

            if False:
                pass
            elif printer['model'] == 'B3460':
                API = WebAPI_B3460(ip=printer['ip'], name=printer['name'])
            elif printer['model'] == 'B5460':
                API = WebAPI_B5460(ip=printer['ip'], name=printer['name'])
            elif printer['model'] == '5110CN' or printer['model'] == '5130CN':
                API = WebAPI_5110CN(ip=printer['ip'], name=printer['name'])
            elif printer['model'] == 'HPLJ9050':
                API = WebAPI_HPLJ9050(ip=printer['ip'], name=printer['name'])
            elif printer['model'] == '5330DN':
                API = WebAPI_5330DN(ip=printer['ip'], name=printer['name'])
            else:
                API = None

            if API:
                status = API.getStatusObj()

                if 'error' in printer:
                    del printer['error']



                printer.update(status)
                PR.updateFromStatusObj(printer)



if __name__ == "__main__":

    #PR = PrinterRecords(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_PRINTERS_COLL)
    #PR.insertOriginalRecords()
    import urllib2, json

    updateAll()
    #PR = getPrinterRecords()
    #PR.getAllImportant()
    # data = PR.getAllImportant()

    #
    # payload = {'data':data}
    # request = urllib2.Request('http://%s:%d/redirectOutput' % ('localhost', 8000))
    # request.add_header('Content-Type', 'application/json')
    # urllib2.urlopen(request, json.dumps(payload))


    # printers = {'WEST_HELP_DESK':"http://192.168.18.7/cgi-bin/dynamic/printer/PrinterStatus.html"}
    #
    # API = WebAPI_B3460(baseURL=printers['WEST_HELP_DESK'])


