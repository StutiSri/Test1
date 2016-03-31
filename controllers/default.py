# -*- coding: utf-8 -*-
#released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    #response.view = 'default/index.json'
    if not session.counter:
        session.counter = 1
    else:
        session.counter += 1
    return dict(message="Test1 welcomes you", counter=session.counter)

def register_shop():
    message=''
    fields = []
    categories = db().select(db.tbl_categories.ALL)
    for category in categories:
        fields.append(Field(category.category_field_name, 'boolean',label=category.category_name,default=category.id))
    form=SQLFORM.factory(db.tbl_shops,*fields)
    if form.process().accepted:
        new_shop_id = db.tbl_shops.insert(**db.tbl_shops._filter_fields(form.vars))
        form.vars.tbl_shop=new_shop_id
        i=0
        categoryCount=0
        categoryCheckboxes=[]
        for field in fields:
            categoryCheckboxes.append(request.vars.get(field.name))
        for category in categoryCheckboxes:
            print(str(category))
            if category:
                #record = db.tbl_categories(id,category_name=fields[i].default)
                db['tbl_shop_category_mapping'].insert(shop_id=new_shop_id,category_id=fields[i].default)
                categoryCount = categoryCount+1
            i = i+1
        if categoryCount>0:
            db.commit()
            message='Shop registered successfully. Your shop id is : '+str(new_shop_id)
        else:
            message = 'Please specify atleast one category for your shop'
    return dict(form=form,message=message)

def register_shopkeeperform():
    message = ''
    fields = getUnmappedShops(True)
    if len(fields)>0:
        hasLinkedShops = False
        form=SQLFORM.factory(db.tbl_shopkeeper,*fields)
        if form.process().accepted:
            for field in fields:
                shop = request.vars.get(field.name)
                if shop:
                    new_shopkeeper_id = db.tbl_shopkeeper.insert(**db.tbl_shopkeeper._filter_fields(form.vars))
                    hasLinkedShops = True
                    break
            if hasLinkedShops:
                print(new_shopkeeper_id)
                form.vars.tbl_shopkeeper=new_shopkeeper_id
                shopCount = linkShops(fields,new_shopkeeper_id)
                session.new_shopkeeper_id = new_shopkeeper_id
                redirect(URL('shopkeeper_account_details'))
            else:
                message = 'Please associate atleast one shop with shopkeeper'
                response.flash = 'Failed'
    else:
        message = 'No unregistered shops left. Kindly register a shop before proceeding'
        form = ''
    return dict(message=message,form=form)

def isNotMapped(shop, shopMappings):
    for shopMapping in shopMappings:
        print('shop id : '+ str(shop.id) + ' shopMapping shop id : ' + str(shopMapping.shop_id))
        if str(shop.id) == str(shopMapping.shop_id):
            return False
    return True

def linkShops(fields,shopkeeper_id):
    i=0
    shopCheckboxes=[]
    for field in fields:
        shopCheckboxes.append(request.vars.get(field.name))
    for shop in shopCheckboxes:
        print(str(shop))
        if shop:
            db['tbl_shop_shopkeeper_mapping'].insert(shop_id=fields[i].default,shopkeeper_id=shopkeeper_id)
        i = i+1
    db.commit();

def getUnmappedShops(asField):
    shops = db().select(db.tbl_shops.ALL)
    shopMappings = db().select(db.tbl_shop_shopkeeper_mapping.ALL)
    fields=[]
    for shop in shops:
        if isNotMapped(shop,shopMappings):
            if asField:
                fields.append(Field(shop.shop_name, 'boolean',label=shop.shop_name,default=shop.id))
            else:
                fields.append(INPUT(_name=shop.shop_name, _type = 'checkbox',_value=shop.id))
                fields.append("  "+shop.shop_name)
    print(str(fields))
    return fields

def shopkeeper_account_details():
    message='Shopkeeper registered successfully. Your shopkeeper id is : '+str(session.new_shopkeeper_id)
    form=SQLFORM.factory(db.tbl_account_details)
    print(str(form.custom.widget['uses_ifsc']))   #to get id
    if form.process().accepted:
        for var in form.vars:
            print(str(var))
        db['tbl_account_details'].insert(**form.vars)
        session.shopkeeper_name = form.vars.accountee_name
        redirect(URL('successful_shopkeeper_registration'))
    return dict(message=message,form=form)

def validation():
    if request.vars.shopkeeper_name:
        session.shopkeeper_name= request.vars.shopkeeper_name
    if request.vars.shopkeeper_email_id:
        session.shopkeeper_email_id= request.vars.shopkeeper_email_id
    if request.vars.shopkeeper_phone_number:
        session.shopkeeper_phone_number= request.vars.shopkeeper_phone_number
    if request.vars.shop_name:
        session.shop_name= request.vars.shop_name
    if request.vars.shop_address:
        session.shop_address= request.vars.shop_address
    if request.vars.shop_area:
        session.shop_area= request.vars.shop_area
    if request.vars.min_discount:
        session.min_discount= request.vars.min_discount
    if request.vars.category_name!="--Select--":
        session.category_name= request.vars.category_name
    if request.vars.account_number:
        session.account_number= request.vars.account_number
    if request.vars.accountee_name:
        session.accountee_name= request.vars.accountee_name
    if request.vars.account_type!="--Select--":
        session.account_type= request.vars.account_type
    if (request.vars.ifsc_code or (request.vars.bank_name and request.vars.bank_city and request.vars.bank_branch_name)):
        if request.vars.ifsc_code:
            session.ifsc_code= request.vars.ifsc_code
        else:
            session.bank_name= request.vars.bank_name
            session.bank_city= request.vars.bank_city
            session.bank_branch_name= request.vars.bank_branch_name
    return true

def successful_shopkeeper_registration():
    return dict()

def link_shop_with_shopkeeper():
    message=''
    fields = getUnmappedShops(False)
    print(str(len(fields)))
    if len(fields)>0:
        print('Shops left')
        hasLinkedShops = False
        fields.append(INPUT(_type='submit'))
        form=FORM('Shopkeeper ID : ',(INPUT(_name='shopkeeper_id',requires=IS_IN_DB(db,db.tbl_shopkeeper.id))),*fields)
        if form.process().accepted:
            for field in fields:
                shop = request.vars.get(field.name)
                if shop:
                    hasLinkedShops = True
                    break
            if hasLinkedShops:
                shopkeeper_id = request.vars.get('shopkeeper_id')
                shopCount = linkShops(fields,shopkeeper_id)
                response.flash = 'Shops linked successfully'
            else:
                message = 'Please associate atleast one shop with shopkeeper'
                response.flash = 'Failed'
    else:
        message = 'No unregistered shops left. Kindly register a shop before proceeding'
        form = ''
    return dict(message=message,form=form)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
