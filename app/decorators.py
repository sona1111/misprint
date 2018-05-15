from functools import update_wrapper, wraps
from app import app
from flask import render_template, session, url_for, request
import forms

#some tools to simplify the views file a bit

#====================================================DECORATORS====================================================

def requireLoginLevel(level = None):
    def decorator(fn):
        def wrapped_function(*args, **kwargs):
            if 'level' in session:
                #if no argument specified, being logged in is enough
                if level == None:
                    return fn(*args, **kwargs)
                #lower numbers give more power
                elif session['level'] <= level:
                    return fn(*args, **kwargs)
                else:
                    if session['level'] == 2:
                        header = "Unauthorized"
                        body = """<p>Sorry, your access level does not allow you to view this page.</p>"""                        
                        return render_template('completepage.html', header = header, body = body, user = session['user'])
                    elif session['level'] == 3:
                        header = "Account not enabled"
                        body = """<p>The account is not available to be used for advances operations until a staff member from Rudraya activates it</p>"""                        
                        return render_template('completepage.html', header = header, body = body, user = session['user'])
                    elif session['level'] == 4:
                        header = "Email address not yet verified"
                        body = """<p>In order to view this page, please verify your email address by clicking the link in the email which was sent
                        to the email address you registered with. Please click <a href="%s">here</a> if you would like us to send 
                        the verification email again.</p>"""                        
                        return render_template('completepage.html', header = header, body = body % (url_for('resendactivationemail')), user = session['user'])
                    elif session['level'] == 5:
                        header = "Banned"
                        body = """<p>The account you have attempted to log in with has been banned by an administrator</p>"""                        
                        return render_template('completepage.html', header = header, body = body % (url_for('resendactivationemail')), user = session['user'])
                    else:
                        header = "A strange error has occurred"
                        body = """<p>The design of this page blocks content from superadmin users, please contact webmaster.</p>"""                        
                        return render_template('completepage.html', header = header, body = body, user = session['user'])
            else:
                #if not logged in at all, then must log in
                header = "Please log in"
                body = "<p>You must be logged in to view this page, please use the log in panel at the top of the page.</p>"
                loginForm = forms.loginForm()
                #add the current url to the login form for redirection later
                loginForm.wantsurl.data = request.url
                return render_template('completepage.html', header = header, body = body, loginForm = loginForm, wantsurl='privacy')
                
            
        return update_wrapper(wrapped_function, fn)
    return decorator

#creates the login form and any related blocks if required
def includeLogin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'level' in session:
            user = session['user']
            loginForm = None
        else:
            user = False
            loginForm = forms.loginForm()
            loginForm.wantsurl.data = request.url
        return f(user = user, loginForm = loginForm, *args, **kwargs)
    return decorated_function