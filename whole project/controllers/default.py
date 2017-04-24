# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################


#@auth.requires_login()

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
	
def index():
	products = db(db.product).select(orderby=db.product.product_order)
	return locals()	

def campaignNov2016():
	return locals()

def brightcove():
	return locals()

def post_login():
	if auth.user is None: redirect(URL('login'))
	import datetime	
	#send notification email to service@thesakecellar.com
	name = auth.user.first_name + " " + auth.user.last_name
	company = auth.user.company_name
	now = datetime.datetime.now()
	now = now.strftime("%d/%m/%Y %H:%M")
	admin_email = 'service@thesakecellar.com'
	mail.send(to=[admin_email],
		  subject= "[info] " + name + " has logged in.",
		  # If reply_to is omitted, then mail.settings.sender is used
		  reply_to='service@thesakecellar.com',
		  message= name + " @ " + company + " " + now)
	
	redirect(URL('products'))

	
def products():
	if auth.user is None: redirect(URL('login'))	

	cart = db((db.sales_order.ordered_by == me) & (db.sales_order.order_status == 'in cart')).select(orderby=db.sales_order.order_time).first()
	if cart is None:
		db.sales_order.insert(ordered_by=auth.user, order_status='in cart', payment_method="pay before delivery", postage=0, subtotal=0, total=0)

	products = db(db.product).select(orderby=db.product.product_order)
	return locals()
	
def product_detail():
	if auth.user is None: redirect(URL('login'))	
	cart = db((db.sales_order.ordered_by == me) & (db.sales_order.order_status == 'in cart')).select(orderby=db.sales_order.order_time).first()
	product = db.product(request.args(0)) or redirect(URL('products'))
	return locals()

def add_item():
	order_id = int(request.vars.order_id)
	select_id = int(request.vars.select_item)
	select_item = db.product[select_id]
	item = db((db.sales_item.sales_order == order_id) & (db.sales_item.product == select_item)).select().first()
	
	if item is None:
		db.sales_item.validate_and_insert(
			sales_order=order_id,
			product=select_item,
			sales_price= select_item.price,
			case_quantity=1
		)
		db.commit()
		session.flash = 'An item has been added'
		cart_compute()
		return
	else:
		current_quantity = item.case_quantity
		db((db.sales_item.sales_order == order_id) & (db.sales_item.product == select_item)).update(
			case_quantity=current_quantity + 1
		)
		db.commit()
		session.flash = 'An item has been added'
		cart_compute()		
		return

def drop_item():
	order_id = int(request.vars.order_id)
	select_item = int(request.vars.select_item)
	
	item = db((db.sales_item.sales_order == order_id) & (db.sales_item.product == select_item)).select().first()

	if item.case_quantity == 1:
		db((db.sales_item.sales_order == order_id) & (db.sales_item.product == select_item)).delete()
		db.commit()
		session.flash = 'An item has been dropped'
		cart_compute()
		return
	else:
		db((db.sales_item.sales_order == order_id) & (db.sales_item.product == select_item)).update(
			case_quantity=db.sales_item.case_quantity - 1
		)
		db.commit()
		session.flash = 'An item has been dropped'
		cart_compute()
		return
		
def cart():
	if auth.user is None: redirect(URL('login'))

	cart = db((db.sales_order.ordered_by == me) & (db.sales_order.order_status == 'in cart')).select(orderby=db.sales_order.order_time).first()
	if cart is None:
				db.sales_order.insert(ordered_by=auth.user, order_status='in cart', payment_method="pay before delivery", postage=0, subtotal=0, total=0)
	
	items = db(db.sales_item.sales_order == cart).select()
	
	return locals()
	
	
def cart_compute():	
	if auth.user is None: redirect(URL('login'))

	cart = db((db.sales_order.ordered_by == me) & (db.sales_order.order_status == 'in cart')).select(orderby=db.sales_order.order_time).first()
	items = db(db.sales_item.sales_order == cart).select()

	subtotal = 0;
	for item in items:
		subtotal += item.sales_price * item.case_quantity * 12
	cart.update_record(subtotal=subtotal)
	
	return 

def order_options():
	if auth.user is None: redirect(URL('login'))
	cart = db((db.sales_order.ordered_by == me) & (db.sales_order.order_status == 'in cart')).select(orderby=db.sales_order.order_time).first()
	premises = db(db.premise.purchased_by == me).select(orderby=db.premise.premise_name)
	if cart.total == 0:
		subtotal = cart.subtotal
		cart.update_record(total=subtotal)
	return locals()
		
def checkout():
	if auth.user is None: redirect(URL('login'))
	cart = db((db.sales_order.ordered_by == me) & (db.sales_order.order_status == 'in cart')).select(orderby=db.sales_order.order_time).first()	
	items = db(db.sales_item.sales_order == cart).select()
	return locals()
	
def order_complete():
	import datetime
	if auth.user is None: redirect(URL('login'))
	cart = db((db.sales_order.ordered_by == me) & (db.sales_order.order_status == 'in cart')).select(orderby=db.sales_order.order_time).first()	
	
	now = datetime.datetime.now()
	now_s = now.strftime("%d/%m/%Y %H:%M")
	if cart is not None:
		order_number = now.strftime("%d%m%Y%H%M%S")
	
		if cart.subtotal != 0:
			cart.update_record(order_number=order_number, order_status='order processing', order_time=now, order_time_s=now_s)
			db.commit()

		name = auth.user.first_name
		customer = auth.user.email
		mail.send(to=[customer],
			  subject= "Order confirmation: " + order_number,
			  # If reply_to is omitted, then mail.settings.sender is used
			  reply_to='service@thesakecellar.com',
			  message= "Thank you for your order from The Sake Cellar. ")
			  
			
	latest_order = db(db.sales_order.ordered_by == me).select(orderby=~db.sales_order.order_time).first()
	
	post_payment = 0
	if latest_order.payment_method == "pay after delivery":
		post_payment = 1
	return locals()
	
def history():
	if auth.user is None: redirect(URL('login'))
	orders = db((db.sales_order.ordered_by == me) & (db.sales_order.order_status != 'in cart')).select(orderby=db.sales_order.order_status | ~db.sales_order.order_time)
	return locals()
	
def login(): 
     return dict(form=auth.login())
	 
	 
def about():
	return locals()


def pre_payment():
	order_id = int(request.vars.order_id)
	cart = db((db.sales_order.ordered_by == me) & (db.sales_order.id == order_id)).select().first()
	subtotal = cart.subtotal
	postage = 0.00
	total = subtotal
	cart.update_record(payment_method = "pay before delivery", postage = postage, total = total)
	db.commit()
	return
	
def post_payment():
	order_id = int(request.vars.order_id)
	cart = db((db.sales_order.ordered_by == me) & (db.sales_order.id == order_id)).select().first()
	subtotal = cart.subtotal
	postage = 7.95
	total = subtotal + postage
	cart.update_record(payment_method = "pay after delivery", postage = postage, total = total)	
	db.commit()
	return
	
	
def update_premise():
	premise_id = int(request.vars.premise_id)
	cart = db((db.sales_order.ordered_by == me) & (db.sales_order.order_status == 'in cart')).select(orderby=db.sales_order.order_time).first()
	delivery_premise = db(db.premise.id == premise_id).select().first()
	cart.update_record(delivery_premise = delivery_premise)
	db.commit()
	return
	

@auth.requires_membership('admin')
def admin_top():
	return locals()
	
	
@auth.requires_membership('admin')
def product_create():
	if auth.user is None: redirect(URL('login'))
	form = crud.create(db.product, next='products')
	return locals()

@auth.requires_membership('admin')
def product_edit():
	product = db.product(request.args(0)) or redirect(URL('products'))
	form = crud.update(db.product, product, next='products')
	return locals()


@auth.requires_membership('admin')	
def customers():
	if auth.user is None: redirect(URL('login'))
	customers = db(db.auth_user).select(orderby=db.auth_user.first_name)
	return locals()

@auth.requires_membership('admin')
def customer_create():
	if auth.user is None: redirect(URL('login'))
	form = crud.create(db.auth_user, next='customers')
	return locals()
	
@auth.requires_membership('admin')
def customer_edit():
	customer = db.auth_user(request.args(0)) or redirect(URL('customers'))
	form = SQLFORM(db.auth_user, customer, showid=False, next='products', ignore_rw=True,
	fields=['first_name', 'last_name', 'email', 'company_name', 'company_homepage', 'office_address', 'postcode', 'phone_number', 'title'])
	#form = SQLFORM(db.auth_user, customer, deletable=True)
	if form.process().accepted:
		session.flash = 'form accepted'
		redirect(URL('customers'))
	elif form.errors:
		response.flash = 'form has errors'
	return dict(form=form)

@auth.requires_membership('admin')	
def customer_detail():
	customer = db.auth_user(request.args(0)) or redirect(URL('customers'))
	form = SQLFORM(db.auth_user, customer, showid=False, next='products', readonly=True,
	fields=['first_name', 'last_name', 'email', 'company_name', 'company_homepage', 'office_address', 'postcode', 'phone_number', 'title'])
	#form = SQLFORM(db.auth_user, customer, deletable=True)
	if form.process().accepted:
		session.flash = 'form accepted'
		redirect(URL('customers'))
	elif form.errors:
		response.flash = 'form has errors'
	return locals()

	
@auth.requires_membership('admin')
def categories():
	if auth.user is None: redirect(URL('login'))
	categories = db(db.customer_category).select(orderby=db.customer_category.name)
	return locals()

@auth.requires_membership('admin')
def category_create():
	if auth.user is None: redirect(URL('login'))
	form = crud.create(db.customer_category, next='categories')
	return locals()

@auth.requires_membership('admin')
def category_edit():
	category = db.customer_category(request.args(0)) or redirect(URL('categories'))
	form = crud.update(db.customer_category, category, next='categories')
	return locals()
	

@auth.requires_membership('admin')
def orders():
	if auth.user is None: redirect(URL('login'))
	orders = db(db.sales_order).select(orderby=~db.sales_order.order_time)	
	return locals()

	
@auth.requires_membership('admin')
def order_create():
	if auth.user is None: redirect(URL('login'))
	#form = crud.create(db.sales_order, next='orders')

	import datetime
	now = datetime.datetime.now()
	order_number = now.strftime("%d%m%Y%H%M%S")
	
	form = SQLFORM(db.sales_order)
	if form.validate():
		### deal with uploads explicitly
		form.vars.order_number = order_number
		form.vars.id = db.sales_order.insert(**dict(form.vars))
		response.flash = 'record inserted'
		redirect(URL('orders'))

	return locals()

@auth.requires_membership('admin')
def order_edit():
	order = db.sales_order(request.args(0)) or redirect(URL('orders'))
	form = crud.update(db.sales_order, order, next='orders')
	return locals()

@auth.requires_membership('admin')
def order_detail():
	order = db.sales_order(request.args(0)) or redirect(URL('orders'))
	items = db(db.sales_item.sales_order == order).select()
	return locals()

	
@auth.requires_membership('admin')
def sales_item_create():
	order = db.sales_order(request.args(0)) or redirect(URL('orders'))
	products = db(db.product).select(orderby=db.product.name)
	items = db(db.sales_item.sales_order == order).select()
	return locals()	

	
@auth.requires_membership('admin')	
def premises():
	if auth.user is None: redirect(URL('login'))
	premises = db(db.premise).select(orderby=db.premise.premise_name)
	return locals()
	
@auth.requires_membership('admin')
def premise_create():
	if auth.user is None: redirect(URL('login'))
	form = crud.create(db.premise, next='premises')
	return locals()

@auth.requires_membership('admin')
def premise_edit():
	premise = db.premise(request.args(0)) or redirect(URL('index'))
	form = crud.update(db.premise, premise, next='premises')
	return locals()


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




'''
@auth.requires_membership('admin')
def customer_logs():
	contact = db.contact(request.args(0)) or redirect(URL('companies'))
	db.log.contact.default = contact.id
	db.log.contact.readable = False
	db.log.contact.writable = False
	db.log.posted_on.default = request.now
	db.log.posted_on.readable = False
	db.log.posted_on.writable = False
	form = crud.create(db.log)
	logs = db(db.log.contact==contact.id).select(orderby=db.log.posted_on)
	return locals()
'''	