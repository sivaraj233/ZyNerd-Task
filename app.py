from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap


app = Flask(__name__)
bootstrap = Bootstrap(app)

#menu 
def generate_menu(role):
        technicians_menu = [
        {'url': 'technicians_customer_job', 'menuname':'Current Jobs' },
        {'url': 'technicians_job', 'menuname':'Jobs' }
        ]
        admin_menu = [
            {'url': 'admin_customer_list', 'menuname':'Customer List' },
            {'url': 'admin_customer_search', 'menuname':'Customer Search' }, 
            {'url': 'admin_add_customer', 'menuname':'Add Customer' },
            {'url': 'admin_add_service', 'menuname':'Add Service' },
            {'url': 'admin_add_part', 'menuname':'Add Part' },
            {'url': 'admin_schedule_jobs', 'menuname':'Schedule Jobs' },
            {'url': 'admin_bills', 'menuname':'Unpaid & pay Bills' },
            {'url': 'admin_history', 'menuname':'Billing History' },
            ]
        if(role == 'admin'):
            menu = admin_menu
        else:
            menu = technicians_menu
        return menu
#login page
@app.route("/")
def home():
    return render_template('index.html')

#button click
@app.route('/login', methods=['POST'])
def login():
    role=""
    username = request.form.get('username')
    if( username.endswith('admin')):
        role = 'admin'
    else:
        role = 'Technicians'
    return redirect(url_for('dashboard', role=role))


@app.route('/dashboard/<role>')
def dashboard(role):
    menu = generate_menu(role)
    return render_template('dashboard.html', role=role, menu=menu)

# #admin routing
@app.route('/dashboard/admin/customer_list')
def admin_customer_list():
    menu = generate_menu('admin')
    data = [{
        'first_name':'sivaraj',
        'family_name':'M',
        'email':'sivaraj@gmail.com',
        'phonenumber':'9003912752',

    },{
        'first_name':'sivaraj',
        'family_name':'M',
        'email':'sivaraj@gmail.com',
        'phonenumber':'9003912752',

    },
    {
        'first_name':'sivaraj',
        'family_name':'M',
        'email':'sivaraj@gmail.com',
        'phonenumber':'9003912752',

    },
    {
        'first_name':'sivaraj',
        'family_name':'M',
        'email':'sivaraj@gmail.com',
        'phonenumber':'9003912752',

    }]
    return render_template('admin/customer_list.html', data=data, menu=menu)

@app.route('/dashboard/admin/customer_search')
def admin_customer_search():
    menu = generate_menu('admin')
    return render_template('admin/customer_search.html', menu=menu)

@app.route('/dashboard/admin/add_customer')
def admin_add_customer():
    menu = generate_menu('admin')
    return render_template('admin/add_customer.html', menu=menu)

@app.route('/dashboard/admin/add_service')
def admin_add_service():
    menu = generate_menu('admin')
    return render_template('admin/add_service.html', menu=menu)

@app.route('/dashboard/admin/add_part')
def admin_add_part():
    menu = generate_menu('admin')
    return render_template('admin/add_part.html', menu=menu)

@app.route('/dashboard/admin/schedule_jobs')
def admin_schedule_jobs():
    menu = generate_menu('admin')
    return render_template('admin/schedule_jobs.html', menu=menu)

@app.route('/dashboard/admin/bills')
def admin_bills():
    menu = generate_menu('admin')
    bills = [{
        'first_name': 'Sivaraj',
        'jobs': 'test',
        'status': 'Pending'
    },
    {
        'first_name': 'Sivaraj',
        'jobs': 'test',
        'status': 'Completed'
    },
    {
        'first_name': 'Sivaraj',
        'jobs': 'test',
        'status': 'Completed'
    }]
    return render_template('admin/bills.html', bills=bills, menu=menu)

@app.route('/dashboard/admin/history')
def admin_history():
    menu = generate_menu('admin')
    return render_template('admin/history.html', menu=menu)

# #technicians
@app.route('/dashboard/technicians/jobs')
def technicians_job():
    menu = generate_menu('technicians')
    return render_template('technicians/jobs.html', menu=menu)

@app.route('/dashboard/technicians/customer_jobs')
def technicians_customer_job():
    menu = generate_menu('technicians')
    return render_template('technicians/customer_jobs.html', menu=menu)

if __name__ == '__main__':
    app.run(debug=True)