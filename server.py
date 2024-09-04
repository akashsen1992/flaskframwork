from flask import Flask, jsonify, request
import mysql.connector
import sendgrid
import os
from sendgrid import SendGridAPIClient


from sendgrid.helpers.mail import Mail, Email, To, Content
sg_api_key = os.environ.get(
    "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")

app = Flask(__name__)
SENDGRENDPROINT = "https://api.sendgrid.com/v3/mail/send"


def create_server_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root1',
            password='12345',
            database='practise'
        )
        print("MySQL Database connection successful")
    except mysql.connector.Error as err: 
        print(f"Error: {err}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    return connection


# Define the root route
@app.route("/", methods=['GET'])
def welcome():

    return "Welcome to Akash Sen"

# Define the /getuser route
@app.route("/getuser", methods=['GET'])
def get_user():
    connection = create_server_connection()
    username=request.args.get('username')
    # print(username,"username")
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(users)    

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        fullname = data.get('fullname')
        password = data.get('password')
        
        connection = create_server_connection()
        cursor = connection.cursor(dictionary=True)
        
        insert_query = "INSERT INTO users (username, fullname, email, password) VALUES (%s, %s, %s, %s)"

        # Data values to insert
        data_values = (username, fullname, email, password)  # Replace with actual values

        # Execute the Query
        cursor.execute(insert_query, data_values)
        
        connection.commit()  # Commit the transaction
        
        cursor.close()
        connection.close()
        
        return "Data inserted successfully"
    
    except Exception as e:
        return "Error: " + str(e)

    


@app.route('/sendemail', methods=['POST'])
def send_email():
    # Set your SendGrid API key
    # sg_api_key = os.environ.get("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")  # Corrected API key
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get(
        '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'))

    # Parse request data
    data = request.get_json()

    # Extract email content from request data
    sender_email = data.get('sender_email')
    recipient_email = data.get('recipient_email')
    subject = data.get('subject')
    message = data.get('message')

    # Create Mail object
    email = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject=subject,
        html_content=message
    )

    from_email = Email("hello@onetab.ai")  # Change to your verified sender
    to_email = To("akash@linkites.com")  # Change to your recipient
    subject = "Sending with SendGrid is Fun"
    content = Content(
        "text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

# Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)


@app.route('/addproduct', methods=['POST'])
def addproduct():
    try:
        data = request.json
        connection = create_server_connection()

        Product_name = data.get('Product_name')
        Supplier_id = data.get('Supplier_id')
        price = data.get('price')

        cursor = connection.cursor(dictionary=True)

        insert_query = "INSERT INTO Product (Product_name, Supplier_id, price) VALUES (%s, %s, %s)"

        # Data values to insert
        data_values = (Product_name, Supplier_id, price)

        # Execute the Query
        cursor.execute(insert_query, data_values)
        connection.commit()  # Commit the transaction

        cursor.close()
        connection.close()

        return "Data inserted successfully"
    except Exception as e:
        return str(e)

@app.route('/productby_supplier', methods=['GET'])
def get_products():
    # Get supplier name parameter from query string
    supplier_name = request.args.get('supplier_name')

    # Establish database connection
    connection = create_server_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Execute SQL query with parameterized query
        cursor.execute(
            "SELECT * FROM Product AS pd JOIN supplier AS sp ON pd.Supplier_id=sp.Supplier_id WHERE Supplier_name = %s", (supplier_name,))
        products = cursor.fetchall()

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Return products as JSON response
        return jsonify(products)

    except Exception as e:
        # Handle errors, you may want to return an error response here
        print(f"Error: '{e}'")
        cursor.close()
        connection.close()
        return jsonify({"error": "An error occurred while fetching products"}), 500


# Check if the script is executed directly (i.e., not imported)
if __name__ == '__main__':
    # Run the Flask application on port 7000 with debug mode enabled
    app.run(debug=True, port=5000)
