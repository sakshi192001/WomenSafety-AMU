from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import gmplot
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import cv2
import os

import time

app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysqlpassword'
app.config['MYSQL_DB'] = 'WomenSafety'

# Intialize MySQL
mysql = MySQL(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM details WHERE email = %s AND password = %s', [email, password])
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['FirstName'] = account['FirstName']
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

# @app.route('/logout')
# def logout():
#     # Remove session data, this will log the user out
#    session.pop('loggedin', None)
#    session.pop('id', None)
#    session.pop('email', None)
#    # Redirect to login page
#    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'contact_number' in request.form and 'password' in request.form and 'FirstName' in request.form and 'LastName' in request.form:
        # Create variables for easy access
        FirstName = request.form['FirstName']
        LastName = request.form['LastName']
        email = request.form['email']
        contact_number = request.form['contact_number']
        password = request.form['password']
        
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM details WHERE email = %s AND password=%s', [email, password])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z]+', FirstName):
            msg = 'Username must contain only letters!'
        elif not FirstName or not LastName or not password or not email or not contact_number:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO details VALUES(%s, %s, %s, %s, %s)', (FirstName, LastName, email,contact_number, password))
            mysql.connection.commit()
            msg = 'Successfully registered! Please Sign-In'
            return render_template('index.html')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html',msg=msg)


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':                    
        print(request.form['coord'])
       

# link =https://console.twilio.com/us1/develop/phone-numbers/manage/verified?frameUrl=%2Fconsole%2Fphone-numbers%2Fverified%3Fx-target-region%3Dus1

        account_sid = "AC4a2b694a120c8e36751a679266b9b6b2"
        auth_token = "140cffd2c581692c83ad4595c4061b08"
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
                body= request.form['coord'],
                from_='+14173440746',
                to='+919834480563')  
    return render_template('index.html')


# @app.route('/map')
# def map():
#     return render_template('map.html')


@app.route('/defense')
def defense():
    return render_template('defense.html')

@app.route('/guardian')
def guardian():
    return render_template('guardian.html')



if __name__=="__main__":
    app.run(debug=True)



#-------------------------------------------------------------------------------------------

# # @app.route('/logout')
# # def logout():
# #     # Remove session data, this will log the user out
# #    session.pop('loggedin', None)
# #    session.pop('id', None)
# #    session.pop('email', None)
# #    # Redirect to login page
# #    return redirect(url_for('login'))

@app.route('/capture', methods=['GET','POST'])
def capture():
# Define the duration (in seconds) of the video capture here
    capture_duration = 30

    cap = cv2.VideoCapture(0)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

    start_time = time.time()
    while( int(time.time() - start_time) < capture_duration ):
        ret, frame = cap.read()
        if ret==True:
            frame = cv2.flip(frame,1)

            # write the flipped frame
            out.write(frame)

            cv2.imshow('frame',frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
        else:
            break

    # Release everything if job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    #os.remove('output.avi')
    return render_template('tp.html')

# @app.route('/sendmail', methods=['GET','POST'])
# def sendmail():
#     email_user = 'parikhdhruv76@gmail.com'
#     email_password = 'yddghrhhglieewcx'
#     email_send = 'varadjs22@gmail.com'

#     subject = 'sos'

#     msg = MIMEMultipart()
#     msg['From'] = email_user
#     msg['To'] = email_send
#     msg['Subject'] = subject

#     body = 'Hi there, sending this email from Python!'
#     msg.attach(MIMEText(body,'plain'))

#     filename='output.avi'
#     attachment  =open(filename,'rb')

#     part = MIMEBase('application','octet-stream')
#     part.set_payload((attachment).read())
#     encoders.encode_base64(part)
#     part.add_header('Content-Disposition',"attachment; filename= "+filename)

#     msg.attach(part)
#     text = msg.as_string()
#     server = smtplib.SMTP('smtp.gmail.com',587)
#     server.starttls()
#     server.login(email_user,email_password)


#     server.sendmail(email_user,email_send,text)
#     server.quit()
#     return render_template('index.html')
# if _name=="main_":
#     app.run(debug=True)