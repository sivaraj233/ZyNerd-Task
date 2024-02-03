import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from itertools import groupby
from operator import itemgetter  # Import itemgetter


app = Flask(__name__)
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Null@123"
app.config["MYSQL_DB"] = "spb"

mysql = MySQL(app)
@app.route("/")
def index():
    return render_template('index.html')

#login page
@app.route("/job")
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
        # data = request.get_json()
        job_id = request.form.get('job_id')
        part_id = request.form.get('part_id')
        qty = request.form.get('qty')
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
        return redirect(url_for('technicians_job', id=job_id))
    except Exception as e:
        # Log the error and return an error response
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add part"}), 500

@app.route('/add_service', methods=['POST'])
def add_service():
    # Retrieve data from the request
    try:
        job_id = request.form.get('job_id')
        service_id = request.form.get('service_id')
        qty = request.form.get('qty')
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
        return redirect(url_for('technicians_job', id=job_id))
    except Exception as e:
        # Log the error and return an error response
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add Service"}), 500

@app.route('/completed', methods=['POST'])
def mark_completed():
    try:
        job_id = request.form.get('job_id')
        cur = mysql.connection.cursor()
        # Calculate the total cost from job_part
        cur.execute("""
            SELECT IFNULL(SUM(part.cost * job_part.qty), 0) AS part_total
            FROM job_part
            JOIN part ON job_part.part_id = part.part_id
            WHERE job_part.job_id = %s
        """, (job_id,))
        part_total = cur.fetchone()[0]
        # Calculate the total cost from job_service
        cur.execute("""
            SELECT IFNULL(SUM(service.cost * job_service.qty), 0) AS service_total
            FROM job_service
            JOIN service ON job_service.service_id = service.service_id
            WHERE job_service.job_id = %s
        """, (job_id,))
        service_total = cur.fetchone()[0]

        # Calculate the overall total cost
        total_cost = part_total + service_total
        # Update the total cost in the job table
        cur.execute("UPDATE job SET total_cost = %s, completed=1 WHERE job_id = %s", (total_cost, job_id))
        mysql.connection.commit()
        return redirect('/')
    
    except Exception as e:
        # Log the error and return an error response
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to add complete"}), 500


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
            # Handle the case where search_term is None
    search_term = request.form.get('search_term')
    if search_term is None:
        search_term = ''
    
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
        print(results)
        print(search_term)
        # Close the cursor
        cur.close()

        # Return a JSON response
        return render_template('admin/customer_search.html', customer_details=results,search_term =search_term)

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})


@app.route('/admin/add_customer')
def admin_add_customer():
    return render_template('admin/add_customer.html')

@app.route('/add_customer', methods=['POST'])
def add_customer():
    try:
        first_name = request.form.get('first_name')
        family_name = request.form.get('family_name')
        email = request.form.get('email')
        phonenumber = request.form.get('phone')
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
        return render_template('admin/add_customer.html')

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route('/admin/add_part')
def admin_add_part():
    return render_template('admin/add_part.html')
@app.route('/add_master_part', methods=['POST'])
def add_master_part():
    try:
        part_name =request.form.get('part_name')
        cost = request.form.get('cost')
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
        return render_template('admin/add_part.html')

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})


@app.route('/admin/add_service')
def admin_add_service():
    return render_template('admin/add_service.html')

@app.route('/add_master_service', methods=['POST'])
def add_master_service():
    try:
        service_name =request.form.get('service_name')
        cost = request.form.get('cost')
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
        return render_template('admin/add_service.html')

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
        today = datetime.date.today().strftime('%Y-%m-%d')
        customerSelect =request.form.get('customerSelect')
        bookingDate = request.form.get('bookingDate')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM job WHERE customer = %s AND job_date = %s", (customerSelect, bookingDate))
        existing_record = cur.fetchone()
        cur.execute("""SELECT *
            FROM customer ORDER BY family_name, first_name""")
        columns = [column[0] for column in cur.description]
        customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
        if existing_record:
            return jsonify({"data": "Already Exist", "isExist": True})
        else:
            # Insert a new record
            cur.execute("INSERT INTO job (customer, job_date) VALUES (%s, %s)", (customerSelect, bookingDate))

        cur.connection.commit() 

        # Return a JSON response
        return render_template('admin/schedule_jobs.html', customer_list=customer_list, today=today)

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})

@app.route('/admin/bills', methods=['POST', 'GET'])
def admin_bills():
    cur = mysql.connection.cursor()
    if request.method == 'GET' and request.args.get('customer') is not None :
        print('GET Method')
        customer_id = request.args.get('customer')
        cur.execute(""" 
            SELECT job.job_id, job.job_date, customer.first_name, job.total_cost,customer_id
            FROM job
            JOIN customer ON job.customer = customer.customer_id
            WHERE job.paid = 0 and customer.customer_id=%s; """, (customer_id))
        print(customer_id)
        
    else:
        print('Post Method')
        cur.execute("""
        SELECT job.job_id, job.job_date, customer.first_name, job.total_cost,customer_id
        FROM job
        JOIN customer ON job.customer = customer.customer_id
        WHERE job.paid = 0;
        """)
    columns = [column[0] for column in cur.description]
    customer_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.execute("""
        SELECT customer.first_name, customer_id
        FROM job
        JOIN customer ON job.customer = customer.customer_id
        WHERE job.paid = 0;
        """)
    columns = [column[0] for column in cur.description]
    customer_name = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('admin/bills.html',customer_details=customer_list, customer_name=customer_name)

@app.route('/paid', methods=['POST'])
def mark_paid():
    print(request.method)
    try:
        job_id = request.form.get('job_id')
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
        # Close the cursor
        cur.close()

        # Return a JSON response
        return jsonify({"data": results})

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred during the search."})


@app.route('/unpaid_bills_report')
def unpaid_bills_report():
    try:
        cur = mysql.connection.cursor()
        query = """
            SELECT
                customer.customer_id,
                customer.first_name,
                customer.family_name,
                job.job_date,
                job.total_cost,
                DATEDIFF(NOW(), job.job_date) AS days_since_job
            FROM
                customer
            JOIN
                job ON customer.customer_id = job.customer
            WHERE
                job.paid = 0
            ORDER BY
                customer.family_name,
                customer.first_name,
                days_since_job DESC;
        """
        cur.execute(query)
        columns = [column[0] for column in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]

        if not results:
            # Handle case when results is empty
            return render_template('admin/history.html', results=[])

        sorted_results = sorted(results, key=itemgetter('customer_id', 'job_date'))
        print(sorted_results)
        grouped_results = {key: list(group) for key, group in groupby(sorted_results, key=lambda x: x['customer_id'])}
        print(grouped_results)

        return render_template('admin/history.html', grouped_results=grouped_results)

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return render_template('admin/history.html', results=[])
    finally:
        cur.close()

if __name__ == '__main__':
    app.run(debug=True)