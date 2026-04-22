from flask import Flask, render_template, request, jsonify
import pandas as pd
from rapidfuzz import fuzz, process

app = Flask(__name__)
df = pd.read_csv('data/predictive_maintenance.csv')

# Simple in-memory session context (In a real app, use Flask sessions or a DB)
SESSION_CONTEXT = {
    'last_machine_id': None
}

def calculate_risk_status(machine):
    """Calculates a machine's health status based on sensor thresholds."""
    if machine['Target'] == 1:
        return "Critical (Failed)"
    
    # Heuristic risk scoring
    risk_points = 0
    if machine['Tool wear [min]'] > 200: risk_points += 2
    elif machine['Tool wear [min]'] > 150: risk_points += 1
    
    if machine['Air temperature [K]'] > 300: risk_points += 1
    if machine['Torque [Nm]'] > 60: risk_points += 1
    
    if risk_points >= 3: return "High Warning"
    if risk_points >= 1: return "Elevated"
    return "Safe"

# ============================================================
# Define all available commands with keywords for fuzzy matching
# ============================================================
COMMANDS = {
    'help': ['help', 'commands', 'what can you do', 'options', 'available commands'],
    'hello': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good evening'],
    'status': ['status', 'machine status', 'overall status', 'system status'],
    'all machines': ['all machines', 'total machines', 'how many machines', 'machine count', 'count machines'],
    'failed machines': ['failed machines', 'failures', 'broken machines', 'faulty machines', 'defective machines', 'not working machines'],
    'working machines': ['working machines', 'operational machines', 'active machines', 'running machines', 'good machines', 'healthy machines'],
    'power failure': ['power failure', 'power fail', 'power failures', 'power issue', 'power problem', 'electricity failure'],
    'tool wear': ['tool wear', 'high tool wear', 'wear and tear', 'tool wear failure', 'worn tools'],
    'heat dissipation': ['heat dissipation', 'heat failure', 'heat dissipation failure', 'overheating', 'heat problem', 'temperature failure'],
    'overstrain': ['overstrain', 'overstrain failure', 'strain failure', 'over strain', 'mechanical strain'],
    'random failure': ['random failure', 'random failures', 'random fail', 'unexpected failure'],
    'summary': ['summary', 'statistics', 'stats', 'overview', 'report', 'show summary', 'data summary'],
    'failure types': ['failure types', 'types of failure', 'failure categories', 'failure breakdown', 'failure distribution'],
    'machine types': ['machine types', 'types of machines', 'machine categories', 'quality types', 'machine quality'],
    'avg temperature': ['average temperature', 'avg temperature', 'mean temperature', 'temperature average', 'temp average', 'air temperature'],
    'process temperature': ['process temperature', 'process temp', 'avg process temperature', 'average process temperature'],
    'avg rpm': ['average rpm', 'avg rpm', 'mean rpm', 'rotational speed', 'rotation speed', 'speed average'],
    'avg torque': ['average torque', 'avg torque', 'mean torque', 'torque average', 'torque value'],
    'avg tool wear': ['average tool wear', 'avg tool wear', 'mean tool wear', 'tool wear average'],
    'max tool wear': ['max tool wear', 'maximum tool wear', 'highest tool wear', 'most worn'],
    'min tool wear': ['min tool wear', 'minimum tool wear', 'lowest tool wear', 'least worn'],
    'high quality': ['high quality', 'type h', 'h type', 'high type machines', 'premium machines'],
    'medium quality': ['medium quality', 'type m', 'm type', 'medium type machines', 'mid quality'],
    'low quality': ['low quality', 'type l', 'l type', 'low type machines', 'basic machines'],
    'failure rate': ['failure rate', 'fail rate', 'failure percentage', 'fail percentage', 'defect rate'],
    'no failure': ['no failure', 'no failures', 'machines without failure', 'zero failure', 'safe machines'],
    'high rpm': ['high rpm', 'fast machines', 'high speed machines', 'high rotational speed'],
    'low rpm': ['low rpm', 'slow machines', 'low speed machines', 'low rotational speed'],
    'high torque': ['high torque', 'heavy torque', 'strong torque', 'maximum torque machines'],
    'low torque': ['low torque', 'light torque', 'weak torque', 'minimum torque machines'],
    'high temperature': ['high temperature', 'hot machines', 'overheated', 'above average temperature'],
    'product id': ['product id', 'search product', 'find product', 'product search', 'search machine'],
}

def find_best_command(query):
    """Use fuzzy matching to find the best matching command."""
    all_keywords = []
    keyword_to_command = {}
    
    for command, keywords in COMMANDS.items():
        for keyword in keywords:
            all_keywords.append(keyword)
            keyword_to_command[keyword] = command
    
    # Find the best match using rapidfuzz
    result = process.extractOne(query, all_keywords, scorer=fuzz.token_sort_ratio)
    
    if result and result[1] >= 55:  # 55% threshold
        matched_keyword = result[0]
        return keyword_to_command[matched_keyword], result[1]
    
    return None, 0

def get_response(query):
    query = query.lower().strip()
    
    # Try to find best matching command using fuzzy matching
    command, score = find_best_command(query)
    
    if command is None:
        # Check if it looks like a product ID search
        words = query.split()
        for word in words:
            word_upper = word.upper()
            if word_upper in df['Product ID'].values:
                machine = df[df['Product ID'] == word_upper].iloc[0]
                SESSION_CONTEXT['last_machine_id'] = word_upper
                status = '🔴 Failed' if machine['Target'] == 1 else '🟢 Working'
                risk = calculate_risk_status(machine)
                
                return (f"📡 <b>Machine {word_upper} Details:</b><br>"
                        f"• Type: {machine['Type']} | Status: {status}<br>"
                        f"• <b>Risk Status: {risk}</b><br>"
                        f"• Air Temp: {machine['Air temperature [K]']}K | Process Temp: {machine['Process temperature [K]']}K<br>"
                        f"• RPM: {machine['Rotational speed [rpm]']} | Torque: {machine['Torque [Nm]']}Nm<br>"
                        f"• Tool Wear: {machine['Tool wear [min]']}min | Failure: {machine['Failure Type']}")

        # Contextual follow-up logic
        if SESSION_CONTEXT['last_machine_id']:
            mid = SESSION_CONTEXT['last_machine_id']
            machine = df[df['Product ID'] == mid].iloc[0]
            
            if any(k in query for k in ['temp', 'heat', 'hot', 'temperature']):
                return f"🌡️ The air temperature for machine <b>{mid}</b> is {machine['Air temperature [K]']}K and process temperature is {machine['Process temperature [K]']}K."
            if any(k in query for k in ['rpm', 'speed', 'fast']):
                return f"⚡ Machine <b>{mid}</b> is running at {machine['Rotational speed [rpm]']} RPM."
            if any(k in query for k in ['wear', 'tool']):
                return f"🔧 Current tool wear for machine <b>{mid}</b> is {machine['Tool wear [min]']} minutes."
            if any(k in query for k in ['risk', 'health', 'condition']):
                risk = calculate_risk_status(machine)
                return f"🛡️ The health status for machine <b>{mid}</b> is currently: <b>{risk}</b>."
        
        return "Sorry, I didn't understand that. Type 'help' to see available commands."
    
    # Process the matched command
    if command == 'help':
        return ("Available commands:\n"
                "• show all machines / total machines\n"
                "• show failed machines / working machines\n"
                "• show status / summary / statistics\n"
                "• show failure types / failure rate\n"
                "• show power failure / heat dissipation / overstrain / tool wear / random failure\n"
                "• show machine types / high quality / medium quality / low quality\n"
                "• avg temperature / process temperature / avg rpm / avg torque\n"
                "• avg tool wear / max tool wear / min tool wear\n"
                "• high rpm / low rpm / high torque / low torque / high temperature\n"
                "• search product ID (e.g., 'L47181')\n"
                "• hello / help")
    
    elif command == 'hello':
        return "Hello! Welcome to InfraChat 🤖 Type 'help' to see all available commands."
    
    elif command == 'status':
        total = len(df)
        failed = len(df[df['Target'] == 1])
        working = len(df[df['Target'] == 0])
        rate = round((failed / total) * 100, 2)
        return f"Machine Status:\nTotal: {total} | Working: {working} | Failed: {failed} | Failure Rate: {rate}%"
    
    elif command == 'all machines':
        return f"Total machines in dataset: {len(df)}"
    
    elif command == 'failed machines':
        failed = df[df['Target'] == 1]
        return f"Total failed machines: {len(failed)}"
    
    elif command == 'working machines':
        working = df[df['Target'] == 0]
        return f"Total working machines: {len(working)}"
    
    elif command == 'power failure':
        power = df[df['Failure Type'] == 'Power Failure']
        return f"Machines with Power Failure: {len(power)}"
    
    elif command == 'heat dissipation':
        heat = df[df['Failure Type'] == 'Heat Dissipation Failure']
        return f"Machines with Heat Dissipation Failure: {len(heat)}"
    
    elif command == 'overstrain':
        overstrain = df[df['Failure Type'] == 'Overstrain Failure']
        return f"Machines with Overstrain Failure: {len(overstrain)}"
    
    elif command == 'random failure':
        random_f = df[df['Failure Type'] == 'Random Failures']
        return f"Machines with Random Failures: {len(random_f)}"
    
    elif command == 'tool wear':
        tool_wear_f = df[df['Failure Type'] == 'Tool Wear Failure']
        high_wear = df[df['Tool wear [min]'] > 200]
        return (f"Tool Wear Failure machines: {len(tool_wear_f)}\n"
                f"Machines with tool wear above 200 min: {len(high_wear)}")
    
    elif command == 'summary':
        total = len(df)
        failed = len(df[df['Target'] == 1])
        working = len(df[df['Target'] == 0])
        rate = round((failed / total) * 100, 2)
        avg_temp = round(df['Air temperature [K]'].mean(), 1)
        avg_rpm = round(df['Rotational speed [rpm]'].mean(), 0)
        avg_torque = round(df['Torque [Nm]'].mean(), 1)
        avg_wear = round(df['Tool wear [min]'].mean(), 1)
        return (f"Dataset Summary:\n"
                f"Total: {total} | Working: {working} | Failed: {failed}\n"
                f"Failure Rate: {rate}%\n"
                f"Avg Air Temp: {avg_temp}K | Avg RPM: {int(avg_rpm)}\n"
                f"Avg Torque: {avg_torque}Nm | Avg Tool Wear: {avg_wear}min")
    
    elif command == 'failure types':
        failures = df[df['Failure Type'] != 'No Failure']['Failure Type'].value_counts()
        result = "Failure Type Distribution:\n"
        for ftype, count in failures.items():
            result += f"• {ftype}: {count}\n"
        return result.strip()
    
    elif command == 'machine types':
        types = df['Type'].value_counts()
        result = "Machine Quality Types:\n"
        for mtype, count in types.items():
            label = {'L': 'Low', 'M': 'Medium', 'H': 'High'}.get(mtype, mtype)
            result += f"• {mtype} ({label}): {count}\n"
        return result.strip()
    
    elif command == 'avg temperature':
        avg = round(df['Air temperature [K]'].mean(), 2)
        min_t = round(df['Air temperature [K]'].min(), 2)
        max_t = round(df['Air temperature [K]'].max(), 2)
        return f"Air Temperature:\nAverage: {avg}K | Min: {min_t}K | Max: {max_t}K"
    
    elif command == 'process temperature':
        avg = round(df['Process temperature [K]'].mean(), 2)
        min_t = round(df['Process temperature [K]'].min(), 2)
        max_t = round(df['Process temperature [K]'].max(), 2)
        return f"Process Temperature:\nAverage: {avg}K | Min: {min_t}K | Max: {max_t}K"
    
    elif command == 'avg rpm':
        avg = round(df['Rotational speed [rpm]'].mean(), 0)
        min_r = df['Rotational speed [rpm]'].min()
        max_r = df['Rotational speed [rpm]'].max()
        return f"Rotational Speed:\nAverage: {int(avg)} RPM | Min: {min_r} RPM | Max: {max_r} RPM"
    
    elif command == 'avg torque':
        avg = round(df['Torque [Nm]'].mean(), 2)
        min_t = round(df['Torque [Nm]'].min(), 2)
        max_t = round(df['Torque [Nm]'].max(), 2)
        return f"Torque:\nAverage: {avg} Nm | Min: {min_t} Nm | Max: {max_t} Nm"
    
    elif command == 'avg tool wear':
        avg = round(df['Tool wear [min]'].mean(), 1)
        return f"Average tool wear: {avg} minutes"
    
    elif command == 'max tool wear':
        max_w = df['Tool wear [min]'].max()
        machine = df[df['Tool wear [min]'] == max_w].iloc[0]
        return f"Maximum tool wear: {max_w} min\nMachine: {machine['Product ID']} (Type: {machine['Type']})"
    
    elif command == 'min tool wear':
        min_w = df['Tool wear [min]'].min()
        return f"Minimum tool wear: {min_w} minutes"
    
    elif command == 'high quality':
        h = df[df['Type'] == 'H']
        failed_h = len(h[h['Target'] == 1])
        return f"High Quality (Type H) machines: {len(h)}\nFailed: {failed_h} | Working: {len(h) - failed_h}"
    
    elif command == 'medium quality':
        m = df[df['Type'] == 'M']
        failed_m = len(m[m['Target'] == 1])
        return f"Medium Quality (Type M) machines: {len(m)}\nFailed: {failed_m} | Working: {len(m) - failed_m}"
    
    elif command == 'low quality':
        l = df[df['Type'] == 'L']
        failed_l = len(l[l['Target'] == 1])
        return f"Low Quality (Type L) machines: {len(l)}\nFailed: {failed_l} | Working: {len(l) - failed_l}"
    
    elif command == 'failure rate':
        total = len(df)
        failed = len(df[df['Target'] == 1])
        rate = round((failed / total) * 100, 2)
        return f"Overall failure rate: {rate}% ({failed} out of {total})"
    
    elif command == 'no failure':
        no_fail = df[df['Failure Type'] == 'No Failure']
        return f"Machines with no failure: {len(no_fail)}"
    
    elif command == 'high rpm':
        avg_rpm = df['Rotational speed [rpm]'].mean()
        high = df[df['Rotational speed [rpm]'] > avg_rpm]
        return f"Machines with above average RPM (>{int(avg_rpm)}): {len(high)}"
    
    elif command == 'low rpm':
        avg_rpm = df['Rotational speed [rpm]'].mean()
        low = df[df['Rotational speed [rpm]'] < avg_rpm]
        return f"Machines with below average RPM (<{int(avg_rpm)}): {len(low)}"
    
    elif command == 'high torque':
        avg_torque = df['Torque [Nm]'].mean()
        high = df[df['Torque [Nm]'] > avg_torque]
        return f"Machines with above average torque (>{round(avg_torque, 1)}Nm): {len(high)}"
    
    elif command == 'low torque':
        avg_torque = df['Torque [Nm]'].mean()
        low = df[df['Torque [Nm]'] < avg_torque]
        return f"Machines with below average torque (<{round(avg_torque, 1)}Nm): {len(low)}"
    
    elif command == 'high temperature':
        avg_temp = df['Air temperature [K]'].mean()
        high = df[df['Air temperature [K]'] > avg_temp]
        return f"Machines with above average air temp (>{round(avg_temp, 1)}K): {len(high)}"
    
    elif command == 'product id':
        return "To search a specific machine, type the Product ID directly. Example: L47181 or M14860"
    
    else:
        return "Sorry, I didn't understand that. Type 'help' to see available commands."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/dashboard-data')
def dashboard_data():
    total = len(df)
    failed = int(df['Target'].sum())
    working = total - failed

    failure_counts = df[df['Failure Type'] != 'No Failure']['Failure Type'].value_counts()
    failure_types = {
        'labels': failure_counts.index.tolist(),
        'values': failure_counts.values.tolist()
    }

    type_counts = df['Type'].value_counts()
    machine_types = {
        'labels': type_counts.index.tolist(),
        'values': type_counts.values.tolist()
    }

    bins = [0, 50, 100, 150, 200, 250, 300]
    labels_tw = ['0-50', '51-100', '101-150', '151-200', '201-250', '250+']
    df['Wear Bin'] = pd.cut(df['Tool wear [min]'], bins=bins, labels=labels_tw, right=True)
    wear_dist = df['Wear Bin'].value_counts().sort_index()
    tool_wear = {
        'labels': wear_dist.index.tolist(),
        'values': wear_dist.values.tolist()
    }

    avg_air_temp = round(float(df['Air temperature [K]'].mean()), 1)
    avg_process_temp = round(float(df['Process temperature [K]'].mean()), 1)
    avg_rpm = round(float(df['Rotational speed [rpm]'].mean()), 0)
    avg_torque = round(float(df['Torque [Nm]'].mean()), 1)
    high_wear_count = int(len(df[df['Tool wear [min]'] > 200]))
    failure_rate = round((failed / total) * 100, 2)

    sample_cols = ['UDI', 'Product ID', 'Type', 'Air temperature [K]', 
                   'Process temperature [K]', 'Rotational speed [rpm]', 
                   'Torque [Nm]', 'Tool wear [min]', 'Target', 'Failure Type']
    
    # Calculate Risk Score for each machine in sample
    sample_df = df[sample_cols].head(50).copy()
    sample_df['Risk'] = sample_df.apply(calculate_risk_status, axis=1)
    sample = sample_df.to_dict(orient='records')

    # Get Top 5 Highest Risk Machines (Excluding failed ones)
    risk_priority = {'High Warning': 3, 'Elevated': 2, 'Safe': 1, 'Critical (Failed)': 0}
    df_copy = df.copy()
    df_copy['Risk'] = df_copy.apply(calculate_risk_status, axis=1)
    df_copy['Risk_Val'] = df_copy['Risk'].map(risk_priority)
    critical_machines = df_copy[df_copy['Target'] == 0].sort_values('Risk_Val', ascending=False).head(5)
    
    return jsonify({
        'total': total,
        'working': working,
        'failed': failed,
        'failure_rate': failure_rate,
        'high_wear_count': high_wear_count,
        'avg_air_temp': avg_air_temp,
        'avg_process_temp': avg_process_temp,
        'avg_rpm': avg_rpm,
        'avg_torque': avg_torque,
        'failure_types': failure_types,
        'machine_types': machine_types,
        'tool_wear': tool_wear,
        'sample_data': sample,
        'at_risk': critical_machines[sample_cols + ['Risk']].to_dict(orient='records')
    })

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message'].lower().strip()
    response = get_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
