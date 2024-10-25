from flask import Flask, render_template_string, request, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess

app = Flask(__name__)
auth = HTTPBasicAuth()

# Define users and hashed passwords
users = {
    "admin": "hashedpassword"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# HTML template for rendering the web page
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>IPSet Manager</title>
</head>
<body>
    <h1>IPSet Manager</h1>
    <form method="get" action="/">
        <input type="text" name="search" placeholder="Search IP or List Name" value="{{ search }}">
        <input type="submit" value="Search">
    </form>
    <h2>IPSet Entries</h2>
    <table border="1">
        <tr>
            <th>List Name</th>
            <th>IP Address</th>
            <th>Details</th>
            <th>Action</th>
        </tr>
        {% for entry in entries %}
        <tr>
            <td>{{ entry['list_name'] }}</td>
            <td>{{ entry['ip_address'] }}</td>
            <td>{{ entry['details'] }}</td>
            <td>
                <form method="post" action="/delete" style="display:inline;">
                    <input type="hidden" name="list_name" value="{{ entry['list_name'] }}">
                    <input type="hidden" name="ip_address" value="{{ entry['ip_address'] }}">
                    <input type="submit" value="Delete">
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
    <h2>Add Entry</h2>
    <form method="post" action="/add">
        <input type="text" name="list_name" placeholder="List Name" required>
        <input type="text" name="ip_address" placeholder="IP Address" required>
        <input type="submit" value="Add">
    </form>
    <h2>Save/Restore List</h2>
    <form method="post" action="/save">
        <input type="submit" value="Save List">
    </form>
    <form method="post" action="/restore" enctype="multipart/form-data">
        <input type="file" name="file" accept=".ipset" required>
        <input type="submit" value="Restore List">
    </form>
</body>
</html>
'''

def get_ipset_entries():
    result = subprocess.run(['sudo', 'ipset', 'list', '-o', 'save'], stdout=subprocess.PIPE)
    lines = result.stdout.decode().splitlines()
    entries = []
    for line in lines:
        if line.startswith('create '):
            current_set = line.split()[1]
        elif line.startswith('add '):
            parts = line.split()
            if len(parts) >= 3:
                entry = {
                    'list_name': parts[1],
                    'ip_address': parts[2],
                    'details': ' '.join(parts[3:]) if len(parts) > 3 else ''
                }
                entries.append(entry)
    return entries

@app.route('/', methods=['GET'])
@auth.login_required
def index():
    search = request.args.get('search', '')
    entries = get_ipset_entries()
    if search:
        entries = [e for e in entries if search in e['ip_address'] or search in e['list_name']]
    return render_template_string(TEMPLATE, entries=entries, search=search)

@app.route('/delete', methods=['POST'])
@auth.login_required
def delete_entry():
    list_name = request.form['list_name']
    ip_address = request.form['ip_address']
    subprocess.run(['sudo', 'ipset', 'del', list_name, ip_address])
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
@auth.login_required
def add_entry():
    list_name = request.form['list_name']
    ip_address = request.form['ip_address']
    # Ensure the set exists
    subprocess.run(['sudo', 'ipset', 'create', list_name, 'hash:ip'], stderr=subprocess.DEVNULL)
    subprocess.run(['sudo', 'ipset', 'add', list_name, ip_address])
    return redirect(url_for('index'))

@app.route('/save', methods=['POST'])
@auth.login_required
def save_list():
    with open('ipset_backup.ipset', 'w') as f:
        subprocess.run(['sudo', 'ipset', 'save'], stdout=f)
    return redirect(url_for('index'))

@app.route('/restore', methods=['POST'])
@auth.login_required
def restore_list():
    file = request.files['file']
    if file:
        file.save('ipset_restore.ipset')
        subprocess.run(['sudo', 'ipset', 'restore'], stdin=open('ipset_restore.ipset', 'r'))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3300)

