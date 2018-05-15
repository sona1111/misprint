from WebAPI import WebAPI
from ClassRecords import ClassRecords
from ParseHTML import parseToTimeBlocks

URL = "https://ssbprod.raritanval.edu/prod/bwckschd.p_disp_dyn_sched"
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'misprint'
MONGO_CLASSES_COLL = "classes"

def updateTerm(term):
    API = WebAPI(baseURL=URL)
    CR = ClassRecords(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_CLASSES_COLL)

    print "Obtaining courses website. Please wait as this can take a while..."
    rawHTML = API.getAllCoursesHTML(term)
    print "Received positive response of length %d" % len(rawHTML)
    records = parseToTimeBlocks(rawHTML)
    print "Successfully parsed %d records from course list" % len(records)
    CR.insertRecords(records, term=term)
    print "All records inserted successfully"


def getClassRecords():
    try:
        from app import app
        mh = app.config['MONGO_HOST']
        mp = app.config['MONGO_PORT']
        md = app.config['MONGO_DATABASE']
    except:
        mh = MONGO_HOST
        mp = MONGO_PORT
        md = MONGO_DB
    CR = ClassRecords(mh, mp, md, MONGO_CLASSES_COLL)
    return CR



if __name__ == "__main__":


    # CR = ClassRecords(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_CLASSES_COLL)
    # res = CR.getClassesNow('A16')
    # for clas in res:
    #     print clas
    updateTerm("Spring 2016 - Youth")







