
from lxml import etree
import re
from datetime import datetime, timedelta
import copy

def parseToTimeBlocks(rawhtml):

    root = etree.HTML(rawhtml)

    mainTable = root.xpath('/html/body/div[3]/table[1]')

    allClasses = []
    title = ''
    monthNames = {'Jan':1,
                  'Feb':2,
                  'Mar':3,
                  'Apr':4,
                  'May':5,
                  'Jun':6,
                  'Jul':7,
                  'Aug':8,
                  'Sep':9,
                  'Oct':10,
                  'Nov':11,
                  'Dec':12}

    daysNames = {'M':1,
                 'T':2,
                 'W':3,
                 'R':4,
                 'F':5,
                 'S':6}

    for i, elem in enumerate(mainTable[0][1:]):
        currentClass = {}

        if i % 2 == 0:
            # even numbers have the titles
            anchor = elem.find('th/a')
            title = anchor.text.split('-')[0].rstrip(' ')
            currentClass['title'] = title
        else:

            rows = elem.xpath('td/table/tr')

            # rows = chunks(elem.xpath('td[@class="dddefault"]'), 7)
            for row in rows[1:]:
                cells = row.xpath("td")

                # for our end functionality we want to be able to ask if there is a class
                # going on in the room at a specific time, and when it will end
                # we will store a time block object for each class period, and later we
                # will ask the database to find any objects where the room matches, and
                # the current time is after the start time, and the current time is before
                # the end time

                times = cells[1].text
                days = cells[2].text
                room = cells[3].text
                dates = cells[4].text

                if not times or not days:
                    continue
                if any((not x in daysNames.keys() for x in days)):
                    print "Skipping class %s with unknown day values %s" % (title, days)
                    continue

                # roomMatches = re.match(r".*([A-Z]\d{3}).*", room)
                # room = roomMatches.group(1)
                if room:
                    room = room.split(' ')[-1]
                else:
                    room = "UNKNOWN"

                # for j, cell in enumerate(cells):
                #     if j == 1: # time
                #         time = cell.text
                #     elif j == 2: #days
                #         days = cell.text
                #     elif j == 3: # room
                #         room = cell.text
                #     elif j == 4: # dates
                #         dates = cell.text


                timesMatches = re.match(r"(\d+):(\d{2}) (am|pm) - (\d+):(\d{2}) (am|pm)", times)

                startHours = int(timesMatches.group(1))
                if startHours == 12:
                    if timesMatches.group(3) == "pm":
                        startHours = 12
                    else:
                        startHours = 0
                else:
                    if timesMatches.group(3) == "pm":
                        startHours += 12

                endHours = int(timesMatches.group(4))
                if endHours == 12:
                    if timesMatches.group(6) == "pm":
                        endHours = 12
                    else:
                        endHours = 0
                else:
                    if timesMatches.group(6) == "pm":
                        endHours += 12

                startMinute = int(timesMatches.group(2))
                endMinute = int(timesMatches.group(5))







                datesMatches = re.match(r"(.*) (\d+), (\d{4}) - (.*) (\d+), (\d{4})", dates)
                start = datetime(year=int(datesMatches.group(3)),
                                 month=monthNames[datesMatches.group(1)],
                                 day=int(datesMatches.group(2)))
                end = datetime(year=int(datesMatches.group(6)),
                                 month=monthNames[datesMatches.group(4)],
                                 day=int(datesMatches.group(5)))


                def printBlock(block):
                    print "Bl Start: %s End: %s Day: %s Room: %s" % (str(block['start']),
                                                                     str(block['end']),
                                                                     block['day'],
                                                                     block['room'])

                for day in [daysNames[x] for x in days]:
                    currentDay = copy.deepcopy(start)

                    while currentDay <= end:
                        if currentDay.isoweekday() == day:
                            sl = currentDay.replace(hour=startHours, minute=startMinute)
                            el = currentDay.replace(hour=endHours, minute=endMinute)
                            newBlock = {'room':room, 'title':title}
                            newBlock['start'] = sl
                            newBlock['end'] = el
                            newBlock['day'] = day
                            allClasses.append(newBlock)
                            # printBlock(newBlock)
                            # assert False
                        currentDay = currentDay + timedelta(days=1)


    return allClasses




if __name__ == "__main__":

    with open('htmlout.txt', 'r') as f:
        testHTML = f.read()

    allClasses = parseToTimeBlocks(testHTML)


    # for block in allClasses:
    #     print block
    # etree.tostring(root)