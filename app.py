from flask import Flask, jsonify, redirect, render_template, request, url_for
from connect import dbuser, dbhost, dbname, dbpass, dbport
from flask_mysqldb import MySQL
from flask_hashing import Hashing
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import base64
import os


app = Flask(__name__)
app.config["MYSQL_USER"] = dbuser
app.config["MYSQL_PASSWORD"] = dbpass
app.config["MYSQL_DB"] = dbname
app.config["MYSQL_HOST"] = dbhost
app.config["MYSQL_"] = dbport
mysql = MySQL(app)
hashing = Hashing(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.secret_key = 'AGRICULTURE'


#Common For all User
class User(UserMixin):
    def __init__(self, user_id, user_type):
        self.id = user_id
        self.user_type = user_type


@login_manager.user_loader
def load_user(user_id):
    user_data = getUserRole(user_id)
    if user_data:
        return User(user_id, user_data)
    return None

def generate_salt():
    return "NOcIBrUMiDNA"

def generate_menu():
    if current_user.user_type == '3':
        menu_list =[{
            'menu_name':'Pest details',
            'menu_link':'pest_details'
        },
        {
            'menu_name':'Weed details',
            'menu_link':'weed_details'
        },
        {
            'menu_name':'Update Profile',
            'menu_link':'update_profile'
        }
        ]
    elif current_user.user_type == '2':
        menu_list =[
        {
            'menu_name':'Pest details',
            'menu_link':'pest_details'
        },
        {
           'menu_name':'Weed details',
           'menu_link':'weed_details'
        },
        {
            'menu_name':'Add Agriculture Item',
            'menu_link':'add_agriculture'
        }, 
        {
            'menu_name':'agronosmist list',
            'menu_link':'agronomist_list'
        },
        {
            'menu_name':'Update Profile',
            'menu_link':'update_profile'
        },
        {
            'menu_name':'view item',
            'menu_link':'view_item'
        }
        ]
    elif current_user.user_type == '1':
        menu_list =[        
            {
                    'menu_name':'Pest details',
                    'menu_link':'pest_details'
                },
                {
                   'menu_name':'Weed details',
                   'menu_link':'weed_details'
                },
                {
                    'menu_name':'Add Agriculture Item',
                    'menu_link':'add_agriculture'
                }, 
                {
                    'menu_name':'agronosmist list',
                    'menu_link':'agronomist_list'
                },
                {
                    'menu_name':'Update Profile',
                    'menu_link':'update_profile'
                },
                {
                    'menu_name':'view item',
                    'menu_link':'view_item'
                },
                {
                    'menu_name':'Staff Details',
                    'menu_link':'staff_details'
                },
                {
                   'menu_name':'Add Staff',
                   'menu_link':'add_staff'
                }
        ]
    else:
        menu_list= []
    return menu_list

def getUserRole(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_profile WHERE user_id = %s", (user_id,))
    columns = [column[0] for column in cur.description]
    user_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    if user_list:
        return user_list[0]['user_type']
    else:
        print("The user_list is empty.")
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template('register.html')

# agronosmist signup
@app.route('/agronosmist_signup', methods=['POST'])
def agronosmist_signup():
    try:
        cur = mysql.connection.cursor()
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        username = request.form.get('username')
        password = request.form.get('password')
        address = request.form.get('address')
        salt = generate_salt()
        hashed_password = hashing.hash_value(password, salt=salt)
        cur.execute("SELECT * FROM user_profile WHERE email = %s", (username,))
        existing_record = cur.fetchone()
        if existing_record:
            successModalLabel = "Already Exist"
            successModalSubLabel = "User Already Exist"
            return render_template('register.html', success_modal=True, successModalLabel =successModalLabel, successModalSubLabel=successModalSubLabel)
        else:
            cur.execute("INSERT INTO user_profile (first_name, last_name, phone_number, email, password, address, user_type) VALUES (%s, %s, %s, %s, %s, %s, %s )", (first_name, last_name, phone_number, username,hashed_password,  address, 3,))
            cur.connection.commit() 
            successModalLabel = "User Created"
            successModalSubLabel = "Agronosmist created Sucessfully"
            return render_template('register.html', success_modal=True, successModalLabel =successModalLabel, successModalSubLabel=successModalSubLabel)

    except Exception as e:
        # Log the error and return an error response
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add complete"}), 500

# update update_agronomist_profile
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        if request.method == 'POST':
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            phone_number = request.form.get('phone_number')
            password = request.form.get('password')
            address = request.form.get('address')
            if password:
                salt = generate_salt()
                hashed_password = hashing.hash_value(password, salt=salt)
                cur.execute('''UPDATE user_profile SET password=%s WHERE user_id=%s''', (hashed_password, current_user.id))

            cur.execute('''Update user_profile set first_name=%s,last_name=%s, phone_number=%s,address=%s where user_id=%s ''',
                         (first_name,last_name,phone_number,address, current_user.id))
            cur.connection.commit()
            cur.execute("SELECT * FROM user_profile WHERE user_id = %s", (current_user.id))
            existing_record = cur.fetchone()
            column_names = [column[0] for column in cur.description]
            record_dict = dict(zip(column_names, existing_record))
            return render_template('update_profile.html', user_list=record_dict,menu_list=menu_list, success_modal=True, successModalLabel='Updated', successModalSubLabel="user updated")
        elif request.method == 'GET':
            cur.execute("SELECT * FROM user_profile WHERE user_id = %s", (current_user.id))
            existing_record = cur.fetchone()
            if existing_record:
                column_names = [column[0] for column in cur.description]
                record_dict = dict(zip(column_names, existing_record))
                return render_template('update_profile.html', user_list=record_dict,menu_list=menu_list)
    except Exception as e:
        # Log the error and return an error response
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add complete"}), 500

#login
@app.route("/check_user", methods=["post"])
def check_login_details():
    try:
        cur = mysql.connection.cursor()
        username = request.form.get('email')
        password = request.form.get('password')
        salt = generate_salt()
        hashed_password = hashing.hash_value(password, salt=salt)
        cur.execute("SELECT * FROM user_profile WHERE email = %s and password = %s and status=1", (username, hashed_password,))
        existing_record = cur.fetchone()
        if existing_record:
            column_names = [column[0] for column in cur.description]
            record_dict = dict(zip(column_names, existing_record))
            print(record_dict['user_id'])
            login_user(User(record_dict['user_id'], record_dict['user_type']))
            return redirect(url_for('dashboard'))
        else:
            successModalLabel = "Login Failed"
            successModalSubLabel = "User Name and Password Mismatch"
            return render_template('login.html', success_modal=True, successModalLabel =successModalLabel, successModalSubLabel=successModalSubLabel)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add complete"}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    menu_list= generate_menu()
    return render_template('dashboard.html', menu_list=menu_list)

# Common for all user 
@app.route("/pest_list/<id>")
@login_required
def pest_list(id):
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT *
            FROM agriculture.agriculture_item 
            WHERE agriculture_type = 1 and agriculture_id= %s''', (id,))
        columns = [column[0] for column in cur.description]
        pest_list = [dict(zip(columns, row)) for row in cur.fetchall()]

        cur.execute('''SELECT *
            FROM img_table 
            WHERE arg_id= %s ORDER BY is_primary DESC''', (id,))
        columns = [column[0] for column in cur.description]
        image_list = [dict(zip(columns, row)) for row in cur.fetchall()]
        return render_template('pest.html', menu_list=menu_list,pest_list=pest_list, image_list=image_list)
    except Exception as ex:
        # Handle exceptions
        print(f"An error occurred: {str(ex)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route("/pest-details")
@login_required
def pest_details():
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT *
            FROM agriculture.agriculture_item 
            JOIN agriculture.img_table ON agriculture_id = arg_id
            WHERE agriculture_type = 1 and is_primary=1 and is_active=1''')
        columns = [column[0] for column in cur.description]
        pest_details = [dict(zip(columns, row)) for row in cur.fetchall()]
        return render_template('pest_details.html', menu_list=menu_list, pest_details=pest_details)
    except Exception as ex:
        # Handle exceptions
        print(f"An error occurred: {str(ex)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route("/weed_list/<id>")
@login_required
def weed_list(id):
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT *
            FROM agriculture.agriculture_item 
            WHERE agriculture_type = 2 and agriculture_id= %s''', (id,))
        columns = [column[0] for column in cur.description]
        pest_list = [dict(zip(columns, row)) for row in cur.fetchall()]

        cur.execute('''SELECT *
            FROM img_table 
            WHERE arg_id= %s ORDER BY is_primary DESC''', (id,))
        columns = [column[0] for column in cur.description]
        image_list = [dict(zip(columns, row)) for row in cur.fetchall()]
        return render_template('pest.html', menu_list=menu_list, pest_list = pest_list, image_list=image_list)
    except Exception as ex:
        # Handle exceptions
        print(f"An error occurred: {str(ex)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route("/weed_details")
@login_required
def weed_details():
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT *
            FROM agriculture.agriculture_item 
            JOIN agriculture.img_table ON agriculture_id = arg_id
            WHERE agriculture_type = 2 and is_primary=1 and is_active=1''')
        columns = [column[0] for column in cur.description]
        pest_details = [dict(zip(columns, row)) for row in cur.fetchall()]
        return render_template('weed_details.html', menu_list=menu_list, weed_details=pest_details)
    except Exception as ex:
        # Handle exceptions
        print(f"An error occurred: {str(ex)}")
        return jsonify({"error": "An error occurred during the search."})

# Staff item 
@app.route("/add_item", methods=['post'])
def add_item():
    try:
        arg_item =request.form.get('arg_item')
        common_name =request.form.get('common_name')
        science_name =request.form.get('science_name')
        key_char =request.form.get('key_char')
        biology =request.form.get('biology')
        impacts =request.form.get('impacts')
        controls =request.form.get('controls')
        information =request.form.get('information')
        files = request.files.getlist('files')
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO agriculture_item 
                    (agriculture_type, common_name, science_name, key_char, biology, impacts, controls, information) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
                    (arg_item, common_name, science_name,key_char,biology,impacts,controls,information,)
                    )
        mysql.connection.commit()
        cur.execute('SELECT LAST_INSERT_ID()')
        last_inserted_id = cur.fetchone()[0]
        for index, file in enumerate(files):
            is_primary = 1 if index == 1 else 0
            file_data = base64.b64encode(file.read())
            cur.execute('''INSERT INTO img_table (img_url, is_primary, arg_id) VALUES (%s, %s, %s)''',
                        (file_data, is_primary, last_inserted_id))
            mysql.connection.commit()
        cur.close()
        successModalLabel = "Already Exist"
        successModalSubLabel = "Part Already Exist"
        return  redirect(url_for('add_agriculture'))

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route("/agronomist_list")
@login_required
def agronomist_list():
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user_profile WHERE user_type = 3")
        columns = [column[0] for column in cur.description]
        customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    except Exception as ex:
        # Handle exceptions
        print(f"An error occurred: {str(ex)}")
        return jsonify({"error": "An error occurred during the search."})
    return render_template('agronomist_list.html', menu_list=menu_list, staff_list = customer_list)

@app.route("/staff_details")
@login_required
def staff_details():
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user_profile WHERE user_type = 2")
        columns = [column[0] for column in cur.description]
        customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
        return render_template('staff_details.html', menu_list=menu_list, staff_list = customer_list)
    except Exception as ex:
        # Handle exceptions
        print(f"An error occurred: {str(ex)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route("/user_list/<id>")
@login_required
def user_list(id):
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user_profile WHERE user_id= %s ", (id))
        columns = [column[0] for column in cur.description]
        customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    except Exception as ex:
        pass
    return render_template('staff_list.html', menu_list=menu_list, staff_list = customer_list)

@app.route('/update_staff',  methods=['GET', 'POST'])
def update_staff():
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        if request.method == 'POST':
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            phone_number = request.form.get('phone_number')            
            address = request.form.get('address')
            status = request.form.get('status')
            staff_id = request.form.get('user_id')
            cur.execute('''Update user_profile set first_name=%s,last_name=%s, phone_number=%s,address=%s, status=%s where user_id=%s ''',
                         (first_name,last_name,phone_number,address,status, staff_id))
            cur.connection.commit()
            print(first_name, status, phone_number)
    except Exception as e:
        # Log the error and return an error response
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add complete"}), 500
    staff_id = request.form.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_profile WHERE user_id= %s ", (staff_id,))
    columns = [column[0] for column in cur.description]
    customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    successModalLabel = "User Updated"
    successModalSubLabel = "Agronosmist Updated Sucessfully"
    return render_template('staff_list.html', menu_list=menu_list, staff_list = customer_list, success_modal=True, successModalLabel =successModalLabel, successModalSubLabel=successModalSubLabel)

@app.route("/add_staff")
@login_required
def add_staff():
    menu_list= generate_menu()
    return render_template('staff_add.html', menu_list=menu_list)

@app.route("/add_agriculture")
@login_required
def add_agriculture():
    menu_list= generate_menu()
    return render_template('add_agriculture.html',menu_list=menu_list)

@app.route("/view_item")
@login_required
def view_item():
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT *
            FROM agriculture.agriculture_item 
            JOIN agriculture.img_table ON agriculture_id = arg_id
            WHERE is_primary=1''')
        columns = [column[0] for column in cur.description]
        pest_details = [dict(zip(columns, row)) for row in cur.fetchall()]
        return render_template('view_item.html', menu_list=menu_list, pest_details=pest_details)
    except Exception as ex:
        # Handle exceptions
        print(f"An error occurred: {str(ex)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route("/delete_item/<int:item_id>")
@login_required
def delete_item(item_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('''UPDATE agriculture_item SET is_active=0 WHERE agriculture_id=%s''', (item_id,))
        cur.connection.commit()
        return  redirect(url_for('view_item'))
    except Exception as ex:
        # Handle exceptions
        print(f"An error occurred: {str(ex)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route("/edit_item/<id>")
@login_required
def edit_item(id):
    menu_list= generate_menu()
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM agriculture WHERE agriculture_id= %s ", (id))
        columns = [column[0] for column in cur.description]
        customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
        return render_template('edit_item.html', menu_list=menu_list, staff_list = customer_list)
    except Exception as ex:
        return render_template('edit_item.html', menu_list=menu_list)



@app.route("/staff_add", methods=['post'])
def staff_add():
    try:
        cur = mysql.connection.cursor()
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        email = data.get('username')
        password = data.get('password')
        salt = generate_salt()
        hashed_password = hashing.hash_value(password, salt=salt)
        cur.execute("SELECT * FROM user_profile WHERE email = %s", (email,))
        existing_record = cur.fetchone()
        if existing_record:
            return jsonify({"success": False, "error": "Already Exist"})
        else:
            cur.execute("INSERT INTO user_profile (first_name, last_name, phone_number, email, password, user_type) VALUES (%s, %s, %s, %s, %s, %s)", (first_name, last_name, phone_number, email,hashed_password, 2,))
            cur.connection.commit() 
            return jsonify({"success": True, "error": None})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add complete"}), 500

if __name__ == '__main__':
    app.run(debug=True)