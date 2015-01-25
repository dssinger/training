#!/usr/bin/python2.7
""" If there's a new HTML file in the Webmaster's training directory,
    get it (if more than one, only get the latest).
    Otherwise, exit with a status of 1. """

import dropbox

def authorize():
    appinfo = open('tokens.txt','r')
    for l in appinfo.readlines():
        (name, value) = l.split(':',1)
        name = name.strip().lower()
        value = value.strip()
        if name == 'app key':
            appkey = value
        elif name == 'app secret':
            appsecret = value
    appinfo.close()
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(appkey, appsecret)
    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print '1. Go to: ' + authorize_url
    print '2. Click "Allow" (you might have to log in first)'
    print '3. Copy the authorization code.'
    code = raw_input("Enter the authorization code here: ").strip()
    token, user_id = flow.finish(code)
    out = open('token_store.txt', 'w')
    out.write('oauth2:%s\n' % token)
    out.close()
    return token


token = None
tokinfo = open('token_store.txt', 'r')
for l in tokinfo.readlines():
    (name, value) = l.strip().split(':')
    if name == 'oauth2':
        token = value
tokinfo.close()
if not token:
    token = authorize()

# If we get here, we are authorized.
client = dropbox.client.DropboxClient(token)
print 'linked account: ', client.account_info()
