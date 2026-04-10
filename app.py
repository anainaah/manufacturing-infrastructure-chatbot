from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)
df = pd.read_csv('data/predictive_maintenance.csv')

def get_response(query):
    query = query.lower().strip()

    if query == 'help':
        return 'Available commands: show all machines, show failed machines, show working machines, show power failure, show tool wear, show summary, hello'
    
    elif 'hello' in query or query == 'hi':
        return 'Hello! Welcome to Manufacturing Infrastructure Chatbot. Type help to see available commands.'
    
    elif 'status' in query:
        total = len(df)
        failed = len(df[df['Target'] == 1])
        working = len(df[df['Target'] == 0])
        return f'Machine Status - Total: {total} | Working: {working} | Failed: {failed}'
    
    elif 'all machines' in query or 'all machine' in query:
        return f'Total machines in dataset: {len(df)}'
    
    elif 'failed machines' in query or 'failed machine' in query:
        failed = df[df['Target'] == 1]
        return f'Total failed machines: {len(failed)}'
    
    elif 'working machines' in query or 'working machine' in query:
        working = df[df['Target'] == 0]
        return f'Total working machines: {len(working)}'
    
    elif 'power failure' in query or 'power fail' in query:
        power = df[df['Failure Type'] == 'Power Failure']
        return f'Total power failure machines: {len(power)}'
    
    elif 'tool wear' in query or 'tool war' in query:
        high_wear = df[df['Tool wear [min]'] > 200]
        return f'Machines with high tool wear above 200 mins: {len(high_wear)}'
    
    elif 'summary' in query or 'statistics' in query:
        total = len(df)
        failed = len(df[df['Target'] == 1])
        working = len(df[df['Target'] == 0])
        return f'Total machines: {total} | Working: {working} | Failed: {failed}'
    
    else:
        return 'I dont understand. Type help to see available commands.'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message'].lower().strip()
    response = get_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)