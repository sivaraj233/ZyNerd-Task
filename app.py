import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Null@123"
app.config["MYSQL_DB"] = "spb"

mysql = MySQL(app)
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
    cur = mysql.connection.cursor()
    cur.execute("""SELECT job.*, customer.first_name
        FROM job
        JOIN customer ON job.customer = customer.customer_id where completed=0""")
    columns = [column[0] for column in cur.description]
    rv = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('technicians/customer_jobs.html', data=rv)


#technicians
@app.route('/technicians/jobs/<id>')
def technicians_job(id):
    cur = mysql.connection.cursor()
    #get part
    cur.execute("""
        SELECT job_part.*, part.part_id, part.part_name, part.cost
        FROM job_part
        JOIN part ON job_part.part_id = part.part_id
        WHERE job_part.JOB_ID = %s
    """, (id,))
    columns = [column[0] for column in cur.description]
    part_details = [dict(zip(columns, row)) for row in cur.fetchall()]

    #get service
    cur.execute("""
        SELECT job_service.*, service.service_id, service.service_name, service.cost
        FROM job_service
        JOIN service ON job_service.service_id = service.service_id
        WHERE job_service.JOB_ID = %s
    """, (id,))
    columns = [column[0] for column in cur.description]
    job_details = [dict(zip(columns, row)) for row in cur.fetchall()]

    #get all part
    cur.execute("""
        SELECT * FROM part
    """)
    columns = [column[0] for column in cur.description]
    job_part = [dict(zip(columns, row)) for row in cur.fetchall()]

    #get all service
    cur.execute("""
        SELECT * FROM service
    """)
    columns = [column[0] for column in cur.description]
    job_service = [dict(zip(columns, row)) for row in cur.fetchall()]

    #get customer Details
    cur.execute("""SELECT job.*, customer.first_name
        FROM job
        JOIN customer ON job.customer = customer.customer_id where job_id=%s""", (id))
    columns = [column[0] for column in cur.description]
    customer_details = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('technicians/jobs.html', part_details=part_details,job_details=job_details, job_part=job_part, job_service=job_service, customer_details=customer_details, job_id=id)

@app.route('/add_part', methods=['POST'])
def add_part():
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        part_id = data.get('part_id')
        qty = data.get('qty')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM job_part WHERE job_id = %s AND part_id = %s", (job_id, part_id))
        existing_record = cur.fetchone()

        if existing_record:
            updated_qty = existing_record[2] + int(qty)
            cur.execute("UPDATE job_part SET qty = %s WHERE job_id = %s AND part_id = %s", (updated_qty, job_id, part_id))
        else:
            # Insert a new record
            cur.execute("INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s)", (job_id, part_id, qty))

        cur.connection.commit() 
        return jsonify({"message": "Part added successfully"})
    except Exception as e:
        # Log the error and return an error response
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add part"}), 500

@app.route('/add_service', methods=['POST'])
def add_service():
    # Retrieve data from the request
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        service_id = data.get('service_id')
        qty = data.get('qty')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM job_service WHERE job_id = %s AND service_id = %s", (job_id, service_id))
        existing_record = cur.fetchone()

        if existing_record:
            updated_qty = existing_record[2] + int(qty)
            cur.execute("UPDATE job_service SET qty = %s WHERE job_id = %s AND service_id = %s", (updated_qty, job_id, service_id))
        else:
            # Insert a new record
            cur.execute("INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s)", (job_id, service_id, qty))

        cur.connection.commit() 
        return jsonify({"message": "Service added successfully"})
    except Exception as e:
        # Log the error and return an error response
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add Service"}), 500

@app.route('/completed', methods=['POST'])
def mark_completed():
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        cur = mysql.connection.cursor()

        # Calculate the total cost from job_part
        cur.execute("""
            SELECT IFNULL(SUM(part.cost * job_part.qty), 0) AS part_total
            FROM job_part
            JOIN part ON job_part.part_id = part.part_id
            WHERE job_part.job_id = %s
        """, (job_id,))
        part_total = cur.fetchone()[0]
        print(part_total)
        # Calculate the total cost from job_service
        cur.execute("""
            SELECT IFNULL(SUM(service.cost * job_service.qty), 0) AS service_total
            FROM job_service
            JOIN service ON job_service.service_id = service.service_id
            WHERE job_service.job_id = %s
        """, (job_id,))
        service_total = cur.fetchone()[0]
        print(service_total)

        # Calculate the overall total cost
        total_cost = part_total + service_total
        print(total_cost)
        # Update the total cost in the job table
        cur.execute("UPDATE job SET total_cost = %s, completed=1 WHERE job_id = %s", (total_cost, job_id))
        mysql.connection.commit()
        return jsonify({"message": "Service added successfully"})
    
    except Exception as e:
        # Log the error and return an error response
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add Service"}), 500


#admin page
@app.route('/admin')
def admin_home():
    return render_template('admin/admin_index.html')

@app.route('/admin/customer_list')
def admin_customer_list():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT *
        FROM customer ORDER BY family_name, first_name""")
    columns = [column[0] for column in cur.description]
    customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('admin/customer_list.html', customer_details=customer_list)

@app.route('/admin/customer_search')
def admin_customer_search():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT *
        FROM customer ORDER BY family_name, first_name""")
    columns = [column[0] for column in cur.description]
    customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('admin/customer_search.html', customer_details=customer_list)
@app.route('/search_customers',methods=['POST'])
def search_customers():
    data = request.get_json()
    search_term = data.get('searchItem')
    
    try:
        cur = mysql.connection.cursor()

        # Execute the SQL query
        query = (
            "SELECT * FROM customer "
            "WHERE first_name LIKE %s "
            "ORDER BY first_name"
        )
        cur.execute(query, (f"%{search_term}%",))

        # Fetch all the results
        columns = [column[0] for column in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]

        # Close the cursor
        cur.close()

        # Return a JSON response
        return jsonify({"data": results})

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})


@app.route('/admin/add_customer')
def admin_add_customer():
    return render_template('admin/add_customer.html')

@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.get_json()
    try:
        data = request.get_json()
        first_name = data.get('first_name')
        family_name = data.get('family_name')
        email = data.get('email')
        phonenumber = data.get('phone')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM customer WHERE email = %s AND phone = %s", (email, phonenumber))
        existing_record = cur.fetchone()

        if existing_record:
            return jsonify({"data": "Already Exist", "isExist": True})
        else:
            # Insert a new record
            cur.execute("INSERT INTO customer (first_name, family_name, email, phone) VALUES (%s, %s, %s, %s)", (first_name, family_name, email, phonenumber))

        cur.connection.commit() 

        # Return a JSON response
        return jsonify({"data": "Insert Sucessfully", "isExist": False})

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route('/admin/add_part')
def admin_add_part():
    return render_template('admin/add_part.html')
@app.route('/add_master_part', methods=['POST'])
def add_master_part():
    data = request.get_json()
    try:
        data = request.get_json()
        part_name = data.get('part_name')
        cost = data.get('cost')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM part WHERE part_name = %s AND cost = %s", (part_name, cost))
        existing_record = cur.fetchone()

        if existing_record:
            return jsonify({"data": "Already Exist", "isExist": True})
        else:
            # Insert a new record
            cur.execute("INSERT INTO part (part_name, cost) VALUES (%s, %s)", (part_name, cost))

        cur.connection.commit() 

        # Return a JSON response
        return jsonify({"data": "Insert Sucessfully", "isExist": False})

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})


@app.route('/admin/add_service')
def admin_add_service():
    return render_template('admin/add_service.html')

@app.route('/add_master_service', methods=['POST'])
def add_master_service():
    data = request.get_json()
    try:
        data = request.get_json()
        service_name = data.get('service_name')
        cost = data.get('cost')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM service WHERE service_name = %s AND cost = %s", (service_name, cost))
        existing_record = cur.fetchone()

        if existing_record:
            return jsonify({"data": "Already Exist", "isExist": True})
        else:
            # Insert a new record
            cur.execute("INSERT INTO service (service_name, cost) VALUES (%s, %s)", (service_name, cost))

        cur.connection.commit() 

        # Return a JSON response
        return jsonify({"data": "Insert Sucessfully", "isExist": False})

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route('/admin/schedule_jobs')
def admin_schedule_jobs():
    today = datetime.date.today().strftime('%Y-%m-%d')
    cur = mysql.connection.cursor()
    cur.execute("""SELECT *
        FROM customer ORDER BY family_name, first_name""")
    columns = [column[0] for column in cur.description]
    customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('admin/schedule_jobs.html', customer_list=customer_list, today=today)

@app.route('/book_job', methods=['POST'])
def book_job():
    try:
        data = request.get_json()
        customerSelect = data.get('customerSelect')
        bookingDate = data.get('bookingDate')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM job WHERE customer = %s AND job_date = %s", (customerSelect, bookingDate))
        existing_record = cur.fetchone()

        if existing_record:
            return jsonify({"data": "Already Exist", "isExist": True})
        else:
            # Insert a new record
            cur.execute("INSERT INTO job (customer, job_date) VALUES (%s, %s)", (customerSelect, bookingDate))

        cur.connection.commit() 

        # Return a JSON response
        return jsonify({"data": "Insert Sucessfully", "isExist": False})

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route('/admin/bills')
def admin_bills():
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT job.job_id, job.job_date, customer.first_name, job.total_cost,customer_id
    FROM job
    JOIN customer ON job.customer = customer.customer_id
    WHERE job.paid = 0;
    """)
    columns = [column[0] for column in cur.description]
    customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('admin/bills.html',customer_details=customer_list)

@app.route('/paid', methods=['POST'])
def mark_paid():
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        print(job_id)
        cur = mysql.connection.cursor()
        # Update the total cost in the job table
        cur.execute("UPDATE job SET paid=1 WHERE job_id = %s", (job_id,))
        mysql.connection.commit()
        return jsonify({"message": "Service added successfully"})
    
    except Exception as e:
        # Log the error and return an error response
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add Service"}), 500

@app.route('/search_customer',methods=['POST'])
def search_customer():
    data = request.get_json()
    search_term = data.get('searchItem')
    print(search_term)
    try:
        cur = mysql.connection.cursor()

        # Execute the SQL query
        cur.execute(""" SELECT job.job_id, job.job_date, customer.first_name, job.total_cost,customer_id
            FROM job
            JOIN customer ON job.customer = customer.customer_id
            WHERE job.paid = 0 and customer.customer_id=%s;""", (search_term))

        # Fetch all the results
        columns = [column[0] for column in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        print(results)
        # Close the cursor
        cur.close()

        # Return a JSON response
        return jsonify({"data": results})

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})



if __name__ == '__main__':
    app.run(debug=True)