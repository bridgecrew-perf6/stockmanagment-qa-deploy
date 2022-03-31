from datetime import datetime
from email.policy import default
from flask_login import LoginManager, UserMixin
from application import db,app


login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'


# Define models

# role and user have 1:N relationship

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text())
    status = db.Column(db.Boolean(), default= True)
    user = db.relationship('User', backref='role', lazy = True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean(), default= True)
    created_on = db.Column(db.Date(), default=datetime.utcnow)
    use_role_id = db.Column(db.Integer, db.ForeignKey('role.id'),nullable=False)

class Customer(db.Model):  
    """ Customers model """  
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.Date(), default=datetime.utcnow)
    name=db.Column(db.String(), nullable=False)
    patient_phone=db.Column(db.Integer,nullable=True)
    location=db.Column(db.String(), nullable=True)
    debt=db.Column(db.Integer,default=0)
    status = db.Column(db.Boolean(), default= True)
    orders = db.relationship('Order', backref='customer')
    
class UnavailableItems(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    item_type = db.Column(db.String(), nullable= False)
    status = db.Column(db.Boolean(), default= True)
    description = db.Column(db.String(255))

class Product(db.Model):  
    """ Product model """  
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(), unique=True, nullable=False)
    product_type = db.Column(db.String(), nullable= False)
    inserted_by = db.Column(db.String(), nullable=False)
    buy_price = db.Column(db.Integer, default = 0)
    sell_price= db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default = 0 )
    reorder_level = db.Column(db.Integer, default = 0)
    status = db.Column(db.Boolean(), default= True)
    orderitems_id = db.relationship('OrderItems', backref='product')
  
  
class Order(db.Model):  
    """ Orders model """  
    id = db.Column(db.Integer, primary_key=True)
    inserted_on= db.Column(db.DateTime(), default=datetime.utcnow)
    inserted_by=db.Column(db.String(), nullable=False)
    bill_date= db.Column(db.DateTime(), nullable=False)
    payment_type=db.Column(db.String(25),nullable=False)
    sub_total=db.Column(db.Integer, nullable=False)
    payment_amount=db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'))
    status = db.Column(db.Boolean(), default= True)
    orderitems_id = db.relationship('OrderItems', backref='order')
    
class OrderItems(db.Model):  
    """ orderitems model """  
    id = db.Column(db.Integer, primary_key=True)
    quantity=db.Column(db.Integer, nullable=True)
    sell_price=db.Column(db.Integer, nullable=True)
    total_amount=db.Column(db.Integer, nullable=True)
    status = db.Column(db.Boolean(), default= True)
    order_id = db.Column(db.Integer(), db.ForeignKey('order.id')) 
    product_id = db.Column(db.Integer(), db.ForeignKey('product.id'))
    

