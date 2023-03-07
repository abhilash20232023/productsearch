from flask import Flask, render_template,request, jsonify
from flask_paginate import Pagination, get_page_parameter
from flask_caching import Cache
import pandas as pd
import json

app = Flask(__name__)
app.config["CACHE_TYPE"] = "SimpleCache" # better not use this type w. gunicorn
cache = Cache(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/products",methods=["POST","GET"])
def product():
    search = None
    if request.method == 'POST':
        if cache.get('wallmart_data') is None:
            data = pd.read_csv("product_walmart_data.csv")
            data = data[["Uniq Id","Product Name","List Price","Description","Category"]]
            cache.set("wallmart_data", data)
        else:
            data = cache.get("wallmart_data")
        if len(request.form.keys()) > 0:
            search = request.form['query']
        page = request.args.get(get_page_parameter(), type=int, default=1)
        if search is not None:
            data = data[data["Product Name"].str.lower().str.find(search) > 0 ]
        if len(data) > 0:
            pagination = Pagination(page=page, total=(len(data)//10) ,record_name='Products')
            start_page = (page - 1) * 10
            end_page = page * 10 if(len(data) > page * 10) else len(data)
            product_data = data[start_page:end_page]
            return jsonify({'htmlresponse': render_template("product.html",
                products=json.loads(product_data.to_json(orient='records')),
                pagination=pagination)})
        else:
            pagination = Pagination(page=0, total=0 ,record_name='Products')
            return jsonify({'htmlresponse': render_template("product.html",
                products=[],
                pagination=pagination)})