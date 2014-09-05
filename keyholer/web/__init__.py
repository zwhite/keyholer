from flask import Flask, render_template, request

from keyholer.client import KeyholerClient


app = Flask(__name__)
keyholer = KeyholerClient()


@app.route('/', methods=['GET'])
def GET_root():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def POST_login():
    username = request.form.get('username', None)

    if username:
        keyholer.login(username)

    return render_template('verify.html', username=username)


@app.route('/verify', methods=['POST'])
def POST_verify():
    code = request.form.get('code', None)
    username = request.form.get('username', None)

    if code and username:
        result = keyholer.verify(username, code).split('\n')
        ssh_keys = []

        if len(result) > 1:
            ssh_keys = result[1:]

        if result[0] == 'True':
            return render_template('keys.html', code=code, username=username,
                                   ssh_keys=ssh_keys)

    return render_template('sad.html')


@app.route('/add_key', methods=['POST'])
def POST_add_key():
    code = request.form.get('code', None)
    username = request.form.get('username', None)
    ssh_key = request.form.get('ssh_key', None)

    if code and username and ssh_key:
        if keyholer.add_key(username, code, ssh_key) == 'True':
            return render_template('happy.html')

    return render_template('sad.html')
