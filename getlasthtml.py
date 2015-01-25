#!/usr/bin/python2.7
""" If there's a new HTML file in the Webmaster's training directory,
    get it (if more than one, only get the latest).
    Otherwise, exit with a status of 1. """

import dropbox
state_file = 'token_store.txt'
appinfo_file = 'tokens.txt'


def authorize():
    appinfo = open(appinfo_file,'r')
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
    out = open(state_file, 'w')
    out.write('oauth2:%s\n' % token)
    out.close()
    return token


token = None
delta_cursor = None
try:
    tokinfo = open(state_file, 'r')
    for l in tokinfo.readlines():
        (name, value) = l.strip().split(':')
        if name == 'oauth2':
            token = value
        elif name == 'delta_cursor':
            delta_cursor = value
    tokinfo.close()
except IOError:
    pass
if not token:
    token = authorize()

# If we get here, we are authorized.
client = dropbox.client.DropboxClient(token)

# The only files we care about are in the training directory
path = '/training'

has_more = True
lasthtml = None

while has_more:
    print 'delta_cursor: %s' % delta_cursor
    print 'path: %s' % path
    delta = client.delta(delta_cursor, path)   # See if anything has happened

    # No matter what, we want to write the cursor out to the state file

    tokinfo = open(state_file, 'w')
    tokinfo.write('oauth2:%s\ndelta_cursor:%s\n' % (token, delta['cursor']))
    tokinfo.close()

    # Be ready for 'has_more', unlikely though it is:
    has_more = delta['has_more']
    delta_cursor = delta['cursor']
    print 'has_more:', has_more

    # All we care about is changes to .html or .htm files.  
    print 'we have %d entries', len(delta['entries'])
    for (filename, metadata) in delta['entries']:
        print filename
        print metadata
        print '-------------------'

