db.define_table('product',
	Field('product_order', 'integer', notnull=True, unique=True),
	Field('name', 'string', notnull=True, unique=True),
	Field('catch', 'text'),
	Field('meisho', 'string'),
	Field('abv', requires=IS_MATCH('[\d\.]+')),
	Field('volume', requires=IS_MATCH('[\d\.]+')),	
	Field('brewery', 'string'),
	Field('prefecture', 'string'),
	Field('image', 'upload'),
	Field('rice', 'string'),
	Field('nihonshudo', 'string'),
	Field('seimai_buai', 'string'),
	Field('comment', 'text'),
	Field('price', 'double'),
	Field('stock', 'integer'),
	format='%(name)s')

	
db.define_table('premise',
    Field('first_name', length=128, default=''), 
    Field('last_name', length=128, default=''), 
	Field('purchased_by', 'reference auth_user'),
	Field('premise_name', length=128, default=''),	
	Field('premise_address', length=128, default=''),
	Field('premise_homepage', length=128, default=''),
	Field('postcode', length=128),
	Field('phone_number', requires=IS_MATCH('[\d\-\(\) ]+')),
    format='%(first_name)s %(last_name)s')

	
db.premise.first_name.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='First Name')
db.premise.last_name.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Last Name')
db.premise.premise_name.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Restaurant/Shop Name')
db.premise.premise_homepage.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Homepage(optional): e.g. http://yourcompany.com')
db.premise.premise_address.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Restaurant/Shop  Address')
db.premise.postcode.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Postcode')
db.premise.phone_number.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Phone Number')

db.premise.first_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty) 
db.premise.last_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
db.premise.premise_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty) 
db.premise.premise_address.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
db.premise.postcode.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty) 
db.premise.postcode.requires = [IS_MATCH('^[a-zA-Z0-9_\- ]{5,8}$',error_message='wrong postcode')]
db.premise.phone_number.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty) 

db.define_table('sales_order',
	Field('order_number', requires=IS_MATCH('\d{14}'), readable=False, writable=False), #e.g. 20160425131401
	Field('ordered_by', 'reference auth_user', readable=False, writable=False),
	Field('order_status', 'string', notnull=True, requires = IS_IN_SET(['in cart', 'order processing', 'invoiced', 'dispatched', 'paid', 'accounted'], zero=T('-- choose one --'), error_message='Status must be chosen')), #in cart, order processing, invoiced, dispatched, paid, accounted
	Field('order_time', 'datetime', readable=False, writable=False),
	Field('order_time_s', 'string', readable=False, writable=False),
	Field('dispatch_time', 'string', readable=False, writable=False),
	Field('delivery_premise', 'reference premise', readable=False, writable=False),
	Field('payment_method', 'string', readable=False, writable=False),	
	Field('postage', 'double', readable=False, writable=False),	
	Field('subtotal', 'double', readable=False, writable=False),
	Field('total', 'double', readable=False, writable=False))

db.define_table('sales_item',
	Field('sales_order', 'reference sales_order'),
	Field('product', 'reference product'),
	Field('sales_price', 'double'),
	Field('case_quantity', 'integer'))

	
db.define_table('customer_category',
	Field('name', 'string'),
	Field('off_rate', 'double'))	

	
me = auth.user_id