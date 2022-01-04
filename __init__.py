from flask import render_template, request, redirect, url_for, session, flash, current_app
import Donate
import Employees
import Returns
from Forms import CreateEmployeesForm, CreateEntryForm, CheckoutForm, ProductForm, TransactionForm, CreateCustomersForm, RegistrationForm, LoginForm, CreateYukinForm, Addproducts, CreateDonationForm, CommentForm
import shelve, Entry, Order, Product, Transaction, Customers, Yukin
from models import User, Addproduct, Category, Comment
from shop import app, db, bcrypt, photos
import secrets, os
import stripe
from flask_login import logout_user, login_user
from functools import wraps

from authlib.integrations.flask_client import OAuth
app.secret_key = 'random secret'

#oauth config
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='777476834753-gj83v7m6s9cqn0of9lgsgcomlpuo7nrb.apps.googleusercontent.com',
    client_secret='EM4KV_D_cezSpvoAMaYSwaNO',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope':'openid profile email'},
)

def to_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        get_fun = func(*args, **kwargs)
        return json.dumps(get_fun)

    return wrapper

@app.route('/')
def home():
    email = dict(session).get('email', None)
    page = request.args.get('page',1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=8)
    return render_template('home.html', products=products, categories=categories())
    return f'Hello, {email}!'

@app.route('/loginGoogle')
def loginGoogle():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    # do something with the token and profile
    session['email']= user_info['email']
    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

def MergeDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

@app.route('/addcart', methods=['POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        product = Addproduct.query.filter_by(id=product_id).first()
        if product_id and quantity and request.method == "POST":
            DictItems = {product_id: {'name': product.name,
                                     'price': float(product.price),
                                     'discount':product.discount,
                                     'quantity':int(quantity),
                                     'image':product.image_1}}

            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            print(item['quantity'])
                            item['quantity'] += 1
                else:
                    session['Shoppingcart'] = MergeDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)

@app.route('/addwishlist', methods=['POST'])
def AddWishlist():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        product = Addproduct.query.filter_by(id=product_id).first()
        if product_id and quantity and request.method == 'POST':
            DictItems = {product_id: {'name': product.name,
                                     'price': float(product.price),
                                     'discount':product.discount,
                                     'quantity':int(quantity),
                                     'image':product.image_1}}

            if 'Wishlist' in session:
                print(session['Wishlist'])
                if product_id in session['Wishlist']:
                    for key, item in session['Wishlist'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            print(item['quantity'])
                            item['quantity'] += 1
                else:
                    session['Wishlist'] = MergeDicts(session['Wishlist'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Wishlist'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect('wish')

@app.route('/wishes')
def getWish():
    if 'Wishlist' not in session or len(session['Wishlist']) <= 0:
        return redirect(url_for('wish'))
    subtotal = 0
    grandtotal = 0
    for key, product in session['Wishlist'].items():
        discount = (product['discount']/100 * float(product['price']))
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
        tax = 10
        grandtotal = subtotal + tax
    return render_template('wish.html', tax=tax, grandtotal=grandtotal, subtotal=subtotal)

@app.route("/updatewishlist/<int:code>", methods=["POST"])
def updatewishlist(code):
    if 'Wishlist' not in session and len(session['Wishlist']) <= 0:
        return redirect(url_for('wish'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        try:
            session.modified = True
            for key, item in session['Wishlist'].items():
                if int(key) == code:
                    print(item['quantity'])
                    item['quantity'] = quantity
                    flash('Item is updated!')
                    return redirect(url_for('getWish'))
        except Exception as e:
            print(e)
            return redirect(url_for('getWish'))

@app.route('/deletewishlist/<int:id>')
def deletewishlist(id):
    if 'Wishlist' not in session or len(session['Wishlist']) <= 0:
        return redirect(url_for('wish'))
    try:
        session.modified = True
        for key, item in session['Wishlist'].items():
            if int(key) == id:
                session['Wishlist'].pop(key, None)
                return redirect(url_for('getWish'))
        return redirect(url_for('getWish'))
    except Exception as e:
        print(e)
        return redirect(url_for('getWish'))

@app.route('/clearwishlist')
def clearwishlist():
    try:
        session.pop('Wishlist', None)
        return redirect(url_for('wish'))
    except Exception as e:
        print(e)

#use in case there's errors in clearing WISHLIST
@app.route('/emptyWishlist')
def empty_wishlist():
    try:
        session.clear()
        return redirect(url_for('wish'))
    except Exception as e:
        print(e)

@app.route("/wish")
def wish():
    return render_template('wish.html')


@app.route('/carts')
def getCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    subtotal = 0
    grandTotal = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount']/100 * float(product['price']))
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
        tax = 10
        grandTotal = subtotal + tax
    return render_template('cart.html', tax=tax, grandTotal=grandTotal, subtotal=subtotal)



@app.route("/updatecart/<int:code>", methods=["POST"])
def updatecart(code):
    if "Shoppingcart" not in session and len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    print(item['quantity'])
                    item['quantity'] = quantity
                    flash('Item is updated!')
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCart'))

@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getCart'))
        return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))

@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)

#Use in case there's errors
@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('home'))
    except Exception as e:
        print(e)

@app.route('/product/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('single_page.html', product=product)

@app.route('/addproduct', methods=["POST", "GET"])
def addproduct():
    categories = Category.query.all()
    form = Addproducts(request.form)
    if request.method =="POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        desc = form.desc.data
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

        addpro = Addproduct(name=name, price=price, discount=discount, stock=stock, desc=desc, category_id=category,
                            image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(addpro)
        flash(f'The product {name} has been added to your database', 'success')
        db.session.commit()
        return redirect(url_for('retrieve_products'))
    return render_template("addproduct.html", title="Add Product Page", form=form,  categories=categories)

@app.route('/updateproduct/<int:id>', methods=["GET", "POST"])
def updateproduct(id):
    product = Addproduct.query.get_or_404(id)
    categories = Category.query.all()
    category = request.form.get('category')

    form = Addproducts(request.form)
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.desc = form.desc.data
        product.category_id = category
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

        db.session.commit()
        flash(f'You product has been updated.', 'success')
        return redirect(url_for('retrieve_products'))

    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.desc.data = product.desc

    return render_template("updateproduct.html", title="Update Product Page", form=form,product=product, categories=categories)

@app.route("/deleteproduct/<int:id>", methods=["POST"])
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method=="POST":
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
            except Exception as e:
                print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} was deleted from your database.', 'success')
        return redirect(url_for('retrieve_products'))

    flash(f"Can't delete the product", 'danger')
    return redirect(url_for('retrieve_products'))

@app.route("/customerSupport")
def customerSupport():
    return render_template('customerSupport.html')

@app.route("/cart")
def cart():
    return render_template('cart.html')

#forgot password
@app.route("/forgotPassword")
def forgotPassword():
    return render_template('forgotPassword.html')

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    create_checkout_form = CheckoutForm(request.form)
    if request.method == 'POST' and create_checkout_form.validate():
        orders_dict = {}
        db = shelve.open('orders.db', 'c')
        try:
            orders_dict = db['Orders']
        except:
            print("Error in retrieving Orders from storage.db.")

        order = Order.Order(create_checkout_form.email.data, create_checkout_form.address1.data,
                            create_checkout_form.address2.data
                            )
        orders_dict[order.get_order_id()] = order
        db['Orders'] = orders_dict
        # Test codes
        orders_dict = db['Orders']
        order = orders_dict[order.get_order_id()]
        print(order.get_email(), "was stored in storage.db successfully with order_id ==",
              order.get_order_id())

        db.close()

        return redirect(url_for('retrieve_order'))
    return render_template('checkout.html', title="Onusles - Checkout", form=create_checkout_form)

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/trackShipment")
def trackShipment():
    return render_template('trackShipment.html')

@app.route("/shopgrid")
def shopgrid():
    page = request.args.get('page',1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=9)
    return render_template('shop_grid.html', products=products, categories=categories())

@app.route("/order", methods=["GET", "POST"])
def retrieve_order():
    orders_dict = {}
    db = shelve.open('orders.db', 'c')
    orders_dict = db['Orders']
    db.close()

    orders_list = []
    for key in orders_dict:
        order = orders_dict.get(key)
        orders_list.append(order)
    return render_template('retrieveOrder.html', count=len(orders_list), orders_list=orders_list)

def categories():
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return categories

@app.route('/categories/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=4)
    return render_template('home.html', get_cat_prod=get_cat_prod, categories=categories(), get_cat=get_cat)

@app.route('/shopgrid/categories/<int:id>')
def get_cat(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=4)
    return render_template('shop_grid.html', get_cat_prod=get_cat_prod, categories=categories(), get_cat=get_cat)

@app.route('/addcat', methods=["GET", "POST"])
def addcat():
    if request.method=="POST":
        getbrand = request.form.get('category')
        cat = Category(name=getbrand)
        db.session.add(cat)
        flash(f'The Category {getbrand} was added to your database.', 'success')
        db.session.commit()
        return redirect(url_for('addcat'))

    return render_template('addcat.html')


@app.route("/products", methods=['GET','POST'])
def products():
    create_product_form = ProductForm(request.form)
    if request.method == 'POST' and create_product_form.validate():
        products_dict = {}
        db = shelve.open('inventory.db', 'c')

        try:
            products_dict = db['Products']
        except:
            print("Error in retrieving Products from inventory.db.")

        product = Product.Product(create_product_form.product_name.data, create_product_form.product_cost.data,
                            create_product_form.stock.data
                            )
        products_dict[product.get_product_id()] = product
        db['Products'] = products_dict

        # Test codes
        products_dict = db['Products']
        product = products_dict[product.get_product_id()]
        print(product.get_product_name(), "was stored in inventory.db successfully with product_id ==",
              product.get_product_id())

        db.close()

        session['product_created'] = product.get_product_name()

        return redirect(url_for('retrieve_products'))
    return render_template("products.html", form=create_product_form)

@app.route('/retrieveProducts')
def retrieve_products():
    page = request.args.get('page',1, type=int)
    products = Addproduct.query.filter(Addproduct.stock >= 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=5)
    return render_template('retrieveProducts.html', products=products)

@app.route('/updateProduct/<int:id>/', methods=['GET','POST'])
def update_product(id):
    update_product_form = ProductForm(request.form)
    if request.method == 'POST' and update_product_form.validate():
        products_dict = {}
        db = shelve.open('inventory.db', 'w')
        products_dict = db['Products']

        product = products_dict.get(id)
        product.set_product_name(update_product_form.product_name.data)
        product.set_product_cost(update_product_form.product_cost.data)
        product.set_stock(update_product_form.stock.data)

        db['Products'] = products_dict
        db.close()

        session['product_updated'] = product.get_product_name()

        return redirect(url_for('retrieve_products'))
    else:
        products_dict = {}
        db = shelve.open('inventory.db', 'r')
        products_dict = db['Products']
        db.close()

        product = products_dict.get(id)
        update_product_form.product_name.data = product.get_product_name()
        update_product_form.product_cost.data = product.get_product_cost()
        update_product_form.stock.data = product.get_stock()

        return render_template('updateProduct.html', form=update_product_form)

@app.route('/deleteProduct/<int:id>', methods=['POST'])
def delete_product(id):
    products_dict = {}
    db = shelve.open('inventory.db', 'w')
    products_dict = db['Products']

    product = products_dict.pop(id)

    db['Products'] = products_dict
    db.close()

    session['product_deleted'] = product.get_product_name()

    return redirect(url_for('retrieve_products'))


@app.route("/staff", methods=['GET', 'POST'])
def staff():
    create_entry_form = CreateEntryForm(request.form)
    if request.method == 'POST' and create_entry_form.validate():
        entries_dict = {}
        db = shelve.open('storage.db', 'c')

        try:
            entries_dict = db['Entries']
        except:
            print("Error in retrieving Entries from storage.db.")

        entry = Entry.Entry(create_entry_form.cost_category.data, create_entry_form.expenses.data, create_entry_form.description.data
                            )
        entries_dict[entry.get_entry_id()] = entry
        db['Entries'] = entries_dict

        # Test codes
        entries_dict = db['Entries']
        entry = entries_dict[entry.get_entry_id()]
        print(entry.get_cost_category(), "was stored in storage.db successfully with entry_id ==",
              entry.get_entry_id())

        db.close()

        session['entry_created'] = entry.get_cost_category()

        return redirect(url_for('retrieve_entries'))
    return render_template("staff.html",form=create_entry_form)

@app.route('/retrieveEntry')
def retrieve_entries():
    entries_dict = {}
    db = shelve.open('storage.db', 'r')
    entries_dict = db['Entries']
    db.close()

    entries_list = []
    for key in entries_dict:
        entry = entries_dict.get(key)
        entries_list.append(entry)
    return render_template('retrieveEntries.html', count=len(entries_list), entries_list=entries_list)

@app.route('/updateEntry/<int:id>/', methods=['GET','POST'])
def update_entry(id):
    update_entry_form = CreateEntryForm(request.form)
    if request.method == 'POST' and update_entry_form.validate():
        entries_dict = {}
        db = shelve.open('storage.db', 'w')
        entries_dict = db['Entries']

        entry = entries_dict.get(id)
        entry.set_cost_category(update_entry_form.cost_category.data)
        entry.set_expenses(update_entry_form.expenses.data)
        entry.set_description(update_entry_form.description.data)

        db['Entries'] = entries_dict
        db.close()

        session['entry_updated'] = entry.get_cost_category()

        return redirect(url_for('retrieve_entries'))
    else:
        entries_dict = {}
        db = shelve.open('storage.db', 'r')
        entries_dict = db['Entries']
        db.close()

        entry = entries_dict.get(id)
        update_entry_form.cost_category.data = entry.get_cost_category()
        update_entry_form.expenses.data = entry.get_expenses()
        update_entry_form.description.data = entry.get_description()

        return render_template('updateEntry.html', form=update_entry_form)

@app.route('/deleteEntry/<int:id>', methods=['POST'])
def delete_entry(id):
    entries_dict = {}
    db = shelve.open('storage.db', 'w')
    entries_dict = db['Entries']

    entry = entries_dict.pop(id)

    db['Entries'] = entries_dict
    db.close()

    session['entry_deleted'] = entry.get_cost_category()

    return redirect(url_for('retrieve_entries'))

@app.route("/transaction", methods=['GET', 'POST'])
def transaction():
    create_transaction_form = TransactionForm(request.form)
    if request.method == 'POST' and create_transaction_form.validate():
        transactions_dict = {}
        db = shelve.open('transaction.db', 'c')

        try:
            transactions_dict = db['Transactions']
        except:
            print("Error in retrieving Transactions from transaction.db.")

        transaction = Transaction.Transaction(create_transaction_form.products.data, create_transaction_form.total_cost.data, create_transaction_form.order_status.data
                            )
        transactions_dict[transaction.get_order_id()] = transaction
        db['Transactions'] = transactions_dict

        # Test codes
        transactions_dict = db['Transactions']
        transaction = transactions_dict[transaction.get_order_id()]
        print(transaction.get_order_id(), "was stored in transactions.db successfully with order_id ==",
              transaction.get_order_id())

        db.close()

        session['entry_created'] = transaction.get_order_id()

        return redirect(url_for('retrieve_transactions'))
    return render_template("transaction.html",form=create_transaction_form)

@app.route('/retrieveTransactions')
def retrieve_transactions():
    transactions_dict = {}
    db = shelve.open('transaction.db', 'r')
    transactions_dict = db['Transactions']
    db.close()

    transactions_list = []
    for key in transactions_dict:
        transaction = transactions_dict.get(key)
        transactions_list.append(transaction)
    return render_template('retrieveTransactions.html', count=len(transactions_list), transactions_list=transactions_list)

@app.route('/updateTransaction/<int:id>/', methods=['GET','POST'])
def update_transaction(id):
    update_transaction_form = TransactionForm(request.form)
    if request.method == 'POST' and update_transaction_form.validate():
        transactions_dict = {}
        db = shelve.open('transaction.db', 'w')
        transactions_dict = db['Transactions']

        transaction = transactions_dict.get(id)
        transaction.set_products(update_transaction_form.products.data)
        transaction.set_total_cost(update_transaction_form.total_cost.data)
        transaction.set_order_status(update_transaction_form.order_status.data)

        db['Transactions'] = transactions_dict
        db.close()

        session['transaction_updated'] = transaction.get_order_id()

        return redirect(url_for('retrieve_transactions'))
    else:
        transactions_dict = {}
        db = shelve.open('transaction.db', 'r')
        transactions_dict = db['Transactions']
        db.close()

        transaction = transactions_dict.get(id)
        update_transaction_form.products.data = transaction.get_products()
        update_transaction_form.total_cost.data = transaction.get_total_cost()
        update_transaction_form.order_status.data = transaction.get_order_status()

        return render_template('updateTransaction.html', form=update_transaction_form)

@app.route('/deleteTransaction/<int:id>', methods=['POST'])
def delete_transaction(id):
    transactions_dict = {}
    db = shelve.open('transaction.db', 'w')
    transactions_dict = db['Transactions']

    transaction = transactions_dict.pop(id)

    db['Transactions'] = transactions_dict
    db.close()

    session['entry_deleted'] = transaction.get_order_id()

    return redirect(url_for('retrieve_transactions'))

#Return Form



#adding new employees
@app.route("/employees", methods=['GET', 'POST'])
def customer():
    create_employees_form = CreateEmployeesForm(request.form)
    if request.method == 'POST' and create_employees_form.validate():
        employees_dict = {}
        db = shelve.open('employees.db', 'c')

        try:
            employees_dict = db['Employees']
        except:
            print("Error in retrieving Employees from employees.db.")

        employees = Employees.Employees(create_employees_form.first_name.data, create_employees_form.last_name.data, create_employees_form.gender.data, create_employees_form.role.data, create_employees_form.phone_number.data, create_employees_form.address.data, create_employees_form.date_of_joining.data)
        employees_dict[employees.get_employees_id()] = employees
        db['Employees'] = employees_dict

        # Test codes
        employees_dict = db['Employees']
        employees = employees_dict[employees.get_employees_id()]
        print(employees.get_first_name(), "was stored in storage.db successfully with employees_id ==",
              employees.get_employees_id())

        db.close()

        session['employees_created'] = employees.get_first_name()


        return redirect(url_for('retrieve_employees'))
    return render_template("employees.html",form=create_employees_form)

#retrieve employees
@app.route('/retrieveEmployees')
def retrieve_employees():
    employees_dict = {}
    db = shelve.open('employees.db', 'r')
    employees_dict = db['Employees']
    db.close()

    employees_list = []
    for key in employees_dict:
        employees = employees_dict.get(key)
        employees_list.append(employees)
    return render_template('retrieveEmployees.html', count=len(employees_list), employees_list=employees_list)

#Update Employees
@app.route('/updateEmployees/<int:id>/', methods=['GET','POST'])
def update_employees(id):
    update_employees_form = CreateEmployeesForm(request.form)
    if request.method == 'POST' and update_employees_form.validate():
        employees_dict = {}
        db = shelve.open('employees.db', 'w')
        employees_dict = db['Employees']

        employees = employees_dict.get(id)
        employees.set_first_name(update_employees_form.first_name.data)
        employees.set_last_name(update_employees_form.last_name.data)
        employees.set_gender(update_employees_form.gender.data)
        employees.set_role(update_employees_form.role.data)
        employees.set_phone_number(update_employees_form.phone_number.data)
        employees.set_address(update_employees_form.address.data)
        employees.set_date_of_joining(update_employees_form.date_of_joining.data)

        db['Employees'] = employees_dict
        db.close()

        session['employes_updated'] = employees.get_first_name()


        return redirect(url_for('retrieve_employees'))
    else:
        employees_dict = {}
        db = shelve.open('employees.db', 'r')
        employees_dict = db['Employees']
        db.close()

        employees = employees_dict.get(id)
        update_employees_form.first_name.data = employees.get_first_name()
        update_employees_form.last_name.data = employees.get_last_name()
        update_employees_form.gender.data = employees.get_gender()
        update_employees_form.role.data = employees.get_role()
        update_employees_form.phone_number.data = employees.get_phone_number()
        update_employees_form.address.data = employees.get_address()
        update_employees_form.date_of_joining.data = employees.get_date_of_joining()

        return render_template('updateEmployees.html', form=update_employees_form)

#Delete Employees
@app.route('/deleteEmployees/<int:id>', methods=['POST'])
def delete_employees(id):
    employees_dict = {}
    db = shelve.open('employees.db', 'w')
    employees_dict = db['Employees']

    employees = employees_dict.pop(id)

    db['Employees'] = employees_dict
    db.close()

    session['employees_deleted'] = employees.get_first_name()

    return redirect(url_for('retrieve_employees'))


@app.route("/customers", methods=['GET', 'POST'])
def customers():
    create_customers_form = CreateCustomersForm(request.form)
    if request.method == 'POST' and create_customers_form.validate():
        customers_dict = {}
        db = shelve.open('customers.db', 'c')

        try:
            customers_dict = db['Customers']
        except:
            print("Error in retrieving Customers from customers.db.")

        customers = Customers.Customers(create_customers_form.first_name.data, create_customers_form.last_name.data, create_customers_form.gender.data, create_customers_form.membership.data, create_customers_form.phone_number.data, create_customers_form.locations.data, create_customers_form.date_of_joining.data)
        customers_dict[customers.get_customers_id()] = customers
        db['Customers'] = customers_dict

        # Test codes
        customers_dict = db['Customers']
        customers = customers_dict[customers.get_customers_id()]
        print(customers.get_first_name(), "was stored in storage.db successfully with customers_id ==",
              customers.get_customers_id())

        db.close()

        session['customers_created'] = customers.get_first_name()


        return redirect(url_for('retrieve_customers'))
    return render_template("customers.html",form=create_customers_form)

@app.route('/retrieveCustomers')
def retrieve_customers():
    customers_dict = {}
    db = shelve.open('customers.db', 'r')
    customers_dict = db['Customers']
    db.close()

    customers_list = []
    for key in customers_dict:
        customers = customers_dict.get(key)
        customers_list.append(customers)
    return render_template('retrieveCustomers.html', count=len(customers_list), customers_list=customers_list)

@app.route('/updateCustomers/<int:id>/', methods=['GET','POST'])
def update_customers(id):
    update_customers_form = CreateCustomersForm(request.form)
    if request.method == 'POST' and update_customers_form.validate():
        customers_dict = {}
        db = shelve.open('customers.db', 'w')
        customers_dict = db['Customers']

        customers = customers_dict.get(id)
        customers.set_first_name(update_customers_form.first_name.data)
        customers.set_last_name(update_customers_form.last_name.data)
        customers.set_gender(update_customers_form.gender.data)
        customers.set_membership(update_customers_form.membership.data)
        customers.set_phone_number(update_customers_form.phone_number.data)
        customers.set_locations(update_customers_form.locations.data)
        customers.set_date_of_joining(update_customers_form.date_of_joining.data)

        db['Customers'] = customers_dict
        db.close()

        session['customers_updated'] = customers.get_first_name()


        return redirect(url_for('retrieve_customers'))
    else:
        customers_dict = {}
        db = shelve.open('customers.db', 'r')
        customers_dict = db['Customers']
        db.close()

        customers = customers_dict.get(id)
        update_customers_form.first_name.data = customers.get_first_name()
        update_customers_form.last_name.data = customers.get_last_name()
        update_customers_form.gender.data = customers.get_gender()
        update_customers_form.membership.data = customers.get_membership()
        update_customers_form.phone_number.data = customers.get_phone_number()
        update_customers_form.locations.data = customers.get_locations()
        update_customers_form.date_of_joining.data = customers.get_date_of_joining()

        return render_template('updateCustomers.html', form=update_customers_form)

@app.route('/deleteCustomers/<int:id>', methods=['POST'])
def delete_customers(id):
    customers_dict = {}
    db = shelve.open('customers.db', 'w')
    customers_dict = db['Customers']

    customers = customers_dict.pop(id)

    db['Customers'] = customers_dict
    db.close()

    session['customers_deleted'] = customers.get_first_name()

    return redirect(url_for('retrieve_customers'))


@app.route('/createForm', methods=['GET', 'POST'])
def create_form():
    create_user_form = CreateYukinForm(request.form)
    if request.method == 'POST' and create_user_form.validate():
        userforms_dict = {}
        db= shelve.open('userforms.db','c')

        try:
            userforms_dict = db['userForms']
        except:
            print('Error in retrieving userForms from storage.db.')

        yukin = Yukin.Yukin(create_user_form.name.data, create_user_form.email.data, create_user_form.form.data, create_user_form.remarks.data)
        userforms_dict[yukin.get_user_id()] = yukin
        db['Users'] = userforms_dict
        # Test codes
        userforms_dict = db['Users']
        yukin = userforms_dict[yukin.get_user_id()]
        print(yukin.get_name(), yukin.get_email(), "was stored in storage.db successfully with user_id ==", yukin.get_user_id())

        db.close()

        return redirect(url_for('retrieve_users'))
    return render_template('createForm.html', form=create_user_form)

@app.route('/retrieveForms')
def retrieve_users():
    userforms_dict = {}
    db = shelve.open('userforms.db','r')
    userforms_dict = db['Users']
    db.close()

    users_list = []
    for key in userforms_dict:
        yukin = userforms_dict.get(key)
        users_list.append(yukin)
    return redirect(url_for('home'))
    return render_template('retrieveForms.html',count=len(users_list), users_list=(users_list))


@app.route('/updateForm/<int:id>/', methods=['GET', 'POST'])
def update_user(id):
    update_user_form = CreateYukinForm(request.form)
    if request.method == 'POST' and update_user_form.validate():
        userforms = {}
        db = shelve.open('userforms.db', 'w')
        userforms = db['Users']

        yukin = userforms.get(id)
        yukin.set_name(update_user_form.name.data)
        yukin.set_email(update_user_form.email.data)
        yukin.set_form(update_user_form.form.data)
        yukin.set_remarks(update_user_form.remarks.data)

        db['Users'] = userforms
        db.close()

        return redirect(url_for('retrieve_users'))
    else:
        userforms = {}
        db = shelve.open('storage.db', 'r')
        userforms = db['Users']
        db.close()

        yukin = userforms.get(id)
        update_user_form.name.data = yukin.get_name()
        update_user_form.email.data = yukin.get_email()
        update_user_form.form.data = yukin.get_form()
        update_user_form.remarks.data = yukin.get_remarks()

        return render_template('updateForm.html', form=update_user_form)



@app.route('/deleteUser/<int:id>', methods=['POST'])
def delete_user(id):
    userforms_dict = {}
    db = shelve.open('userforms.db', 'w')
    userforms_dict = db['Users']

    userforms_dict.pop(id)

    db['Users'] = userforms_dict
    db.close()

    return redirect(url_for('retrieve_users'))

@app.route('/createDonation', methods=['GET','POST'])
def create_donation():
   create_donation_form = CreateDonationForm(request.form)
   if request.method == "POST" and create_donation_form.validate():
       donate_dict ={}
       db = shelve.open('Dstorage.db','c')

       try:
           donate_dict = db['Donate']
       except:
           print('Error in retrieving User Donates from Dstorage.db')

       donate = Donate.Donate(create_donation_form.first_name.data,create_donation_form.last_name.data,create_donation_form.email.data,create_donation_form.check_one.data,create_donation_form.specifications.data)
       donate_dict[donate.get_donate_id()]= donate
       db['Donate'] = donate_dict



       return redirect(url_for('retrieve_donate'))
   return render_template("createDonation.html" , form= create_donation_form)

@app.route('/retrieveDonate')
def retrieve_donate():
    donate_dict = {}
    db = shelve.open('Dstorage.db','r')
    donate_dict = db['Donate']
    db.close()

    donate_list = []
    for key in donate_dict:
        donate = donate_dict.get(key)
        donate_list.append(donate)
    return redirect(url_for('home'))
    return render_template('retrieveDonate.html', count=len(donate_list), donate_list = donate_list )

@app.route('/updateDonate/<int:id>/', methods=['GET','POST'])
def update_donate(id):
    update_donate_form = CreateDonationForm(request.form)
    if request.method == 'POST' and update_donate_form.validate():
        donate_dict = {}
        db = shelve.open('Dstorage.db', 'w')
        donate_dict = db['Donate']

        donate = donate_dict.get(id)
        donate.set_first_name(update_donate_form.first_name.data)
        donate.set_last_name(update_donate_form.last_name.data)
        donate.set_email(update_donate_form.email.data)
        donate.set_check_one(update_donate_form.check_one.data)
        donate.set_specifications(update_donate_form.specifications.data)

        db['Donate'] = donate_dict
        db.close()

        return redirect(url_for('retrievedon'))
    else:
        donate_dict = {}
        db = shelve.open('Dstorage.db', 'r')
        donate_dict = db['Donate']
        db.close()

        donate = donate_dict.get(id)
        update_donate_form.first_name.data = donate.get_first_name()
        update_donate_form.last_name.data = donate.get_last_name()
        update_donate_form.email.data = donate.get_email()
        update_donate_form.check_one.data = donate.get_check_one()
        update_donate_form.specifications.data = donate.get_specifications()


        return render_template('updateDonate.html', form=update_donate_form)

    return render_template('updateDonate.html', form=update_user_form)

@app.route('/deleteDonate/<int:id>',methods=['POST'])
def delete_donate(id):
    donate_dict = {}
    db = shelve.open('Dstorage.db', 'w')
    donate_dict = db['Donate']

    donate_dict.pop(id)

    db['Donate'] = donate_dict
    db.close()

    return redirect(url_for('retrieve_users'))

@app.route('/comment', methods=["GET", "POST"])
def comment():
    form = CommentForm(request.form)
    if request.method == 'POST':
        comment = Comment(name=form.name.data, email=form.email.data, message=form.message.data)
        db.session.add(comment)
        flash('Your comment has been submitted', 'success')
        db.session.commit()
        return redirect(url_for('about'))
    return render_template('comment.html', form=form)

@app.route('/about')
def about():
    page = request.args.get('page',1, type=int)
    comment = Comment.query.filter(Comment.id >= 0).order_by(Comment.id).paginate(page=page, per_page=3)
    return render_template('about.html', comment=comment)

@app.route('/retrieveForm')
def retrieveform():
    userforms_dict = {}
    db = shelve.open('userforms.db','r')
    userforms_dict = db['Users']
    db.close()

    users_list = []
    for key in userforms_dict:
        yukin = userforms_dict.get(key)
        users_list.append(yukin)
    return render_template('retrieveForm.html', count=len(users_list), users_list=(users_list))

@app.route('/retrieveDon')
def retrievedon():
    donate_dict = {}
    db = shelve.open('Dstorage.db','r')
    donate_dict = db['Donate']
    db.close()

    donate_list = []
    for key in donate_dict:
        donate = donate_dict.get(key)
        donate_list.append(donate)
    return render_template('retrieveDon.html', count=len(donate_list), donate_list = donate_list)

@app.route("/retrieveComments")
def retrieve_comments():
    page = request.args.get('page',1, type=int)
    comment = Comment.query.filter(Comment.id >= 0).order_by(Comment.id).paginate(page=page, per_page=5)
    return render_template('retrieveComments.html', comment=comment)

@app.route("/deletecomment/<int:id>", methods=["POST"])
def deletecomment(id):
    comment = Comment.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(comment)
        db.session.commit()
        flash(f'The comment was deleted from your database.', 'success')
        return redirect(url_for('retrieve_comments'))
    flash(f"Can't delete the product", 'danger')
    return redirect(url_for('retrieve_comments'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404

if __name__ == '__main__':
    app.run()
