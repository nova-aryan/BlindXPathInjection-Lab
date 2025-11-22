from flask import Flask, request, render_template
from lxml import etree
import os

app = Flask(__name__)
DATAFILE = os.path.join(os.path.dirname(__file__), 'data', 'users.xml')

def load_xml():
    with open(DATAFILE, 'rb') as f:
        return etree.parse(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET','POST'])
def message():
    if request.method == 'POST':
        username = request.form.get('username','')
        msg = request.form.get('msg','')
        xml = load_xml()
        xpath_expr = f"/accounts/account[username='{username}']"
        try:
            res = xml.xpath(xpath_expr)
        except Exception as e:
            return render_template('message.html', error=str(e))
        if res:
            return render_template('message.html', success=True, msg=msg)
        else:
            return render_template('message.html', success=False)
    return render_template('message.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)