import mechanize
from lxml import etree
import re
from hostCheck import doesServiceExist
from lxml.etree import tostring
from itertools import chain

class WebAPI_Base(object):

    def __init__(self, ip, **kwargs):

        self.ip = ip
        self.baseURL = "http://%s/cgi-bin/dynamic/printer/PrinterStatus.html" % ip
        self.br = mechanize.Browser()
        #self.br.set_all_readonly(False)    # allow everything to be written to
        self.br.set_handle_robots(False)   # ignore robots
        self.br.set_handle_refresh(False)  # can sometimes hang without this
        #br.addheaders =   	      	# [('User-agent', 'Firefox')]
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])


    def _stringify_children(self, node):

        parts = ([node.text] +
                list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) +
                [node.tail])
        for part in parts:
            print part
        # filter removes possible Nones in texts and tails
        return ''.join(filter(None, parts))

    def _matchTonerPercent(self, tonerPercent):
        match = re.match(r'.* ~(\d{1,3})%', tonerPercent)
        if match:
            tonerPercent = int(match.group(1))
        else:
            match = re.match(r'.* (\d{1,3})', tonerPercent)
            if match:
                tonerPercent = int(match.group(1))
            else:

                tonerPercent = 0
        return tonerPercent

    def getPanelMessage(self):
        panelMessage = self.root.xpath('/html/body/table[1]/tr[3]/td/table/tr[1]/td/font')
        if panelMessage:
            panelMessage = panelMessage[0].text.rstrip(' ')
            panelMessage2 = self.root.xpath('/html/body/table[1]/tr[3]/td/table/tr[2]/td/font')
            if panelMessage2 and panelMessage2[0].text:
                panelMessage += '\n' + panelMessage2[0].text.rstrip(' ')
            return panelMessage
        print "Unable to parse panel message @ %s" % self.baseURL
        return ''

    def getTonerPercent(self):
        tonerPercent = self.root.xpath('/html/body/table[1]/tr[4]/td/b')
        if tonerPercent:

            tonerPercent = self._matchTonerPercent(tonerPercent[0].text)
            if tonerPercent == 0:
                tonerPercent = self.root.xpath('/html/body/table[1]/tr[5]/td')
                if tonerPercent:
                    tonerPercent = int(re.sub("[^0-9]", "", tonerPercent[0].get('width')))
                    return tonerPercent
                else:
                    tonerPercent = 'Error'
                    return tonerPercent
            else:
                return tonerPercent

        print "Unable to parse toner percent @ %s" % self.baseURL
        return ''

    def getTray1(self):
        tray1 = self.root.xpath('/html/body/table[2]/tr[3]/td[2]/table/tr/td/b')
        if tray1:
            tray1 = tray1[0].text
            return tray1
        print "Unable to parse tray1 @ %s" % self.baseURL
        return ''

    def getFeeder(self):
        feeder = self.root.xpath('/html/body/table[2]/tr[4]/td[2]/table/tr/td/b')
        if feeder:
            feeder = feeder[0].text
            return feeder
        print "Unable to parse feeder @ %s" % self.baseURL
        return ''

    def getOutputBin(self):
        outputBin = self.root.xpath('/html/body/table[2]/tr[7]/td[2]/table/tr/td/b')
        if outputBin:
            outputBin = outputBin[0].text
            return outputBin
        outputBin = self.root.xpath('/html/body/table[2]/tr[6]/td[2]/table/tr/td/b')
        if outputBin:
            outputBin = outputBin[0].text
            return outputBin
        print "Unable to parse output bin @ %s" % self.baseURL
        return ''

    def getStatusObj(self):
        hostUP = doesServiceExist(self.ip, 80)
        if not hostUP:
            errstr =  "ip %s does not seem to be available to connect to!" % self.ip
            if hasattr(self, 'name'):
                errstr += "\nFor %s" % self.name
            print errstr
            return {'error':errstr}

        try:
            response = self.br.open(self.baseURL, timeout=10.0)
        except:
            errstr =  "ip %s does not seem to be available to connect to! (http request)" % self.ip
            if hasattr(self, 'name'):
                errstr += "\nFor %s" % self.name
            print errstr
            return {'error':errstr}
        self.root = etree.HTML(response.read())
        parsed = self.parseToStatus()
        return parsed

class WebAPI_B3460(WebAPI_Base):

    def __init__(self, ip, **kwargs):
        super(WebAPI_B3460, self).__init__(ip, **kwargs)

    def parseToStatus(self):

        return {'panelMessage':self.getPanelMessage(),
               'tonerPercent':self.getTonerPercent(),
               'tray1':self.getTray1(),
               'feeder':self.getFeeder(),
               'outputBin':self.getOutputBin()}

class WebAPI_B5460(WebAPI_Base):

    def __init__(self, ip, **kwargs):
        super(WebAPI_B5460, self).__init__(ip, **kwargs)

    def getPanelMessage(self):
        panelMessage = self.root.xpath('/html/body/table[2]/tr[3]/td/table/tr[1]/td/font')
        if panelMessage:
            panelMessage = panelMessage[0].text.rstrip(' ')
            panelMessage2 = self.root.xpath('/html/body/table[2]/tr[3]/td/table/tr[2]/td/font')
            if panelMessage2 and panelMessage2[0].text:
                panelMessage += '\n' + panelMessage2[0].text.rstrip(' ')
            return panelMessage
        print "Unable to parse panel message @ %s" % self.baseURL
        return ''

    def getTonerPercent(self):
        tonerPercent = self.root.xpath('/html/body/table[2]/tr[4]/td/b')


        if tonerPercent:
            tonerPercent = self._matchTonerPercent(tonerPercent[0].text)
            if tonerPercent == 0:
                tonerPercent = self.root.xpath('/html/body/table[2]/tr[5]/td')
                if tonerPercent:
                    tonerPercent = int(re.sub("[^0-9]", "", tonerPercent[0].get('width')))
                    return tonerPercent
                else:
                    tonerPercent = 'Error'
                    return tonerPercent
            else:
                return tonerPercent

        print "Unable to parse toner percent @ %s" % self.baseURL
        return ''

    def getTray1(self):
        tray1 = self.root.xpath('/html/body/table[3]/tr[3]/td[2]/table/tr/td/b')
        if tray1:
            tray1 = tray1[0].text
            return tray1
        print "Unable to parse tray1 @ %s" % self.baseURL
        return ''

    def getTray2(self):
        tray2 = self.root.xpath('/html/body/table[3]/tr[4]/td[2]/table/tr/td/b')
        if tray2:
            tray2 = tray2[0].text
            return tray2
        print "Unable to parse tray2 @ %s" % self.baseURL
        return ''

    def getFeeder(self):
        feeder = self.root.xpath('/html/body/table[3]/tr[4]/td[2]/table/tr/td/b')
        if feeder:
            feeder = feeder[0].text
            return feeder
        print "Unable to parse feeder @ %s" % self.baseURL
        return ''

    def getOutputBin(self):
        outputBin = self.root.xpath('/html/body/table[3]/tr[8]/td[2]/table/tr/td/b')
        if outputBin:
            outputBin = outputBin[0].text
            return outputBin
        outputBin = self.root.xpath('/html/body/table[3]/tr[7]/td[2]/table/tr/td/b')
        if outputBin:
            outputBin = outputBin[0].text
            return outputBin
        print "Unable to parse output bin @ %s" % self.baseURL
        return ''

    def parseToStatus(self):

        return {'panelMessage':self.getPanelMessage(),
               'tonerPercent':self.getTonerPercent(),
               'tray1':self.getTray1(),
               'tray2':self.getTray2(),
               'feeder':self.getFeeder(),
               'outputBin':self.getOutputBin()}

class WebAPI_5110CN(WebAPI_Base):

    def __init__(self, ip, **kwargs):
        super(WebAPI_5110CN, self).__init__(ip, **kwargs)
        self.baseURL = "http://%s/status/status.htm" % ip

    def getPanelMessage(self):
        panelMessage = self.root.xpath('//*[@id="console"]')
        if panelMessage:
            panelMessage = panelMessage[0].text.rstrip(' ')
            # panelMessage2 = self.root.xpath('/html/body/table[2]/tr[3]/td/table/tr[2]/td/font')
            # if panelMessage2 and panelMessage2[0].text:
            #     panelMessage += '\n' + panelMessage2[0].text.rstrip(' ')
            return panelMessage
        print "Unable to parse panel message @ %s" % self.baseURL
        return ''

    def getTonerPercent(self):
        total = 0
        black = self.getBlack()
        if black:
            total += int(black)
        cyan = self.getCyan()
        if cyan:
            total += int(cyan)
        mag = self.getMagenta()
        if mag:
            total += int(mag)
        yel = self.getYellow()
        if yel:
            total += int(yel)
        return total / 4.0

    def getCyan(self):
        cyan = self.root.xpath('/html/body/table[1]/tr/td/form/table[1]/tr/td/table/tr[3]/td[1]/table/tr/td[1]')
        if cyan:
            cyan = int(cyan[0].get('width')) / 2.0
            return cyan
        print "Unable to parse tray1 @ %s" % self.baseURL
        return ''

    def getMagenta(self):
        magenta = self.root.xpath('/html/body/table[1]/tr/td/form/table[1]/tr/td/table/tr[5]/td[1]/table/tr/td[1]')
        if magenta:
            magenta = int(magenta[0].get('width')) / 2.0
            return magenta
        print "Unable to parse tray1 @ %s" % self.baseURL
        return ''

    def getYellow(self):
        yellow = self.root.xpath('/html/body/table[1]/tr/td/form/table[1]/tr/td/table/tr[7]/td[1]/table/tr/td[1]')
        if yellow:
            yellow = int(yellow[0].get('width')) / 2.0
            return yellow
        print "Unable to parse tray1 @ %s" % self.baseURL
        return ''

    def getBlack(self):
        black = self.root.xpath('/html/body/table[1]/tr/td/form/table[1]/tr/td/table/tr[9]/td[1]/table/tr/td[1]')
        if black:
            black = int(black[0].get('width')) / 2.0
            return black
        print "Unable to parse tray1 @ %s" % self.baseURL
        return ''

    # def getWaste(self):
    #     waste = self.root.xpath('/html/body/table/tr/td/form/table[2]/tr/td/table/tr[6]/td[2]/b')
    #     if waste:
    #         waste = waste[0].text
    #         return waste
    #     print "Unable to parse tray1 @ %s" % self.baseURL
    #     return ''

    def getTray1(self):
        tray1 = self.root.xpath('/html/body/table/tr/td/form/table[3]/tr/td/table/tr[3]/td[2]/b')
        if tray1:
            tray1 = tray1[0].text
            if tray1 == "Add Paper":
                tray1 = "Empty"
            return tray1
        print "Unable to parse tray1 @ %s" % self.baseURL
        return ''

    def getTray2(self):
        tray2 = self.root.xpath('/html/body/table/tr/td/form/table[3]/tr/td/table/tr[4]/td[2]/b')
        if tray2:
            tray2 = tray2[0].text
            if tray2 == "Add Paper":
                tray2 = "Empty"
            return tray2
        print "Unable to parse tray2 @ %s" % self.baseURL
        return ''

    # def getFeeder(self):
    #     feeder = self.root.xpath('/html/body/table[3]/tr[4]/td[2]/table/tr/td/b')
    #     if feeder:
    #         feeder = feeder[0].text
    #         return feeder
    #     print "Unable to parse feeder @ %s" % self.baseURL
    #     return ''

    # def getOutputBin(self):
    #     outputBin = self.root.xpath('/html/body/table[3]/tr[8]/td[2]/table/tr/td/b')
    #     if outputBin:
    #         outputBin = outputBin[0].text
    #         return outputBin
    #     print "Unable to parse output bin @ %s" % self.baseURL
    #     return ''

    def parseToStatus(self):


        return {'tonerPercent':self.getTonerPercent(),
               'tray1':self.getTray1(),
               'tray2':self.getTray2()}


    def getStatusObj(self):
        hostUP = doesServiceExist(self.ip, 80)
        if not hostUP:
            errstr =  "ip %s does not seem to be available to connect to!" % self.ip
            if hasattr(self, 'name'):
                errstr += "\nFor %s" % self.name
            print errstr
            return {'error':errstr}
        try:
            response = self.br.open(self.baseURL, timeout=10.0)
        except:
            errstr = "ip %s does not seem to be available to connect to! (http request)" % self.ip
            if hasattr(self, 'name'):
                errstr += "\nFor %s" % self.name
            print errstr
            return {'error': errstr}
        self.root = etree.HTML(response.read())
        parsed = self.parseToStatus()
        self.baseURL = "http://%s/frametop.htm" % self.ip
        response = self.br.open(self.baseURL, timeout=10.0)
        self.root = etree.HTML(response.read())
        parsed['panelMessage'] = self.getPanelMessage()
        return parsed

class WebAPI_HPLJ9050(WebAPI_Base):

    def __init__(self, ip, **kwargs):
        super(WebAPI_HPLJ9050, self).__init__(ip, **kwargs)
        self.baseURL = "http://%s/hp/device/" % ip

    def getPanelMessage(self):
        panelMessage = self.root.xpath('//*[@id="deviceStatusPage"]/div[1]/div[1]')
        if panelMessage:
            panelMessage = panelMessage[0].text.rstrip(' ')
            panelMessage2 = self.root.xpath('//*[@id="deviceStatusPage"]/div[1]/div[2]')
            if panelMessage2 and panelMessage2[0].text:
                panelMessage += '\n' + panelMessage2[0].text.rstrip(' ')
            panelMessage = panelMessage.lstrip('\n').rstrip('\n')
            if panelMessage == 'Sleep Mode on':
                panelMessage = 'Sleep Mode'
            return panelMessage
        print "Unable to parse panel message @ %s" % self.baseURL
        return ''

    def _matchTonerPercent(self, tonerPercent):
        match = re.match(r'.* (\d{1,3})%', tonerPercent)
        if match:
            tonerPercent = int(match.group(1))
        else:
            tonerPercent = 0
        return tonerPercent

    def getTonerPercent(self):
        tonerPercent = self.root.xpath('//*[@id="deviceStatusPage"]/div[2]/table/tr/td[1]/div/span')
        if tonerPercent:
            tonerPercent = str(re.sub(r'[^\x00-\x7F]+',' ', tonerPercent[0].text)).replace('\n', '')
            tonerPercent = self._matchTonerPercent(tonerPercent)
            if tonerPercent == 0:
                tonerPercent = self.root.xpath('/html/body/table[2]/tr[5]/td')
                if tonerPercent:
                    tonerPercent = int(re.sub("[^0-9]", "", tonerPercent[0].get('width')))
                    return tonerPercent
                else:
                    tonerPercent = 'Error'
                    return tonerPercent
            else:
                return tonerPercent

        print "Unable to parse toner percent @ %s" % self.baseURL
        return ''

    def getTray1(self):
        tray1 = self.root.xpath('//*[@id="deviceStatusPage"]/div[3]/table/tr[3]/td[2]/span')
        if tray1:
            tray1 = str(tray1[0].text[2:])
            if tray1 == 'Empty':
                return 'Empty'
            elif tray1 == 'Unknown':
                return 'Empty'
            elif tray1 == '10 - 20%':
                return 'Low'
            else:
                return 'OK'

        print "Unable to parse tray1 @ %s" % self.baseURL
        return ''

    def getTray2(self):
        tray2 = self.root.xpath('//*[@id="deviceStatusPage"]/div[3]/table/tr[4]/td[2]/span')
        if tray2:
            tray2 = str(tray2[0].text[2:])
            if tray2 == 'Empty':
                return 'EMPTY'
            elif tray2 == 'Unknown':
                return 'EMPTY'
            elif tray2 == '10 - 20%':
                return 'Low'
            else:
                return 'OK'
        print "Unable to parse tray2 @ %s" % self.baseURL
        return ''

    def getFeeder(self):
        feeder = self.root.xpath('//*[@id="deviceStatusPage"]/div[3]/table/tr[2]/td[2]/span')
        if feeder:
            feeder = feeder[0].text[2:]
            return feeder
        print "Unable to parse feeder @ %s" % self.baseURL
        return ''

    def getOutputBin(self):
        outputBin = self.root.xpath('//*[@id="deviceStatusPage"]/div[3]/table/tr[5]/td[2]/span')
        if outputBin:
            outputBin = outputBin[0].text[2:]
            return outputBin
        print "Unable to parse output bin @ %s" % self.baseURL
        return ''

    def parseToStatus(self):

        return {'panelMessage':self.getPanelMessage(),
               'tonerPercent':self.getTonerPercent(),
               'tray1':self.getTray1(),
               'tray2':self.getTray2(),
               'feeder':self.getFeeder(),
               'outputBin':self.getOutputBin()}

class WebAPI_5330DN(WebAPI_Base):

    def __init__(self, ip, **kwargs):
        super(WebAPI_5330DN, self).__init__(ip, **kwargs)
        self.baseURL = "http://%s/prn_status.htm" % ip

    def getPanelMessage(self):
        match = re.match(r'.*var lcd_str_1 = "([a-zA-Z0-9 \/]*)";', self.response)
        if match:
            panelMessage = match.group(1)

            if panelMessage == 'Tray 1':
                panelMessage = "READY"
            elif panelMessage == 'Power Save':
                panelMessage = 'Sleep Mode'
            return panelMessage
        print "Unable to parse panel message @ %s" % self.baseURL
        return ''

    def getTonerPercent(self):
        match = re.match(r'.*var black_val = "(\d*)";', self.response)
        if match:
            return int(match.group(1))
        print "Unable to parse toner percent @ %s" % self.baseURL
        return ''

    def getTray1(self):
        match = re.match(r'.*<td>Tray 1<\/td><td>([a-zA-Z ]*)<\/td>', self.response)
        if match:
            tray1 = match.group(1)
            if tray1 == 'Ready':
                tray1 = 'OK'
            return tray1
        print "Unable to parse tray1 @ %s" % self.baseURL
        return ''

    def getTray2(self):
        match = re.match(r'.*<td>Tray 2<\/td>"\);\r\t}\r\tdocument\.write\("\t<td>([a-zA-Z ]*)<\/td>"\);', self.response)
        print match.group(1)
        if match:
            tray2 = match.group(1)
            if tray2 == 'Ready':
                tray2 = 'OK'
            return tray2
        print "Unable to parse tray2 @ %s" % self.baseURL
        return ''

    def getFeeder(self):
        match = re.match(r'.*<\/script>.*<tr><td>MP Feeder<\/td><script LANGUAGE="JavaScript".*type="text\/javascript".*>.*document\.write\("<td>([a-zA-Z ]*)<\/td>"\);', self.response)
        if match:
            return match.group(1)
        print "Unable to parse feeder @ %s" % self.baseURL
        return ''

    def parseToStatus(self):

        return {'tonerPercent':self.getTonerPercent(),
               'tray1':self.getTray1(),
               'tray2':self.getTray2(),
               'feeder':self.getFeeder()}

    def getStatusObj(self):
        hostUP = doesServiceExist(self.ip, 80)
        if not hostUP:
            errstr = "ip %s does not seem to be available to connect to!" % self.ip
            if hasattr(self, 'name'):
                errstr += "\nFor %s" % self.name
            print errstr
            return {'error':errstr}
        try:
            response = self.br.open(self.baseURL, timeout=10.0)
        except:
            errstr = "ip %s does not seem to be available to connect to! (http request)" % self.ip
            if hasattr(self, 'name'):
                errstr += "\nFor %s" % self.name
            print errstr
            return {'error': errstr}
        self.response = response.read()
        self.root = etree.HTML(self.response)

        self.response = self.response.replace('\n', '')

        # '.*var black_val = "(32)";.*<td>Tray 1<\/td><td>(Ready)<\/td>.*document.write\("	<td>Tray 2<\/td>"\);	}	document.write\("	<td>(Ready)<\/td>"\);.*<\/script> <tr><td>MP Feeder<\/td><script LANGUAGE="JavaScript" type="text\/javascript" >	document.write\("<td>(Empty)<\/td>"\);'
        parsed = self.parseToStatus()
        self.baseURL = "http://%s/topbar_op.htm" % self.ip
        response = self.br.open(self.baseURL, timeout=10.0)
        self.response = response.read()
        self.root = etree.HTML(self.response)
        self.response = self.response.replace('\n', '')
        parsed['panelMessage'] = self.getPanelMessage()
        return parsed

if __name__ == "__main__":

    # printers = {'WEST_HELP_DESK':"http://192.168.18.7/cgi-bin/dynamic/printer/PrinterStatus.html"}

    w = WebAPI_5330DN('172.25.32.100')
    print w.getStatusObj()

    # from ghost import Ghost
    # import time
    # ghost = Ghost()
    # with ghost.start() as session:
    #
    #     page, extra_resources = session.open("http://172.25.32.100/topbar_op.htm")
    #     session.wait_for_selector("#panel_display tr td")
    #     print page.content