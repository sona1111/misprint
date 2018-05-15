import ldap
import subprocess


def get_username_and_domain(username):
    domain = 'academic'
    if '\\' in username:
       temp = username.split('\\')
       username = temp[1]
       domain = temp[0]
    return username, domain

def check_credentials(username, password):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure
    # Adapt to your needs
    """
    username, domain = get_username_and_domain(username)
    LDAP_SERVER = 'ldap://raritanval.edu'
    # fully qualified AD user name
    LDAP_USERNAME = '%s\%s' % (domain, username)
    # your password
    LDAP_PASSWORD = password
    try:
       # build a client
       ldap_client = ldap.initialize(LDAP_SERVER)
       # perform a synchronous bind
       ldap.set_option(ldap.OPT_REFERRALS, 0)
       #ldap_client.set_option(ldap.OPT_REFERRALS,0)
       #ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,ldap.OPT_X_TLS_NEVER)
       ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
    except ldap.INVALID_CREDENTIALS:
       ldap_client.unbind()
       print "Incorrect password"
       return False, 0
    except ldap.SERVER_DOWN:
       print "AD server not responding"
       return False, 1
    # all is well


    ldap_client.unbind()
    return True

def get_name_from_username(username):
    username, domain = get_username_and_domain(username)
    cmd = "%s %s\\\\%s | grep Gecos:" % ("/opt/pbis/bin/find-user-by-name",
                                                                     domain,
                                                                     username)
    try:
        userNameRaw = subprocess.check_output(cmd, shell=True)
    except:
        return None
    if userNameRaw:

        userNames = userNameRaw.replace('Gecos:','').replace('\n', '').rstrip(' ').split(',')
        if len(userNames) == 2:
            return userNames[1].lstrip(' ').rstrip(' '), userNames[0].lstrip(' ').rstrip(' ')
    return None

if __name__ == "__main__":
    # print check_credentials('g00228389', 'Aq`1`1`1')
    # print get_name_from_username('g00228389')


    #ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    LDAP_SERVER = 'ldap://192.168.160.112:389'
    # fully qualified AD user name
    ldap.set_option(ldap.OPT_REFERRALS,0)
    ldap_client = ldap.initialize(LDAP_SERVER)

    # build a client

    # perform a synchronous bind
    ldap_client.set_option(ldap.OPT_REFERRALS, 0)
    ldap_client.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    ldap_client.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
    ldap_client.set_option( ldap.OPT_X_TLS_DEMAND, True )
    ldap_client.set_option( ldap.OPT_DEBUG_LEVEL, 255 )

    #ldap_client.set_option(ldap.OPT_REFERRALS,0)
    #ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,ldap.OPT_X_TLS_NEVER)
    ldap_client.simple_bind_s('academic\g00228389', 'Aq`1`1`1')


