from flask import Flask, render_template, url_for, redirect, request
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
import pandas as pd
import extract
import target
import gzip
from cs50 import SQL
import csv
from geo import open_gds

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename


extract.get_important_data()
# import sql ---> Uncomment if tranfac.db not present


# create a flask application object
def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    FontAwesome(app)
    app.config['SECRET_KEY'] = 'change this unsecure key'

    return app
app = create_app()
# we need to set a secret key attribute for secure forms

class QueryForm(FlaskForm):
    submit = SubmitField()


@app.route('/')
def index():
    return render_template('index.html')

# define the action for the top level route
@app.route('/search', methods=['GET','POST'])
def search():
    form = QueryForm()
    htf_name = None

    if request.method == 'POST':
        htf_name = request.form.get('keywords')
        category_type = request.form.get('category')
        if category_type == 'tf':
            return redirect(url_for('tfprofile', htf_name = htf_name))
        elif category_type == 'gene':
            return 'gene'
        elif category_type == 'drug':
            return 'drug'
    return render_template('searchpage.html', form=form)

@app.route('/tfprofile/<htf_name>', methods=['GET'])
def tfprofile(htf_name):

    symbs = extract.get_symbols()

    if htf_name in symbs:
        db = SQL("sqlite:///tranfac.db")

        user_inp = db.execute("SELECT * FROM HtfUniprot JOIN HtfLocation ON HtfUniprot.Uniprot = HtfLocation.Uniprot WHERE HtfUniprot.Symbol = ? ", htf_name)

        for num in range(len(user_inp)):
            ensembl = user_inp[num]['Ensembl']
            chr = user_inp[num]['Chromosome']
            full_name = user_inp[num]['Protein_name'].title()
            uniprot = user_inp[num]['Uniprot']
            subcell = user_inp[num]['Subcellular_location']
            func = user_inp[num]['Functions']
            symbol = user_inp[num]['Symbol']
            family = user_inp[num]['Family']
            break
        # symbol = data[htf_name]['Symbol']
        # family = data[htf_name]['Family']
        # chr = data[htf_name]['Chr_loc']
        # full_name = data[htf_name]['Full_Name']
        # uniprot = data[htf_name]['Uniprot']
        # subcell = data[htf_name]['Subcell']
        # func = data[htf_name]['Func']
        targets = target.get_htf_target_data(htf_name)

        return render_template('tfprofile.html', symbol= symbol, ensembl=ensembl, family=family,chr=chr, full_name=full_name, uniprot=uniprot,
        subcell=subcell, func=func ,targets=targets)
    else:
        return redirect(url_for('error', htf_name = None))

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/geo',methods=['GET','POST'])
def geo():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        a = open_gds(f.filename)
        print(a)
    return render_template('GEO.html')

@app.route('/drugprofile')
def drugs():
    return render_template('drugprofile.html')

# @app.route('/browse/drugs/<htf_name>')
# def drugs():

#     return render_template('drugprofile.html')


# start the web server
if __name__ == '__main__':
    app.run(debug=True)
