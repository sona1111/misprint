import mechanize




class WebAPI(object):

    def __init__(self, baseURL):

        self.baseURL = baseURL
        self.br = mechanize.Browser()
        #self.br.set_all_readonly(False)    # allow everything to be written to
        self.br.set_handle_robots(False)   # ignore robots
        self.br.set_handle_refresh(False)  # can sometimes hang without this
        #br.addheaders =   	      	# [('User-agent', 'Firefox')]



    def selectTerm(self, term):

        self.br.form = list(self.br.forms())[0]
        control = self.br.form.find_control("p_term")
        item_name = None
        for item in control.items:
            if item.get_labels()[0].text == term:
                item_name = item.name
                break
        if not item_name:
            raise KeyError("The requested term %s was not found on the RVCC course selections" % term)
        self.br[control.name] = [item_name]
        self.response = self.br.submit()

    def selectAllCourses(self):



        self.br.form = list(self.br.forms())[0]


        # for item in control.items:
        #     print item.name

        control = self.br.find_control(id='subj_id')
        control.value = [item.name for item in control.items]
        # control = self.br.controls[18]
        # for item in control.items:
        #     print item.name
        control = self.br.find_control(id='camp_id')
        control.value = ["M"]
        # self.br.controls[18] = "M"
        # for item in control.items:
        #     print item
        self.response = self.br.submit()

    def getAllCoursesHTML(self, term):
        self.br.open(self.baseURL)
        self.selectTerm(term)
        self.selectAllCourses()
        return self.response.read()

