from wtforms.fields import *
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms.fields.html5 import EmailField
from wtforms import Form, StringField, TextAreaField, SelectField, IntegerField, validators, RadioField, PasswordField, SubmitField

class CreateEntryForm(Form):
    cost_category = StringField('Cost Category', [validators.Length(min=1, max=150), validators.DataRequired()])
    expenses = StringField('Expenses', [validators.Length(min=1, max=150), validators.DataRequired()])
    description = TextAreaField('Description', [validators.Optional()])

class CheckoutForm(Form):
    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])
    email = EmailField('Email', [validators.DataRequired()])
    phone = IntegerField('Phone Number', [validators.DataRequired()])
    country = SelectField('Country', [validators.DataRequired()],
                         choices=[('', 'Select'), ('S', 'Singapore'), ('AF', 'Afghanistan')], default='')
    address1 = StringField('Address Line 1', [validators.DataRequired()])
    address2 = StringField('Address Line 2', [validators.DataRequired()])
    postal_code = IntegerField('Postal Code', [validators.DataRequired()])

    card_name = StringField("Card Name", [validators.Optional()])
    card_number = IntegerField("Card Number", [validators.Optional()])
    expiry_date = StringField("Expiry Date", [validators.Optional()])
    cvv = IntegerField("CVV", [validators.Optional()])
    remember_me = BooleanField("Remember Me")

class ProductForm(Form):
    product_name = StringField('Product Name', [validators.DataRequired()])
    product_cost = StringField('Price', [validators.DataRequired()])
    stock = IntegerField('Qty', [validators.DataRequired()])

class TransactionForm(Form):
    products = IntegerField('Products', [validators.DataRequired()])
    total_cost = StringField('Total Cost', [validators.DataRequired()])
    order_status = StringField('Order Status', [validators.DataRequired()])


class CreateCustomersForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('F', 'Female'), ('M', 'Male')], default='')
    membership = RadioField('Membership', choices=[('F', 'Fellow'), ('S', 'Senior'), ('P', 'Professional')], default='F')
    phone_number = IntegerField('Phone Number', [validators.DataRequired()])
    locations = TextAreaField('Locations', [validators.Optional()])
    date_of_joining = TextAreaField('Date Of Joining', [validators.Optional()])

class CreateEmployeesForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('F', 'Female'), ('M', 'Male')], default='')
    role = RadioField('Role', choices=[('M', 'Manager'), ('S', 'Supervisor'), ('F', 'Full-time'), ('P', 'Part-time')], default='F')
    phone_number = IntegerField('Phone Number', [validators.DataRequired()])
    address = TextAreaField('Locations', [validators.Optional()])
    date_of_joining = TextAreaField('Date Of Joining', [validators.Optional()])


class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()]
                        )
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])

class CreateYukinForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=1, max=150), validators.DataRequired()])
    form = RadioField('Form Type', choices=[('F', 'Feedback'), ('P', 'Preference')], default='F')
    remarks = TextAreaField('Remarks', [validators.DataRequired()])

class CreateDonationForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=1, max=150), validators.DataRequired()])
    check_one = RadioField('Check One', choices=[('C', 'Clothes'), ('S', 'Shoes'), ('B', 'Bags'), ('A','Accessories')], default='F')
    specifications = TextAreaField('Specifications', [validators.DataRequired()])

class Addproducts(Form):
    name = StringField("Name", [validators.DataRequired()])
    price = IntegerField("Price", [validators.DataRequired()])
    discount = IntegerField("Discount", default=0)
    stock = IntegerField("Stock", [validators.DataRequired()])
    desc = TextAreaField("Description", [validators.DataRequired()])

    image_1 = FileField('Image 1', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])
    image_2 = FileField('Image 2', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])
    image_3 = FileField('Image 3', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])

class CommentForm(FlaskForm):
    name = StringField("Name", [validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=1, max=150), validators.DataRequired()])
    message = TextAreaField("Comment", [validators.DataRequired()])
    submit = SubmitField('Submit')
