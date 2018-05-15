from app import app
from functions import get_db
from flask.ext.wtf import Form
from wtforms import TextAreaField, SelectField, StringField, FileField, BooleanField, SelectMultipleField, RadioField, HiddenField, PasswordField, DateField, IntegerField
from wtforms.validators import Optional, DataRequired, regexp, EqualTo, ValidationError, NumberRange
import pymongo
import re


#this one checks first to see if the user entered an email at all
checkIfEmail = re.compile("^[-+.\w]{1,64}@[-.\w]{1,64}\.[-.\w]{2,6}$", re.I)
#this one matches any free email subdomain (without extension)
#checkIfFreeAccount = re.compile("^[-+.\w]{1,64}@("+'|'.join(freeAccountProviders)+").[-.\w]{2,6}$", re.I)
#this one matches any free email subdomain (with extension)


def emailChecker(form, field):
    
    if checkIfEmail.match(field.data) == None:
        raise ValidationError("Please Enter a valid email address")
        
    # else:
    #     if checkIfFreeAccount.match(field.data) == None:
    #         pass
    #     else:
    #         raise ValidationError("A corporate email address is required")


class loginForm(Form):
    
    userName = StringField(validators = [DataRequired()])
    password = PasswordField(validators = [DataRequired()])
    wantsurl = HiddenField()
    
class registerForm(Form):
    
    company = StringField(validators = [Optional()])
    userNameReg = StringField(validators = [DataRequired()])
    firstName = StringField(validators = [DataRequired()])
    lastName = StringField(validators = [DataRequired()])
    email = StringField(validators = [DataRequired(), emailChecker])
    passwordReg = PasswordField(validators = [DataRequired(), EqualTo('passwordConf', message='Passwords must match')])
    passwordConf = PasswordField(validators = [DataRequired()])
    officePhone = StringField(validators = [Optional()])
    mobilePhone = StringField(validators = [Optional()])
    street = StringField(validators = [Optional()])
    city = StringField(validators = [Optional()])
    state = StringField(validators = [Optional()])    
    zip = StringField(validators = [Optional()])
    country = StringField(validators = [Optional()])
    
class profileUpdateForm(Form):
    
    company = StringField(label="Company", validators = [Optional()])    
    firstName = StringField(label="First Name", validators = [DataRequired()])
    lastName = StringField(label="Last Name", validators = [DataRequired()])
    email = StringField(validators = [Optional(), emailChecker])
    passwordReg = PasswordField(label="New Password", validators = [EqualTo('passwordConf', message='Passwords must match')])
    passwordConf = PasswordField(label="Confirm New Password")
    officePhone = StringField(label="Tel (Office)", validators = [Optional()])
    mobilePhone = StringField(label="Tel (Mobile)", validators = [Optional()])
    street = StringField(label="Street Name", validators = [Optional()])
    city = StringField(label="City", validators = [Optional()])
    state = StringField(label="State", validators = [Optional()])    
    zip = StringField(label="Zip Code", validators = [Optional()])
    country = StringField(label="Country", validators = [Optional()])
    oldPassword = PasswordField(validators = [DataRequired()])
    
    def __init__(self, userInfo = {}, *args, **kwargs):
        super(profileUpdateForm, self).__init__(*args, **kwargs)
        
        #this will prepopulate all of the fields
        for update in userInfo:
            getattr(self, update).data = userInfo[update]
        

class forgotPasswordForm(Form):
    
    userName = StringField(validators = [DataRequired()])
    
class forgotUserForm(Form):
    
    email = StringField(validators = [DataRequired(), emailChecker])
    
class orderForm(Form):
    
    product = HiddenField()
    contactPhone = StringField()
    contactTime = StringField(validators = [DataRequired()])
    neededBy = StringField(validators = [DataRequired()])
    comments = TextAreaField()
    
class confirmUserForm(Form):
    pass


class userCreateClusterForm(Form):
    
    name = StringField(label=u'Name', description=u'The name of the cluster (human readable)', validators=[DataRequired()])
    numComputeNodes = IntegerField(label=u'Number of Compute Nodes', description=u'The number of compute nodes to create the cluster', validators=[NumberRange(min=1, max=99, message=u'Please enter a number of computenodes between 1 and 99')])
    size = SelectField(label=u'Node Size', description=u'The size (Performance) of the nodes', choices = [('t1.micro','t1.micro'), ('t2.small','t2.small'), ('m3.medium','m3.medium'), ('m3.large','m3.large')])
    
    #def __init__(self, *args, **kwargs):
    #    super(userCreateClusterForm, self).__init__(*args, **kwargs)
    #    
    #    for sz in ('t1.micro', 't2.small', 'm3.medium', 'm3.large',):
    #        self.size.choices.append((sz, sz,))
         
#         self.numComputeNodes.choices = [(x+1,x+1,) for x in xrange(MAX_COMPUTE_NODES)]

class createClusterForm(Form):
    
    name = StringField(label=u'Name', description=u'The name of the cluster (human readable)')
    type = StringField(label=u'Type', description=u'The type of the cluster (human readable)')
    accounts = SelectField(label=u'AWS account', description=u'The AWS account to use (defined in awsconfig_web.ini)')
    headAMIs = SelectField(label=u'Headnode AMI', description=u'The AMI machine image to use for the headnode')
    computeAMIs = SelectField(label=u'Computenode AMI', description=u'The AMI machine image to use for the computenode')
    numComputeNodes = StringField(label=u'Compute Nodes', description=u'The number of compute nodes to create the cluster')
    users = SelectMultipleField(label='Users', description=u'Users who will be allowed access (on the sonic platform website)')        
    
    def __init__(self, clustersInfo = {}, *args, **kwargs):
        super(createClusterForm, self).__init__(*args, **kwargs)
        
        if 'accounts' in clustersInfo:            
            self.accounts.choices = [(x['account'],x['account'],) for x in clustersInfo['accounts']]
        if 'headAMIs' in clustersInfo:               
            self.headAMIs.choices = [(x['ami'],x['ami'],) for x in clustersInfo['headAMIs']]
        if 'computeAMIs' in clustersInfo:            
            self.computeAMIs.choices = [(x['ami'],x['ami'],) for x in clustersInfo['computeAMIs']]
        if 'users' in clustersInfo:
            self.users.choices = [(x,x,) for x in clustersInfo['users']]
       # self.numComputeNodes.choices = [(x+1,x+1,) for x in xrange(MAX_COMPUTE_NODES)]
    
    
    
    
    
    
    
    
    
    
    
#---------------------------------------------------------------------------
    
    
class quickAddForm(Form):
    items = SelectMultipleField(u'')
    quickAddRemove = BooleanField(label = u'Remove selections')
    
    def __init__(self, quickAddItems, *args, **kwargs):        
        #dont lose this
        super(quickAddForm, self).__init__(*args, **kwargs)
        
        self.items.choices = []
        cur = quickAddItems.find({},{'item':1}).sort([('item',1)])
        for item in cur:
            self.items.choices.append((item['item'],item['item'],))
        
    
    
class stdAddForm(Form):
    person = RadioField(u'', choices = [('Paul','Paul'),('Sara','Sara'),('Mom','Mom'),('Unspecified','Unspecified')], default='Unspecified')
    item = StringField(u'')
    comment = TextAreaField(u'')
    quickAddCheck = BooleanField(label=u'Add this to Quick Items')
    
    
    
    


