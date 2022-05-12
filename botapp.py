from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
import os
import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


def chain_messages(start , *fun):
    res = start
    for fun in funs:
        res = fun(res)
    return res

@app.route("/")
def hello():
    return "Hello, world!!!!"

@app.route("/sms", methods=['POST'])  #dynamic routing
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    print(request)
    msg = request.form.get('Body')
    
    msg = msg.upper()
    
    if 'HI' in msg or 'HEY' in msg or 'HELLO' in msg or 'MENU' in msg:
        resp = MessagingResponse()
        resp.message("👋🏻 Welcome to MyDoc, a directory of doctors on WhatsApp! 🏥 I'm Laura, your virtual assistant! I'll help you find a local GP. To get started, please enter your postcode.")
        return str(resp)
    
    elif '0' in msg or '1' in msg or '2' in msg or '3' in msg or '4' in msg or '5' in msg or '6' in msg or '7' in msg or '8' in msg or '9' in msg:
        #creds for your local postgres
        DATABASE_URL = os.environ['DATABASE_URL']

        #So that 'finally closing' bit has some input even if a connection wasn't opened
        db_conn = None
        db_cursor = None

        try:  #THIS BIT DOES NOT WORK- GOES TO EXCEPT-WORKS FROM THERE
            db_conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            db_cursor = db_conn.cursor()
            #sql script is executed-
            #make table of gps, contact etc. if it does not exist already

            query = str(format(msg)).replace(" ", "") #this needs to be a str, replace func removes any spaces if they exist 

            db_cursor.execute('SELECT gp1, gp2, gp3 FROM gps_list u WHERE u.postcode = %s;', [query,])

            records = db_cursor.fetchone()
            gp1 = records[0]
            gp2 = records[1]
            gp3 = records[2]

             #Commit
            db_conn.commit()
               # Create reply
            resp = MessagingResponse()
            response = chain_messages(
                resp.message("🧐 I found these GPs near you") ,
                 resp.message(gp1) ,
                  resp.message(gp2) ,
                    resp.message(gp3) ,
                      resp.message("Which of these surgeries would you like to book an appointment with?")
            )

            return str(response)

        except Exception as error:
            # Create reply
            resp = MessagingResponse()
            resp.message("Error: {}".format(error))
            resp.message("Sorry, I didn't understand. If you are looking for local GPs, please send us your postcode. FYI, we only work for London at the moment!")

            return str(resp)

        finally:
        
            if db_cursor is not None:
                #Closing the cursor only if it was opene
                db_cursor.close()
                #Close the connection only if it was opened
                db_conn.close()
                

    else:
        resp = MessagingResponse()
        resp.message("No problem- book through https://calendly.com/mydocemail306/15-minute-meeting")
        return str(resp)

if __name__ == "__main__":
    print('running')
    app.run(debug=True)