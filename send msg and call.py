from flask import Flask, request, render_template, jsonify
import smtplib
import os
from twilio.rest import Client
from langchain.agents import tool, initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI

app = Flask(__name__)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")



TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")  

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)



@tool
def send_sms(input: str):
    """
    Send an SMS. Format: 'to: +91xxxxxx; message: Hello!'
    """
    parts = input.split(";")
    to_number = parts[0].split("to:")[1].strip()
    message_body = parts[1].split("message:")[1].strip()

    try:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_NUMBER,
            to=to_number
        )
        return f"SMS sent successfully. SID: {message.sid}"
    except Exception as e:
        return f"Error: {str(e)}"
    
    
    
    
    
    
    
    
    




@tool
def make_call(input: str):
    """
    make an call. Format: 'to: +91xxxxxx; message: Hello!'

    """
    parts = input.split(";")
    to_number = parts[0].split("to:")[1].strip()
    message = parts[1].split("message:")[1].strip()
    try:
        call = client.calls.create(
            to=to_number,
            from_=TWILIO_NUMBER,
            twiml=f'<Response><Say voice="alice">{message}</Say></Response>'
        )
        return f"Call initiated successfully. SID: {call.sid}"
    except Exception as e:
        return f"Error: {str(e)}"












@app.route('/', methods=['GET', 'POST'])
def index():
    tools = [ make_call ,send_sms]
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )
    result = None
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            try:
                result = agent.run(query)
            except Exception as e:
                result = f"Error: {str(e)}"
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
