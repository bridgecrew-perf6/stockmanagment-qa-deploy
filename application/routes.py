from crypt import methods
import datetime
from datetime import date,datetime,timedelta
from itertools import product
import json
from random import sample
import flask_login
from flask_login import LoginManager,login_user, login_required, logout_user, current_user
import flask
from flask import render_template,url_for,request, flash, redirect, session, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc,asc,and_,or_, func
from application.models import Order, User, Customer, UnavailableItems, Product, Role, OrderItems
from application import app, db

# The login manager contains the code that lets your application and Flask-Login work together,
# such as how to load a user from an ID, where to send users when they need to log in, and the like.

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def before_request():
    g.user = current_user
    
def get_current_user_role():
    return g.user.role

# -----------------------------------------------------------------------------------------------------------
# Roles routes

@app.route("/allroles")
# @login_required
def allRoles():
    """ All system users """
    roles = Role.query.filter_by(status = True).all()
    return render_template("allroles.html", roles = roles) 

# Admin add user
@app.route("/addrole", methods=['POST'])
# @login_required
def addRole():
    """ Add new system role function """
    if request.method == 'POST':
        NewRole = Role(name = request.form['roleName'],description = request.form['description'])
        db.session.add(NewRole)
        try:
            db.session.commit()
            flash(f' {NewRole.name} Successfully Added!', 'success')
            return jsonify('success')
        except IntegrityError:
            db.session.rollback()
            flash(f'That Role already exists !','danger')
            return jsonify('success')

# -----------------------------------------------------------------------------------------------------
# allUsers route
@app.route("/allusers")
# @login_required
def allUsers():
    """ All system users """
    users = User.query.filter_by(status = True).all()
    return render_template("allusers.html", users = users)
    # if g.user.role.name == 'Admin':
    #     users = db.session.query(User).filter(~User.user_role_id.in_([1])).all()
    #     return render_template("allusers.html", users = users)
    # elif  g.user.role.name == 'SuperUser':
    #     users = User.query.filter_by(status = True).all()
    #     return render_template("allusers.html", users = users)
    # else:
    #     return render_template("allusers.html")

@app.route("/viewroles", methods=["POST"])
# @login_required
def viewAllRoles():
    """ Get all system roles"""
    if request.method == 'POST':
        # data = Role.query.filter(~id.in_([1])).all()
        data = db.session.query(Role).filter(~Role.id.in_([1])).all()
        rolesDataArray = []
        for role in data:
            if role.name != 'SuperAdmin' :
                roleobj = {}
                roleobj['id'] = role.id
                roleobj['name'] = role.name
                rolesDataArray.append(roleobj)
        return json.dumps(rolesDataArray)

@app.route("/adduser", methods=['POST'])
# @login_required
def add_user():
    """ Add system users route """
    if request.method == 'POST':
        hashed_password= generate_password_hash(request.form['password'], method='sha256')
        newuser = User(username = request.form['username'] ,email = request.form['useremail'], password = hashed_password,\
            user_role_id = int(request.form['role']))
        db.session.add(newuser)
        try:
            db.session.commit()
            flash(f' {newuser.username} Successfully Added!', 'success')
            return jsonify('success')
        except IntegrityError:
            db.session.rollback()
            flash(f'This User already exists','danger')
            return jsonify('success')

@app.route("/viewuser", methods=['POST'] )
# @login_required
def viewUser():
    if request.method == 'POST':
        user = User.query.filter_by(id = request.form['user_id']).first()
        userDataArray = []
        userobj = {}
        userobj['id'] = user.id
        userobj['username'] = user.username
        userobj['email'] = user.email
        userobj['role_id'] =  user.user_role_id
        userobj['role'] = user.role.name
        userDataArray.append(userobj)
        return json.dumps(userDataArray)

@app.route('/edituser', methods = ['POST'])
# @login_required
def editUser():
    if request.method == 'POST':
        userToEdit = User.query.filter_by(id = request.form['user_id']).first()
        if userToEdit.username:
            userToEdit.username = request.form['username'].title()
        if userToEdit.email:
            userToEdit.email = request.form['email']
        if userToEdit.password:
            hashed_password= generate_password_hash(request.form['password'], method='sha256')
            userToEdit.password = hashed_password
        if userToEdit.user_role_id:
            userToEdit.user_role_id = request.form['role_id']
        db.session.add(userToEdit)
        db.session.commit() 
        flash(f'{userToEdit.username}  has been updated!', 'success')
        return jsonify('success')
    
# delete_service route
@app.route('/deleteuser', methods = ['POST'])
@login_required
def deleteUser():
    if request.method == 'POST':
        userToDelete = User.query.filter_by(id = request.form['user_id']).first()
        userToDelete.status = False
        db.session.add(userToDelete)
        db.session.commit() 
        flash(f'{userToDelete.username}  has been deleted!', 'danger')
        return jsonify('success') 
    
# ----------------------------------------------------------------------------------------------------------------
#Login route
@app.route("/")
@app.route('/login' , methods = ['GET','POST'])
def login():
    """ Login route """
    if request.method == 'POST':
        user=User.query.filter_by(username = request.form['username']).first()
        if user:
            if check_password_hash(user.password, request.form['password']):
                login_user(user, remember = True)
                return redirect(url_for('Billing'))
        flash('Incorrect Username or password','danger')
        return redirect(url_for('login'))
    return render_template('login.html')  

# ----------------------------------------------------------------------------------------------------------------
# Billing route
@app.route("/billing")
@login_required
def Billing():
    """ billing route """
    customers = Customer.query.filter_by(status = True).all()
    products = Product.query.filter_by(status = True).all()
    return render_template("billingpage.html", customers = customers, products = products) 

@app.route("/productsdetails", methods = ['POST'])
@login_required
def ProductDetails():
    """ get products details """
    if request.method == 'POST':
        product = Product.query.filter_by(id = request.form['productId']).first()
        productArray = []
        productDict = {}
        productDict['id'] = product.id
        productDict['product_name'] = product.product_name
        productDict['current_qty'] = product.quantity
        productDict['selling_price'] = product.sell_price
        productArray.append(productDict)
        return json.dumps(productArray)
        
@app.route("/addbillitems", methods=['POST'] )
@login_required
def AddBillItems():
    """ save bill items """
    if request.method == 'POST':
        customerDetails = json.loads(request.form['customerDetails'])
        billItems = json.loads(request.form['ArrayItem'])
        customerId = Customer.query.filter_by(id = int(customerDetails[0]['CustomerId'])).first()
        newOrder = Order(inserted_by = current_user.username,\
            bill_date=datetime.strptime(customerDetails[0]['PurchaseDate'], "%Y-%m-%d").date(),\
            payment_type = customerDetails[0]['PaymentType'],payment_amount = customerDetails[0]['PaidAmount'],\
                sub_total = customerDetails[0]['Subtotal'],customer_id = customerId.id )
        for orderitem in billItems:
            product_to_sell = Product.query.filter_by(id = int(orderitem['ProductId'])).first()
            if product_to_sell.product_type == 'Product':
                product_to_sell.quantity -= int(orderitem['ProductQty'])
                newOrderline = OrderItems(product_id = product_to_sell.id , quantity = int(orderitem['ProductQty']),\
                    sell_price = int(orderitem['ProductCost']), total_amount = int(orderitem['ProductTotalAmount']),\
                        order = newOrder)
                # add to session
                db.session.add(newOrder)
                db.session.add(newOrderline)
                db.session.add(product_to_sell)
                # commit to db
                db.session.commit()
                db.session.commit()
                db.session.commit()
            else:
                newOrderline = OrderItems(product_id = product_to_sell.id , quantity = int(orderitem['ProductQty']),\
                    sell_price = int(orderitem['ProductCost']), total_amount = int(orderitem['ProductTotalAmount']),\
                        order = newOrder)
                # add to session
                db.session.add(newOrder)
                db.session.add(newOrderline)
                db.session.add(product_to_sell)
                # commit to db
                db.session.commit()
                db.session.commit()
                db.session.commit()
        
        flash(f'Bill successfully added !', 'success')
        return jsonify('success')

# -----------------------------------------------------------------------------------------------------------------
# allProducts route
@app.route("/allproducts")
@login_required
def allProducts():
    """ All Products """
    products = services = Product.query.filter(and_(Product.status == True,Product.product_type == 'Product')).all()
    return render_template("all_products.html", products = products) 

# addnewitem endpoint
@app.route("/addnewproduct", methods=['POST'] )
@login_required
def addProduct():
    if request.method == 'POST':
        # check if the product already exists
        productToAdd = Product.query.filter(Product.product_name == request.form.get('product_name').title()).first()
        # if exists just activate the record
        if productToAdd:
            if productToAdd.status == True:
                flash(f'This Product already exists, use the search field to find it.','danger')
                return jsonify('success')
            else:
                productToAdd.status = True
                productToAdd.product_name = request.form.get('product_name').title()
                productToAdd.product_type = request.form.get('product_type').title()
                productToAdd.buy_price = request.form.get('buying_price')
                productToAdd.sell_price = request.form.get('selling_price')
                productToAdd.quantity = request.form.get('current_quantity')
                productToAdd.reorder_level = request.form.get('reorder_level')
                productToAdd.inserted_by = current_user.username
                db.session.add(productToAdd)
                db.session.commit() 
                flash(f'{productToAdd.product_name} has been added (activated) !', 'success')
                return jsonify('success')
        # if its a new product , add that record to db.
        elif request.form.get('product_type').title() == 'Service':
            newProduct = Product(product_name = request.form.get('product_name').title(),product_type = request.form.get('product_type').title(),sell_price = request.form.get('selling_price'),inserted_by = current_user.username)
            db.session.add(newProduct)
          
            try:
                db.session.commit()
                flash(f' {newProduct.product_name} Successfully Added (new)!', 'success')
                return jsonify('success')
            except IntegrityError:
                db.session.rollback()
                flash(f'Something wrong, try again','danger')
                return jsonify('success')
        else:
            newProduct = Product(product_name = request.form.get('product_name').title(),buy_price = request.form.get('buying_price'),\
                product_type = request.form.get('product_type').title(),sell_price = request.form.get('selling_price'),quantity = request.form.get('current_quantity'),\
                    reorder_level = request.form.get('reorder_level'),inserted_by = current_user.username)
            db.session.add(newProduct)
           
            try:
                db.session.commit()
                flash(f' {newProduct.product_name} Successfully Added (new)!', 'success')
                return jsonify('success')
            except IntegrityError:
                db.session.rollback()
                flash(f'Something wrong, try again','danger')
                return jsonify('success')

# viewProduct endpoint 
@app.route("/viewproduct", methods=['POST'] )
@login_required
def viewProduct():
    if request.method == 'POST':
        product = Product.query.filter_by(id = request.form['product_id']).first()
        productDataArray = []
        productobj = {}
        productobj['id'] = product.id
        productobj['product_name'] = product.product_name
        productobj['buy_price'] = product.buy_price
        productobj['sell_price'] = product.sell_price
        productobj['quantity'] = product.quantity
        productobj['reorder_level'] = product.reorder_level
        productDataArray.append(productobj)
        return json.dumps(productDataArray)

# Editproduct endpoint
@app.route('/editproduct', methods = ['POST'])
@login_required
def editProduct():
    if request.method == 'POST':
        productToEdit = Product.query.filter_by(id = request.form['product_id']).first()
        if productToEdit.product_name:
            productToEdit.product_name = request.form['product_name'].title()
        if productToEdit.buy_price:
            productToEdit.buy_price = request.form['buying_price']
        if productToEdit.sell_price:
            productToEdit.sell_price = request.form['selling_price']
        if productToEdit.quantity:
            productToEdit.quantity = request.form['current_quantity']
        else:
            productToEdit.quantity = request.form['current_quantity']
        if productToEdit.reorder_level:
            productToEdit.reorder_level = request.form['reorder_level']
        db.session.add(productToEdit)
        db.session.commit() 
        flash(f'{productToEdit.product_name}  has been updated!', 'success')
        return jsonify('success')
    
# delete_service route
@app.route('/deleteproduct', methods = ['POST'])
@login_required
def deleteProduct():
    if request.method == 'POST':
        productToDelete = Product.query.filter_by(id = request.form['product_id']).first()
        productToDelete.status = False
        db.session.add(productToDelete)
        db.session.commit() 
        flash(f'{productToDelete.product_name}  has been deleted!', 'danger')
        return jsonify('success') 
# --------------------------------------------------------------------------------------------------------
# allServices route
@app.route("/allservices")
@login_required
def allServices():
    """ All Services """
    services = Product.query.filter(and_(Product.status == True,Product.product_type == 'Service')).all()
    return render_template("all_services.html", services = services) 

# viewService endpoint 
@app.route("/viewservice", methods=['GET','POST'] )
@login_required
def viewService():
    if request.method == 'POST':
        service_id = request.form['service_id']
        data = Product.query.filter_by(id = service_id).all()
        serviceDataArray = []
        for service in data:
            serviceobj = {}
            serviceobj['id'] = service.id
            serviceobj['name'] = service.product_name
            serviceobj['price'] = service.sell_price
            serviceDataArray.append(serviceobj)
        return json.dumps(serviceDataArray)

# EditService endpoint
@app.route('/editservice', methods = ['POST'])
@login_required
def editService():
    if request.method == 'POST':
        service_id = request.form['service_id']
        service_name = request.form['service_name']
        service_price = request.form['service_charge']
        editService = Product.query.filter_by(id=service_id).first()
        
        if editService.product_name:
            editService.product_name = service_name
        else:
            editService.product_name = service_name
        if editService.sell_price:
            editService.sell_price = service_price
        db.session.add(editService)
        db.session.commit() 
        flash(f'{editService.product_name}  has been updated!', 'success')
        return jsonify('success') 
    
# delete_service route
@app.route('/deleteservice', methods = ['POST'])
@login_required
def deleteService():
    if request.method == 'POST':
        service_id = request.form['service_id']
        deleteService = Product.query.filter_by(id = service_id).first()
        deleteService.status = False
        db.session.add(deleteService)
        db.session.commit() 
        flash(f'{deleteService.product_name}  has been deleted!', 'danger')
        return jsonify('success') 
# -----------------------------------------------------------------------------------------------------------------------

# allCustomers route
@app.route("/allcustomers")
@login_required
def allCustomers():
    """ All Customers """
    customers =Customer.query.filter_by(status = True).all()
    return render_template("all_customers.html", customers = customers) 

# addCustomer route 
@app.route("/addcustomer", methods=['POST'] )
@login_required
def addCustomer():
    """ Add Customer """
    if request.method == 'POST':
        # check if the customer already exists
        CustomerToAdd = Customer.query.filter(and_(Customer.name == request.form['name'].title(),\
            Customer.patient_phone == request.form['patient_phone'])).first()
        # if existing just activate the record
        if CustomerToAdd:
            if CustomerToAdd.status == True:
                flash(f'This Customer already exists','danger')
                return redirect(url_for('allCustomers'))
            else:
                CustomerToAdd.status = True
                db.session.add(CustomerToAdd)
                db.session.commit() 
                flash(f'{CustomerToAdd.name} has been added!', 'success')
                return redirect(url_for('allCustomers'))
        # if its a new customer add that record afresh
        else:
            newCustomer = Customer(name = request.form['name'].title(),patient_phone = request.form['patient_phone'])
            db.session.add(newCustomer)
            try:
                db.session.commit()
                flash(f' {newCustomer.name} Successfully Added!', 'success')
                return redirect(url_for('allCustomers'))
            except IntegrityError:
                db.session.rollback()
                flash(f'This Customer already exists','danger')
                return redirect(url_for('allCustomers'))

# viewCustomer endpoint 
@app.route("/viewcustomer", methods=['GET','POST'] )
@login_required
def viewCustomer():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        data = Customer.query.filter_by(id=customer_id).all()
        customerDataArray = []
        for customer in data:
            customerobj = {}
            customerobj['id'] = customer.id
            customerobj['name'] = customer.name
            customerobj['patient_phone'] = customer.patient_phone
            customerDataArray.append(customerobj)
        return json.dumps(customerDataArray)
         
@app.route('/editcustomer', methods = ['POST'])
@login_required
def editCustomer():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        customer_name = request.form['customer_name']
        customer_phone = request.form['customer_phone']
        editCustomer = Customer.query.filter_by(id=customer_id).all()
        
        if editCustomer[0].name:
          editCustomer[0].name = customer_name
        else:
            editCustomer[0].name = customer_name
            
        if editCustomer[0].patient_phone:
            editCustomer[0].patient_phone = customer_phone
        else:
            editCustomer[0].patient_phone = customer_phone
        
        db.session.add(editCustomer[0])
        db.session.commit() 
        flash(f'{customer_name}  has been updated!', 'success')
        return jsonify('success') 
     
# deletecustomer
@app.route('/deletecustomer', methods = ['POST'])
@login_required
def deleteCustomer():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        deleteCustomer = Customer.query.filter_by(id=customer_id).one()
        deleteCustomer.status = False
        db.session.add(deleteCustomer)
        db.session.commit() 
        flash(f'{deleteCustomer.name}  has been deleted!', 'danger')
        return jsonify('success') 
# ------------------------------------------------------------------------------------------    

@app.route("/allunavailableitmes")
@login_required
def UnavailableItmes():
    """ All Unavailable products """
    unavailableItmes = UnavailableItems.query.filter_by(status = True).all()
    return render_template("allunavailableitmes.html", items = unavailableItmes) 

@app.route("/additem", methods=['POST'] )
@login_required
def addItem():
    """ Add Unavailable products """
    if request.method == 'POST':
        ItemToAdd = UnavailableItems.query.filter_by(name = request.form['item_name'].title()).first()
        # if existing just activate the record
        if ItemToAdd:
            if ItemToAdd.status == True:
                flash(f'This Item already exists','warning')
                return jsonify('success')
            else:
                ItemToAdd.status = True
                db.session.add(ItemToAdd)
                db.session.commit() 
                flash(f'{ItemToAdd.name} has been added(reactivated)!', 'success')
                return jsonify('success')
        # if its a new customer add that record afresh
        else:
            newItem = UnavailableItems(name = request.form['item_name'].title(),item_type = request.form['item_type'],\
                description = request.form['item_desc'] )
            db.session.add(newItem)
            try:
                db.session.commit()
                flash(f' {newItem.name} Successfully Added!', 'success')
                return jsonify('success')
            except IntegrityError:
                db.session.rollback()
                flash(f'Something went wrong','danger')
                return jsonify('success')

@app.route("/viewunavailableitem", methods=['POST'] )
@login_required
def ViewItem():
    """ View item details"""
    if request.method == 'POST':
        item_id = request.form['item_id']
        data = UnavailableItems.query.filter_by(id=item_id).all()
        itemDataArray= []
        for item in data:
            itemobj = {}
            itemobj['id'] = item.id
            itemobj['name'] = item.name
            itemDataArray.append(itemobj)
        return json.dumps(itemDataArray)

@app.route("/removeitem", methods=['POST'] )
@login_required
def RemoveItem():
    """ Remove items from Unavailable products list"""
    if request.method == 'POST':
        item_id = request.form['item_id']
        item_to_delete = UnavailableItems.query.filter_by(id=item_id).first()
        item_to_delete.status = False
        db.session.add(item_to_delete)
        db.session.commit() 
        flash(f'{item_to_delete.name}  has been deleted!', 'danger')
        return jsonify('success') 
# ---------------------------------------------------------------------------------
# REPORTS
# Transactions
@app.route("/allorders", methods=['Get','POST'] )
@login_required
def AllOrders():
    """ All orders"""    
    orders = db.session.query(Order, Customer).filter(and_(Order.customer_id == Customer.id,\
        Order.status==True)).all()
    return render_template("allsalesReport.html", orders = orders) 

# view order details with a modal 
@app.route("/viewreceipt", methods=['POST'] )
@login_required
def ViewOrderDetails():
    if request.method == 'POST':
        bill_order = Order.query.filter_by(id = request.form['order_id']).first()
        customer = Customer.query.filter_by(id = bill_order.customer_id).first()
        
        order_items = db.session.query(Product.product_name, Product.product_type,OrderItems.sell_price,\
            OrderItems.total_amount).join(Product.orderitems_id).filter(OrderItems.order_id == bill_order.id ).all()
       
        OrderDataArray = []
        customerDict = {}
        orderLineDict = {}
        # create customer object and add customer details
        customerobj = {}
        customerobj['id'] = customer.id
        customerobj['name'] = customer.name
        customerobj['patient_phone'] = customer.patient_phone
        # add customerobj to customer dictionary
        customerDict['Customer'] = customerobj
        for item in order_items:
            itemobj ={}
            itemobj['name'] = item[0]
            itemobj['type'] = item[1]
            itemobj['sell_price'] = item[2]
            itemobj['orderline_amount'] = item[3]
            orderLineDict[item[0]] = itemobj
        OrderDataArray.append(customerDict)
        OrderDataArray.append(orderLineDict)
        # print(OrderDataArray)
        return json.dumps(OrderDataArray)

# get data for the delete modal
@app.route("/viewbilldetails", methods=['POST'] )
@login_required
def GetbillInfo():
    if request.method == 'POST':
        bill_order = Order.query.filter_by(id = request.form['order_id']).first()
        customer = Customer.query.filter_by(id = bill_order.customer_id).first()
        dataArray = []
        billobj= {}
        customerobj = {}
        customerobj['name'] = customer.name
        billobj['bill_id'] = bill_order.id
        dataArray.append(customerobj)
        dataArray.append(billobj)
        return json.dumps(dataArray)

@app.route('/deletebill', methods = ['POST'])
@login_required
def deleteBill():
    if request.method == 'POST':
        bill_order_to_delete = Order.query.filter_by(id = request.form['order_id']).first()
        if bill_order_to_delete:
            orderline_to_delete = OrderItems.query.filter(OrderItems.order_id == bill_order_to_delete.id ).all()
            for product_sold in orderline_to_delete:
                
                product_to_update = db.session.query(Product).filter(Product.id == product_sold.product_id).first()
                if product_to_update.product_type == 'Product':
                    product_to_update.quantity += product_sold.quantity
                    product_sold.status = False
                    db.session.add(product_to_update)
                    db.session.add(product_sold)
                    db.session.commit() 
                    db.session.commit()
                else:
                    product_sold.status = False
                    db.session.add(product_to_update)
                    db.session.add(product_sold)
                    db.session.commit() 
                    db.session.commit()   
            bill_order_to_delete.status = False
            db.session.add(bill_order_to_delete)
            db.session.commit() 
            flash(f'Transaction has been deleted!', 'warning')
            return jsonify('success')
        else:
            flash(f'Something went wrong!', 'danger')
            return jsonify('success')
        
# Service Charged
@app.route("/servicedchargedreport")
@login_required
def ServiceCharged():
    """ All service charged """
    servicescharged = db.session.query(Product.product_name, Product.product_type,\
        func.sum(OrderItems.quantity), OrderItems.sell_price,func.sum(OrderItems.total_amount)).\
    join(Product.orderitems_id).filter(and_(OrderItems.status == True,Product.product_type == 'Service')).\
        group_by(Product.product_name,Product.product_type,OrderItems.sell_price).order_by(func.sum(OrderItems.total_amount).desc()).all()
    return render_template("servicechargedReport.html", servicescharged = servicescharged) 

# all sold product
@app.route("/productsoldreport")
@login_required
def ProductSold():
    """ All product sold """
    productssold = db.session.query(Product.product_name, Product.product_type,\
        func.sum(OrderItems.quantity), OrderItems.sell_price,func.sum(OrderItems.total_amount)).\
    join(Product.orderitems_id).filter(and_(OrderItems.status == True,Product.product_type == 'Product')).\
        group_by(Product.product_name,Product.product_type,OrderItems.sell_price).all()
    return render_template("allproductsoldReport.html", productssold = productssold) 

@app.route("/reoderlevelreport")
@login_required
def ReorderLevelReport():
    """ report on products below reorder levels """
    products = Product.query.filter(and_(Product.status == True,Product.product_type == 'Product',\
        Product.quantity <= Product.reorder_level)).all()
    return render_template("reoderlevelReport.html", products = products) 

@app.route("/stockreport")
@login_required
def StockReport():
    """ Stock Report"""
    products= Product.query.filter(and_(Product.status == True,Product.product_type == 'Product',\
        Product.quantity > 0)).all()
    return render_template("stockReport.html", products = products)

@app.route('/allsales/billDetails/<int:order_id>/',methods=['GET','POST'])
@login_required
def ReceiptReport(order_id):
    """ Receipt Report"""
    order = Order.query.filter_by(id = order_id).first()
    purchased_items = db.session.query(Product.product_name, Product.product_type, OrderItems.quantity,OrderItems.sell_price,\
            OrderItems.total_amount).join(Product.orderitems_id).filter(OrderItems.order_id == order.id ).all()
    customer_id =order.customer_id
    Customerdetails = Customer.query.filter_by(id=customer_id).first()
    return render_template("viewReceipt.html", purchased_items = purchased_items, order_id = order_id,\
        order = order, Customerdetails = Customerdetails)

# Create custom Error Pages 404 0r 500

#logout
@app.route('/logout')
@login_required
def logout():
    """ Logout route function """
    logout_user()
    return redirect(url_for('login'))
