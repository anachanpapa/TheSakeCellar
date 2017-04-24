from gluon.tools import *

"""
#db = DAL(settings.db_uri)
db = DAL('sqlite://storage.sqlite')
if settings.db_uri.startswith('gae'):
	session.connect(request, response, db = db)
"""


if not request.env.web2py_runtime_gae:     
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')
    #db4ajax = DAL('sqlite://db.db')  
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore') 
    ## store sessions and tickets there
    session.connect(request, response, db = db) 
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

	
mail = Mail() # mailer
auth = Auth(db) # authentication/authorization

auth.settings.actions_disabled.append('register')

db.define_table( 
    auth.settings.table_user_name, 
    Field('first_name', length=128, default=''), 
    Field('last_name', length=128, default=''), 
    Field('email', length=128, default='', unique=True), 
	Field('company_name', length=128, default=''),
	Field('company_homepage', length=128, default=''),	
	Field('office_address', length=128, default=''),
	Field('postcode', length=128),
	Field('phone_number', requires=IS_MATCH('[\d\-\(\) ]+')),
	Field('title', length=128, default=''),
    Field('password', 'password', length=512, readable=False, label='Password'), 
    Field('registration_key', length=512, writable=False, readable=False, default=''), 
    Field('reset_password_key', length=512, writable=False, readable=False, default=''), 
    Field('registration_id', length=512, writable=False, readable=False, default=''), 
    format='%(first_name)s %(last_name)s')

	
db.auth_user.email.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Email')
db.auth_user.first_name.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='First Name')
db.auth_user.last_name.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Last Name')
db.auth_user.password.widget = lambda f,v: SQLFORM.widgets.password.widget(f, v, _placeholder='Password')
#db.auth_user.password_two.widget = lambda f,v: SQLFORM.widgets.password.widget(f, v, _placeholder='Password')
db.auth_user.company_name.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Company Name')
#db.auth_user.company_category.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Company Category')
db.auth_user.company_homepage.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Homepage(optional): e.g. http://yourcompany.com')
db.auth_user.phone_number.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Phone Number')
db.auth_user.office_address.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Office Address')
db.auth_user.postcode.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Postcode')
db.auth_user.title.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Job Title')

member = db[auth.settings.table_user_name] # get the custom_auth_table 
member.first_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty) 
member.last_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)

member.company_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty) 
member.phone_number.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty) 
member.office_address.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
member.postcode.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty) 
member.postcode.requires = [IS_MATCH('^[a-zA-Z0-9_\- ]{5,8}$',error_message='wrong postcode')]
member.title.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty) 

member.password.requires = [IS_MATCH('^[a-zA-Z0-9_!@\#$%\ˆ\&\(\)\{\}\[\]\-\+]{6,20}$',error_message='length: from 6 to 20'),IS_MATCH('[A-Z]+','need more than 1 upper case characters '), CRYPT()]
#member.password.requires = [IS_STRONG(min=5, special=0, upper=0), CRYPT()]
member.email.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty) 
member.email.requires = [IS_EMAIL(error_message=auth.messages.invalid_email), IS_NOT_IN_DB(db, 'auth_user.email')]


crud = Crud(db) # for CRUD helpers using auth
service = Service() # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

# enable generic views for all actions for testing purpose
response.generic_patterns = ['*']

mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login
auth.settings.hmac_key = settings.security_key

# add any extra fields you may want to add to auth_user
auth.settings.extra_fields['auth_user'] = []

# user username as well as email
auth.define_tables(migrate=settings.migrate,username=True)
auth.settings.mailer = mail
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False


## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'

#mail.settings.server = 'gae'
mail.settings.sender = 'THE SAKE CELLAR <service@thesakecellar.com>'
mail.settings.login = 'service@thesakecellar.com:Amychanpapa'

#mail.settings.login = 'hiroshi.s@thesakecellar.com:Johnpapa'
#mail.settings.server = 'smtp.thesakecellar.com:465' does not work!
#mail.settings.sender = 'anachanpapa@gmail.com'
#mail.settings.login = 'anachanpapa@gmail.com:LordJesusChrist'
#mail.settings.login = 'username:password'

# login session expiration time
auth.settings.expiration = 3600 # seconds
auth.settings.remember_me_form = False

# post login redirection
auth.settings.login_next = URL(r=request, c='default', f='post_login')

# post logout redirection
auth.settings.logout_next = URL(r=request, c='default', f='index')


auth.messages.verify_email = 'Click on the link http://' \
	+ request.env.http_host + URL('default','user',
	args=['verify_email']) \
	+ '/%(key)s to verify your email'
	
auth.settings.reset_password_requires_verification = True

"""
auth.messages.reset_password = 'Click on the link http://' \
	+ request.env.http_host + URL('default','user',
	args=['reset_password']) \
	+ '/%(key)s to reset your password'
"""

auth.messages.reset_password = 'Click on the link http://' + request.env.http_host + URL(r=request,c='default',f='user',args=['reset_password']) + '?key=%(key)s to reset your password'	
	
if settings.login_method=='janrain':
	from gluon.contrib.login_methods.rpx_account import RPXAccount
	auth.settings.actions_disabled=['register', 'change_password', 'request_reset_password']
	auth.settings.login_form = RPXAccount(request,
		api_key = settings.login_config.split(':')[-1],
		domain = settings.login_config.split(':')[0],
		url = "http://%s/%s/default/user/login" % \
		(request.env.http_host, request.application))


first_login = 0
