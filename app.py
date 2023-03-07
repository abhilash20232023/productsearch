from flask import Flask, render_template,request, jsonify
from flask_paginate import Pagination, get_page_parameter
from flask_caching import Cache
import pandas as pd
import json

app = Flask(__name__)
app.config["CACHE_TYPE"] = "SimpleCache"
cache = Cache(app)

@app.route("/product/<p_id>",methods=["GET"])
def product_listing(p_id):
    data = cache_data(
            'wallmart_data',
            "product_walmart_data.csv",
            ["Uniq Id","Product Name","List Price","Description","Category"]
            )
    product_listing = data[data["Uniq Id"] == p_id]
    if len(product_listing) >0:
        return render_template('product_list.html', products= json.loads(product_listing.iloc[0].to_json()))


@app.route("/products",methods=["POST","GET"])
def product():
    search = None
    page = 1
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        # This is for caching the data
        data = cache_data(
            'wallmart_data',
            "product_walmart_data.csv",
            ["Uniq Id","Product Name","List Price","Description","Category"]
            )
        
        # parsing the arguments and assign to a variable
        arguments = parse_arguments(request.form)
        search, page = arguments['query'], arguments['page']

        # if search key present then search for the data
        data = search_function(search, data)

        if len(data) > 0:
            pagination = Pagination(page=page, total=(len(data)//10) ,record_name='Products')
            start_page = (page - 1) * 10
            end_page = page * 10 if(len(data) > page * 10) else len(data)
            product_data = data[start_page:end_page]
            return jsonify({'htmlresponse': render_template("product.html",
                products=json.loads(product_data.to_json(orient='records')),
                pagination=pagination)})
    
        pagination = Pagination(page=0, total=0 ,record_name='Products')
        return jsonify({'htmlresponse': render_template("product.html",
            products=[],
            pagination=pagination)})
        

"""
This function caches data and returns cached data

arguments:
    cache_key: str (key for caching data)
    file_name: str (name of the file for cahing)
    columns: [] (list of columns which are used for caching)
retuns:
    data: df (dataframe)
"""
def cache_data(cache_key, file_name, columns):
    if cache.get(cache_key) is None:
        data = pd.read_csv(file_name)
        data = data[columns]
        cache.set(cache_key, data)
    else:
        data = cache.get(cache_key)
    return data


"""
This function parses the arguments and return with default values

arguments:
    arguments: dict (dictionary of arguments)
retuns:
    default_args: dict (arguments with default values)
"""
def parse_arguments(arguments):
    default_args = {'query': None, 'page': 1}
    for key, value in arguments.items():
        if key == 'page':
            value = int(value)
        default_args[key] = value
    return default_args

"""
This function returns search results based on key it is normal find string in the key words

arguments:
    search: str
    data: dataframe ()
retuns:
    data: dataframe
"""
def search_function(search, data):
    if search is not None:
        data = data[data["Product Name"].str.lower().str.find(search) > 0 ]
    return data
