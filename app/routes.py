import os

import pandas as pd
from flask import render_template, request, redirect, url_for

from app import app
from app.util import check_expired, calc_rs_peaks, calc_w_and_heart_rate_pano
from typeguard import typechecked


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/')
def main():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/uploader', methods=['POST'])
def uploader():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'] + '/' + uploaded_file.filename)
            uploaded_file.save(filepath)
            try:
                data: pd.DataFrame = pd.read_csv(filepath, header=None)
                data = data[:-(len(data) % 1000)]
                data2: pd.Series = data[0]
                data3R: pd.Series = data[1]
                data6: pd.Series = data[2]
            except (FileNotFoundError, IndexError, UnicodeDecodeError):
                os.remove(filepath)
                return redirect(url_for(uploader))
            W, HRpano = calc_w_and_heart_rate_pano(calc_rs_peaks(data2), calc_rs_peaks(data6))
            os.remove(filepath)
            result = HRpano
        else:
            return redirect(url_for(uploader))
    return redirect(url_for('results', result=result, key=app.secret_key))


@app.route('/results/<result>/<key>')
@check_expired
@typechecked
def results(result, key):
    return render_template('results.html', results=float(result)*0.87)
