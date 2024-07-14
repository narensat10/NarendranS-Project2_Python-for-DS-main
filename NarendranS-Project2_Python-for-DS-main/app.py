import secrets

from flask import Flask, request, render_template, session, redirect, url_for
from flask_mysqldb import MySQL
import numpy as np
import sklearn
import pickle

app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.secret_key = secret_key



# Load the pre-trained model
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mclarenf@10405'
app.config['MYSQL_DB'] = 'user'

mysql = MySQL(app)

# Register API
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')


# Login API
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('predict'))  # Redirect to predict.html after successful login
        else:
            return "Invalid username or password"
    return render_template('login.html')


# Home page API
@app.route('/')
def home():
    return render_template('home.html')


# Predict API
@app.route('/predict', methods=['POST'])
def predict_loan_status():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Extract form data and convert to numeric types (with error handling)

            gender = 1 if request.form['gender'] == 'Male' else 0
            married = 1 if request.form['married'] == 'Yes' else 0
            dependents = float(request.form['dependents'])
            education = 1 if request.form['education'] == 'Graduate' else 0
            self_employed = 1 if request.form['self_employed'] == 'Yes' else 0
            applicantincome = int(request.form['applicantincome'])
            coapplicantincome = float(request.form['coapplicantincome'])
            loanamount = float(request.form['loanamount'])
            loan_amount_term = float(request.form['loan_amount_term'])
            credit_history = 1.0 if request.form['credit_history'] == 'Yes' else 0.0
            property_area = request.form['property_area']

            # Encode property area directly
            if property_area == 'Rural':
                property_area = 0
            elif property_area == 'Urban':
                property_area = 1
            else:
                property_area = 2

            print("Form Data:")
            print("Gender:", gender)
            print("Married:", married)
            print("Dependents:", dependents)
            print("Education:", education)
            print("Self Employed:", self_employed)
            print("Applicant Income:", applicantincome)
            print("Coapplicant Income:", coapplicantincome)
            print("Loan Amount:", loanamount)
            print("Loan Amount Term:", loan_amount_term)
            print("Credit History:", credit_history)
            print("Property Area (Numeric):", property_area)


            # Make predictions using the model
            prediction = model.predict([[gender, married, dependents, education, self_employed, applicantincome,
                                         coapplicantincome, loanamount, loan_amount_term, credit_history,
                                         property_area]])


            prediction_text = 'Congrats you are eligible for loan' if prediction[0] == 'y' else 'No! Not Eligible'
            print("Prediction :", prediction[0])


            return render_template('predict.html', prediction_text='Loan status: {}'.format(prediction_text))



    return redirect(url_for('home'))


# Predict API
@app.route('/predict')
def predict():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('predict.html')

# Logout API
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
