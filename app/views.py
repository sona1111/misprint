from app import app
from flask import render_template, flash, redirect, jsonify, send_file, request, url_for, g, session, make_response, abort, send_from_directory
import forms
from functions import get_db
import bson
import datetime
import userDAO
from decorators import requireLoginLevel
from bson.objectid import ObjectId
import time
import logging.config

from blueprint_MISPrint import MISPrint_B
import mailing
from ldapAuth import check_credentials, get_name_from_username

logr = logging.getLogger(__name__)

# logr = logging.getLogger('AppsSite.views')


app.register_blueprint(MISPrint_B)

#log.basicConfig(filename='example.log',level=log.DEBUG, format="[%(levelname)s] : %(message)s")
@app.context_processor
def inject_user():

    pageVars = {}
    pageVars['banner'] = 'MISPrint'
    pageVars['navEnabled'] = True

    if 'level' in session:              
        pageVars['user'] = session['user']
        pageVars['fname'] = session['fname']
        pageVars['lname'] = session['lname']
        pageVars['level'] = session['level']
        pageVars['loginForm'] = None
        #db = get_db()
        # userGlasses = db.users.find_one({"_id":user}, {'_id':0,"glasses":1})['glasses']
        # if len(userGlasses) == 0:
        #     glasses = None
        # else:
        #     glasses = db.glasses_available.find({'nickname':{'$in':userGlasses}})
            
    else:
        pageVars['user'] = False
        pageVars['loginForm'] = forms.loginForm()
        pageVars['loginForm'].wantsurl.data = request.url

    return pageVars

#-----------------------------------------------

@app.route('/index', methods = ['GET', 'POST'])
@app.route('/', methods = ['GET', 'POST'])
def index():


    return render_template("home.html") #render_template('home.html')

#=================================================Error Pages====================================================
 
@app.errorhandler(405)
def errpage_405(e):    
    print "==================405, REDIRECTED===================="
    return redirect('/') #temporary solution because I dont know how to get methods from url_for 
 
@app.errorhandler(404)
def errpage_404(e):    
    return render_template('error.html', error = {'type':404,'title':"404"})

@app.errorhandler(403)
def errpage_403(e):    
    return render_template('error.html', error = {'type':403,'title':"403"})

@app.errorhandler(410)
def errpage_410(e):    
    return render_template('error.html', error = {'type':410,'title':"410"})

@app.errorhandler(500)
def errpage_500(e):  
    #tb = traceback.format_exc()
    #mailing.send_error_to_webmaster(tb)    
    return render_template('error.html', error = {'type':500,'title':"500"})

#=========================================Website and User Management================================================

@app.route('/testmail2', methods = ['Get'])
def testmail2():
    mailing.send_create_ticket_email('g00228389', 'Paul', 'Jewell', [{'msg':'test', 'fname':'Paul', 'lname':'Jewell'}])
    return 'ok'

@app.route('/verifylogin', methods = ['POST'])
def verifylogin():
    
    loginForm = forms.loginForm()    
    
    if loginForm.validate_on_submit():
        
        db = get_db()
        userSecurity = userDAO.userDAO(db)
        user = userSecurity.validate_login(loginForm.userName.data.lower(),loginForm.password.data)
        
        if user == None:

            ldap_validated = check_credentials(loginForm.userName.data.lower(),
                                               loginForm.password.data)
            if ldap_validated is True:

                session['level'] = 2
                session['user'] = loginForm.userName.data
                realName = get_name_from_username(loginForm.userName.data)
                if realName:
                    session['fname'] = realName[0]
                    session['lname'] = realName[1]
                else:
                    session['fname'] = loginForm.userName.data
                    session['lname'] = ''
                session['aduser'] = True

            elif ldap_validated[1] == 0:
                header = "Login Error"
                body = """<p>Sorry, this username / password combination was not found in the database</p>
                """
                return render_template("completepage.html", header = header, body = body, loginForm = loginForm)
            else:
                header = "Login Error / Active Directory Error"
                body = """<p>Sorry, this username / password combination was not found in the local database</p>
                <p>Additionally, the active directory server is not responding to our queries, please contact a system administrator or use a local account.</p>"""
                return render_template("completepage.html", header = header, body = body, loginForm = loginForm)
        
        else:
            session['level'] = user['level']
            session['user'] = user['_id']
            session['fname'] = user['firstName']
            session['lname'] = user['lastName']
            session['aduser'] = False
            
        if 'wantsurl' in request.form:
            return redirect(request.form['wantsurl'])
        else:
            return redirect('/')
    
    header = "Login Error"
    body = """<p>Sorry, this username / password combination was not found in the database</p>"""
    return render_template("completepage.html", header = header, body = body, loginForm = loginForm)

#displays the page to request a password reset of a username reminder
@app.route('/forgotlogininfo', methods = ['GET'])
def forgotlogininfo():
    
    forgotPasswordForm = forms.forgotPasswordForm()
    forgotUserForm = forms.forgotUserForm()
    
    return render_template('forgotlogininfo.html', forgotPasswordForm = forgotPasswordForm, forgotUserForm = forgotUserForm)

#actually processes the user name reminder
@app.route('/forgotUserName', methods = ['POST'])
def forgotUserName():
    
    forgotUserForm = forms.forgotUserForm()
    
    if forgotUserForm.validate_on_submit():
        
        db = get_db()
        user = db.users.find_one({'email':forgotUserForm.email.data})
        if (user == None):
            statusMessage = {'heading':'Failure','body':'Sorry, that email address is not registered on our website.'}
            return render_template('forgotlogininfo.html', statusMessage = statusMessage)
        else:
            #mailing.send_forgot_username_mail({'_id':user['_id'],'email':user['email']})
            statusMessage = {'heading':'Success','body':'The user name was sent successfully to your email address.'}
            return render_template('forgotlogininfo.html', statusMessage = statusMessage)
    
    return render_template('forgotlogininfo.html', forgotUserForm = forgotUserForm)

#actually processes the password reset  
@app.route('/forgotPassword', methods = ['POST'])
def forgotPassword():
    
    forgotPasswordForm = forms.forgotPasswordForm()
    
    if forgotPasswordForm.validate_on_submit():
        
        db = get_db()
        user = db.users.find_one({'_id':forgotPasswordForm.userName.data.lower()})
        if (user == None):
            statusMessage = {'heading':'Failure','body':'Sorry, that user name is not registered on our website.'}
            return render_template('forgotlogininfo.html', statusMessage = statusMessage)
        else:
            userSecurity = userDAO.userDAO(db)
            unhashedPassword = userSecurity.reset_password(user['_id'])
            #mailing.send_forgot_password_mail({'_id':user['_id'],'email':user['email'],'password':unhashedPassword})
            statusMessage = {'heading':'Success','body':'The new password was sent successfully to your email address.'}
            return render_template('forgotlogininfo.html', statusMessage = statusMessage)
    
    return render_template('forgotlogininfo.html', forgotPasswordForm = forgotPasswordForm)

#route to display profile updating page
@app.route('/profile', methods = ['GET'])
@requireLoginLevel(4)
def profile():    
    
    db = get_db()
    
    infoToInclude = {'_id':0,'mobilePhone':1,'company':1,'country':1,'street':1,'city':1,'firstName':1,'zip':1,'state':1,'lastName':1,'email':1,'officePhone':1}        
    userInfo = db.users.find_one({'_id':session['user']},infoToInclude)
    
    profileUpdateForm  = forms.profileUpdateForm(userInfo)
    
    return render_template('profile.html', profileUpdateForm = profileUpdateForm, user = session['user'])
    
    
#route to actually update the profile
@app.route('/profileUpdate', methods = ['POST'])
@requireLoginLevel(4)
def profileUpdate():    

    profileUpdateForm  = forms.profileUpdateForm()
    db = get_db()                
    
    if profileUpdateForm.validate_on_submit():
        
        #make sure password is correct again
        userSecurity = userDAO.userDAO(db)
        user = userSecurity.validate_login(session['user'],profileUpdateForm.oldPassword.data)
        if user != None:
            additionalInfo = {}
            for field in profileUpdateForm:
                
                #its ok to do the password update now because update_user checks for it
                if field.name not in ['csrf_token', 'passwordConf', 'oldPassword'] and field.data != '':
                    
                    additionalInfo[field.name] = field.data                   
            
            userSecurity.update_user(session['user'], additionalInfo)
            flash('Information was changed successfully')
            return redirect('/')
        
        else:
            flash('Incorrect Password Entered')                
            return render_template('profile.html', profileUpdateForm = profileUpdateForm)
    
    else: 
        flash('Form is missing required information')                
        return render_template('profile.html', profileUpdateForm = profileUpdateForm)

@app.route('/logout', methods = ['GET'])
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect('/')

#the route which actually process the confirm
@app.route('/activate_user_admin_confirm/<path:user_hash_admin>', methods = ['POST'])
@requireLoginLevel(1)
def activate_user_admin_confirm(user_hash_admin):
    
    db = get_db()
    db.users.update({'userHashAdmin':user_hash_admin}, {'$set':{'level':2}})
    user = db.users.find_one({'userHashAdmin':user_hash_admin},{'firstName':1,'email':1,'_id':0})
    #mailing.send_user_activated_mail(user)
    flash('user has been activated', 'info')
    return redirect('/')

#the route for administrator to allow the user  
@app.route('/activate_user_admin/<path:user_hash_admin>', methods = ['GET'])
@requireLoginLevel(1)
def activate_user_admin(user_hash_admin):
    
    db = get_db()
    confirm = forms.confirmUserForm()
    
    found_user = db.users.find_one({'userHashAdmin':user_hash_admin})
    if not found_user:
        return abort(404)
    else:
        if found_user['level'] not in [3,4]:
            flash('user already activated', 'info')
            return redirect('/')
        else:           
            return render_template('activateconfirm.html', confirm = confirm, user_hash_admin = user_hash_admin, user = found_user['_id'])
            
#the route for the user to confirm their own email
@app.route('/activate_user_client/<path:user_hash>', methods = ['GET'])
def activate_user_client(user_hash, ):
    
    db = get_db()
    
    found_user = db.users.find_one({'userHash':user_hash})  

    if 'level' in found_user:
        #mailing.send_awaiting_confirm_mail_admin(found_user)
        db.users.update({'userHash':user_hash}, {'$set':{'level':2}})
        header = "Success"
        body = "<p>The email address has been verified.</p>"
        session.clear()
        flash("You were logged out automatically")
        return render_template('completepage.html', header=header, body=body)
    else:
        flash('This user already activated', 'info')
        return redirect('/')

@app.route('/testmail', methods = ['GET'])
def testmail():
    mailing.send_test_mail("pjewell@rudraya.com")
    return "ok"


@app.route('/verifyregister', methods = ['POST'])
def verifyregister():
    
    registerForm = forms.registerForm()
    
    if registerForm.validate_on_submit():
    
        db = get_db()
    
        #check that the passwords match (and possibly other checks)
        #TODO all possible server side checks

        if (registerForm.passwordReg.data != registerForm.passwordConf.data):
            flash("Error, passwords do not match")
            return redirect('/register') 
        #check that username does not already exist
        elif (db.users.find({'_id':registerForm.userNameReg.data}).count() != 0):
            flash("Error, user already exists")
            return redirect('/register') 
        else:                       
            #when successful, render the success page and add the user with limited access                    
            userSecurity = userDAO.userDAO(db)
            
            #access level idea: 4 = unverified, 3 = limited, 2 = standard, 1 = administrator, 0 = banned
            #TODO handle a failure
            additionalInfo = {}
            #add all of the other form fields to the database
            for field in registerForm:
                #make sure not to overwrite unsecure values
                if field.name not in ['csrf_token', 'passwordReg','passwordConf','createLinuxUser','userNameReg']:
                    additionalInfo[field.name] = field.data
            
            #hashing the username makes the confirm url extremely difficult to guess (and look long, as expected)
            user = userSecurity.add_user(registerForm.userNameReg.data,registerForm.passwordReg.data, registerForm.email.data, 4, additionalInfo)

                       
            #send the verification email
            mailing.send_awaiting_confirm_mail(user)
            
            return redirect('/registercomplete')
    
    else:
        flash("Form is missing required information, please check below")
        return render_template('register.html', registerForm = registerForm, registerURL=url_for('verifyregister'))
    


#route to create new users
@app.route('/register', methods = ['GET'])

def register():
    
    registerForm = forms.registerForm()
    
    return render_template('register.html', registerForm = registerForm, registerURL=url_for('verifyregister'))


@app.route('/verifyregisterAdmin', methods = ['POST'])
@requireLoginLevel(1)
def verifyregisterAdmin():

    registerForm = forms.registerForm()

    if registerForm.validate_on_submit():

        db = get_db()

        #check that the passwords match (and possibly other checks)
        #TODO all possible server side checks

        if (registerForm.passwordReg.data != registerForm.passwordConf.data):
            flash("Error, passwords do not match", 'danger')
            return redirect('/register')
        #check that username does not already exist
        elif (db.users.find({'_id':registerForm.userNameReg.data}).count() != 0):
            flash("Error, user already exists", 'danger')
            return redirect('/register')
        else:

            #access level idea: 4 = unverified, 3 = limited, 2 = standard, 1 = administrator, 0 = banned
            #TODO handle a failure
            additionalInfo = {}
            #add all of the other form fields to the database
            for field in registerForm:
                #make sure not to overwrite unsecure values
                if field.name not in ['csrf_token', 'passwordReg','passwordConf','createLinuxUser','userNameReg']:
                    additionalInfo[field.name] = field.data




            userSecurity = userDAO.userDAO(db)

            #hashing the username makes the confirm url extremely difficult to guess (and look long, as expected)
            user = userSecurity.add_user(registerForm.userNameReg.data,registerForm.passwordReg.data, registerForm.email.data, 2, additionalInfo)

            header = 'Registration Complete'
            body = 'The account has been added to the database successfully.'
            return render_template('completepage.html', header=header, body=body)

    else:
        flash("Form is missing required information, please check below", 'info')
        return render_template('register.html', registerForm = registerForm, registerURL=url_for('verifyregisterAdmin'))


#route to create new users
@app.route('/registerAdmin', methods = ['GET'])
@requireLoginLevel(1)
def registerAdmin():

    registerForm = forms.registerForm()
    return render_template('register.html', registerForm = registerForm, registerURL=url_for('verifyregisterAdmin'))


@app.route('/resendactivationemail', methods = ['GET', 'POST'])
@requireLoginLevel(4)
def resendactivationemail():
    #make sure the user is not already verified
    if 'level' in session and session['level'] < 4:
        header = "User Already Registered"
        body = "<p>It seems you are already registered, so no need to re-send the email"
        return render_template('completepage.html', header = header, body = body, user = session['user'])
    else:
        db = get_db()
        user = db.users.find_one({'_id':session['user']},{'_id':1,'userHash':1,'email':1})
        #mailing.send_awaiting_confirm_mail({'_id':user['_id'],'email':user['email'], 'userHash':user['userHash']})
        header = "Verification Email Re-sent"
        body = "<p>OK. The verification email was sent to the provided email address again."
        return render_template('completepage.html', header = header, body = body, user = session['user'])

@app.route('/registercomplete', methods = ['GET', 'POST'])
def registercomplete():
    if session.get('level', None):
        return redirect('/')
    return render_template('registercomplete.html')

#====================================================Static Pages====================================================





