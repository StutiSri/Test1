# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

from gluon.contrib.heroku import get_db

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    #db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
    db = get_db(name=None, pool_size=10)
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
#auth.settings.actions_disabled.append('register')
#auth.settings.actions_disabled.append('request_reset_password')
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
db.define_table('tbl_customer',
                Field('customer_phone_number',type='bigint',required='UNIQUE'),
                Field('customer_name',type='string',required='NOTNULL'),
                Field('customer_email_id',type='string',required='UNIQUE'),
                Field('customer_password',type='password',required='NOTNULL'),
                Field('customer_otp','integer'),
                Field('uniquekey', unique=True, compute=lambda r: r.customer_phone_number+r.customer_email_id))
db.define_table('tbl_shops',
                Field('shop_name',type='string',requires=IS_NOT_EMPTY()),#IS_MATCH('^\[a-zA-Z]{1}[a-zA-Z ]+$')),
                Field('shop_address',type='string',requires=IS_NOT_EMPTY()),
                Field('shop_area',type='string',requires=IS_NOT_EMPTY()),#IS_MATCH('[a-zA-Z][a-zA-Z ]+')),
                Field('min_discount',type='double',requires=IS_FLOAT_IN_RANGE(0,100)),
                Field('shop_image',type='upload',uploadfolder='Test1/uploads'))
db.define_table('tbl_shopkeeper',
                Field('shopkeeper_name',type='string',requires=IS_NOT_EMPTY()),#IS_MATCH('[a-zA-Z][a-zA-Z ]+')),
                Field('shopkeeper_email_id',type='string',requires=IS_EMAIL(error_message='Invalid Email!')),
                Field('shopkeeper_phone_number',type='bigint',requires=IS_NOT_EMPTY()),#IS_MATCH('^\[789]\d{9}$')),
                Field('shopkeeper_password',type='password',writable=False,readable=False),
                Field('shopkeeper_otp','integer',writable=False,readable=False),
               Field('uniquekey', unique=True, compute=lambda r: r.shop_id+r.shopkeeper_email_id+r.shopkeeper_phone_number))
db.define_table('tbl_shop_shopkeeper_mapping',
               Field('shopkeeper_id',type='reference tbl_shopkeeper',requires=IS_IN_DB(db,db.tbl_shopkeeper.id)),
               Field('shop_id',type='reference tbl_shops',requires=IS_IN_DB(db,db.tbl_shops.id),writable=False,readable=False))
db.define_table('tbl_categories',
                Field('category_field_name',type='string'),
                Field('category_name',type='string'),
                Field('category_image','upload'))
db.define_table('tbl_shop_category_mapping',
                Field('shop_id',type='reference tbl_shops',requires=IS_IN_DB(db,db.tbl_shops.id)),
                Field('category_id',type='reference tbl_categories',requires=IS_IN_DB(db,db.tbl_categories.id)))
                     #requires=IS_IN_SET(('Clothing','Food Outlets','General Stores','Stationary','Medical')),
               # Field('discount_percent',type='decimal',requires=IS_DECIMAL_IN_RANGE(0,120)))
db.define_table('tbl_account_details',
                Field('shopkeeper_id',type='reference tbl_shopkeeper',requires=IS_IN_DB(db,db.tbl_shopkeeper.id),writable=False,readable=False),
                Field('account_number',type='bigint',requires=IS_NOT_EMPTY()),
                Field('accountee_name',type='string',requires=IS_NOT_EMPTY()),
                Field('account_type',type='string',requires=IS_IN_SET(('Current','Savings'))),
                Field('uses_ifsc',requires=IS_IN_SET(['By IFSC','By Bank']),widget=SQLFORM.widgets.radio.widget),
                Field('ifsc_code',type='string'),
                Field('bank_name',type='string'),
                Field('bank_state',type='string'),
                Field('bank_city',type='string'),
                Field('bank_branch_name',type='string'),
                Field('uniquekey', unique=True, compute=lambda r: r.shopkeeper_id+r.account_number+r.account_type))




## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
