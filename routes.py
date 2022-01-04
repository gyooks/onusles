import shelve

from flask import redirect, render_template, url_for, flash, request, session, current_app

import Returns
from shop import db, app, photos, bcrypt, login_manager, mail
from .forms import CustomerRegisterForm, CustomerLoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, CreateReturnsForm
from .model import Register
from .model import CustomerOrder
from PIL import Image
import secrets, os
from flask_login import login_required, current_user, logout_user, login_user
import stripe
from flask_mail import Message

publishable_key = 'pk_test_51ICIOSGHGm0ckH0izIMyxTwQVZZmISyThsgRADHkLb9ueH3TxjKOfXXe7012uQnM7pmjT8x5iqbSKpqmeaXTTUnF00fGBfDbtV'

stripe.api_key = 'sk_test_51ICIOSGHGm0ckH0ineoHQvXKE49FCyKH1rJcKBNW59ZyltSDp742kKKg3PBCvfO0DDLNoqMRpwKZrPBmwMu2eXI000X5Ti6GJH'


@app.route('/payment', methods=['POST'])
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        description='onusles',
        amount=amount,
        currency='sgd',
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return render_template('customer/thanks.html')


@app.route('/customer/register', methods=["GET", "POST"])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data,password=hash_password, contact=form.contact.data
                            ,country=form.country.data,state=form.state.data,city=form.city.data,address=form.address.data, zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data}. Thank you for registering!', 'success')
        db.session.commit()
        return redirect(url_for('customerLogin'))
    return render_template('customer/register.html', form=form)

@app.route('/customer/login', methods=["GET", "POST"])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        register = Register.query.filter_by(email=form.email.data).first()
        if register and bcrypt.check_password_hash(register.password, form.password.data):
            login_user(register)
            flash(f"Welcome {register.name}.", 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Login Unsuccessful. Please check email and password', 'danger')
        return redirect(url_for('customerLogin'))

    return render_template('customer/login.html', form=form)

@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))

# removal of unwanted details from shopping cart
#def updateshoppingcart():
    #for _key, product in session['Shoppingcart'].items():
        #session.modified = True
    #return updateshoppingcart

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('customerLogin'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Register.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('customerLogin'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id,orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully', 'success')
            return redirect(url_for('orders', invoice=invoice))

        except Exception as e:
            print(e)
            flash('Something went wrong while getting your order.', 'danger')
            return redirect(url_for('getCart'))


@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subtotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subtotal += float(product['price']) * int(product['quantity'])
            subtotal -= discount
            tax = 10
            grandTotal = subtotal + tax

    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/order.html', invoice=invoice, tax=tax, subtotal=subtotal, grandTotal=grandTotal, customer=customer, orders=orders)

@app.route('/retrieveCustomer')
def retrievecustomers():
    page = request.args.get('page', 1, type=int)
    customer = Register.query.filter(Register.id >= 0).order_by(Register.id).paginate(page=page, per_page=5)
    return render_template('customer/retrieveCustomer.html', customer=customer)

@app.route('/updatecustomer/<int:id>', methods=["GET", "POST"])
def updatecustomer(id):
    customer = Register.query.get_or_404(id)

    form = CustomerRegisterForm(request.form)
    if request.method == "POST":
        customer.name = form.name.data
        customer.username = form.username.data
        customer.country = form.country.data
        customer.contact = form.contact.data
        customer.address = form.address.data


        db.session.commit()
        flash(f'Customer has been updated.', 'success')
        return redirect('/retrieveCustomer')

    form.name.data = customer.name
    form.username.data = customer.username
    form.country.data = customer.country
    form.contact.data = customer.contact
    form.address.data = customer.address

    return render_template("customer/updatecustomer.html", title="Update Customer Page", form=form)

@app.route("/deletecustomer/<int:id>", methods=["POST"])
def deletecustomer(id):
    customer = Register.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(customer)
        db.session.commit()
        flash(f'The product {customer.name} was deleted from your database.', 'success')
        return redirect(url_for('retrievecustomers'))
    flash(f"Can't delete the product", 'danger')
    return redirect(url_for('customers'))

@app.route("/myorders")
def myorders():
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount'] / 100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            tax = 10
            grandTotal = tax + subTotal
    else:
        return redirect(url_for('customerLogin'))
    return render_template('myorders.html', customer=customer, orders=orders, grandTotal=grandTotal, subTotal=subTotal, tax=tax)

@app.route('/retrieveOrders')
def retrieve_orders():
    page = request.args.get('page', 1, type=int)
    order = CustomerOrder.query.filter(CustomerOrder.id >= 0).order_by(CustomerOrder.id).paginate(page=page, per_page=5)
    return render_template('retrieveOrders.html', order=order)

@app.route("/createReturns", methods=['GET', 'POST'])
def create_returns():
    create_returns_form = CreateReturnsForm(request.form)
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
    if request.method == 'POST' and create_returns_form.validate():
        returns_dict = {}
        db = shelve.open('returns.db', 'c')

        try:
            returns_dict = db['Returns']


        except:
            print("Error in retrieving Returns from returns.db.")

        returns = Returns.Returns(create_returns_form.reason.data, create_returns_form.remarks.data)
        returns_dict[returns.get_returns_id()] = returns
        db['Returns'] = returns_dict

        db.close()


        for _key, product in orders.orders.items():
            discount = (product['discount'] / 100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount



        return redirect(url_for('retrieve_returns'))
    return render_template('createReturns.html',form=create_returns_form, orders=orders, grandTotal=grandTotal, subTotal=subTotal)

#Retrieve returns
@app.route('/retrieveReturns')
def retrieve_returns():
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
    returns_dict = {}
    db = shelve.open('returns.db', 'r')
    returns_dict = db['Returns']
    db.close()

    returns_list = []
    for key in returns_dict:
        returns = returns_dict.get(key)
        returns_list.append(returns)

    for _key, product in orders.orders.items():
            discount = (product['discount'] / 100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount


    return render_template('retrieveReturns.html', count=len(returns_list), returns_list=returns_list,  orders=orders, grandTotal=grandTotal, subTotal=subTotal)

#Update Returns
@app.route('/updateReturns/<int:id>/', methods=['GET', 'POST'])
def update_returns(id):
    update_returns_form = CreateReturnsForm(request.form)
    if request.method == 'POST' and update_returns_form.validate():
        users_dict = {}
        db = shelve.open('returns.db', 'w')
        returns_dict = db['Returns']

        returns = returns_dict.get(id)
        returns.set_product(update_returns_form.product.data)
        returns.set_quantity(update_returns_form.quantity.data)
        returns.set_reason(update_returns_form.reason.data)
        returns.set_remarks(update_returns_form.remarks.data)

        db['Returns'] = returns_dict
        db.close()

        return redirect(url_for('retrieve_returns'))
    else:
        db = shelve.open('returns.db', 'r')
        returns_dict = db['Returns']
        db.close()

        returns = returns_dict.get(id)
        update_returns_form.product.data = returns.get_product()
        update_returns_form.quantity.data = returns.get_quantity()
        update_returns_form.reason.data = returns.get_reason()
        update_returns_form.remarks.data = returns.get_remarks()

        return render_template('updateReturns.html', form=update_returns_form)

#delete Return requests
@app.route('/deleteReturns/<int:id>', methods=['POST'])
def delete_returns(id):
    returns_dict = {}
    db = shelve.open('returns.db', 'w')
    returns_dict = db['Returns']

    returns_dict.pop(id)

    db['Returns'] = returns_dict
    db.close()

    return redirect(url_for('retrieve_returns'))



