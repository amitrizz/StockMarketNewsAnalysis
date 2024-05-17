# app.py

from flask import Flask, request, jsonify,render_template
import joblib
import yfinance as yf
from GoogleNews import GoogleNews
import requests
from datetime import datetime,timedelta

app = Flask(__name__)
# Load the model
loaded_model = joblib.load("model.pkl")
vector_model = joblib.load("countvector.pkl")

def get_stock_news(symbol):
    googlenews = GoogleNews()
    googlenews.search(symbol + " stock market news")
    result = googlenews.result()

    # Extract and return relevant information from the search results
    if result:
        # Example: Extracting headlines
        headlines = [item['title'] for item in result]
        return headlines
    else:
        return "No news found."


   
@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/stock',methods=['POST'])
def post_example():

    stockname = request.form.get('stock')
    stockname=stockname.lower()
    
    # Get the current date
    current_date = datetime.now()
    two_days_ago = current_date - timedelta(days=2)
    # Format the current date as "YYYY-MM-DD"
    formatted_date = two_days_ago.strftime("%Y-%m-%d")
    print(formatted_date)

    url = (f'https://newsapi.org/v2/everything?q={stockname}&from={formatted_date}&sortBy=popularity&apiKey=cc7dae6dff8740de8cbede1bd0a71a4e')

    response = requests.get(url).json()
    stockname=stockname.capitalize()
    # print(response)

    
    list_of_objects = []
    test_data=[]
    for row in response['articles']:
        title=row['title']
        # print(row)
        if title != "[Removed]" and stockname in title:
            obj = {
               "title": title,
               "date": row['publishedAt']
            }
            
            list_of_objects.append(obj)
  
    list_of_objects=sorted(list_of_objects, key=lambda x: x['date'], reverse=True)
    val=False
    if len(list_of_objects)>0:
        obj=list_of_objects[0]
        title=obj['title']
        test_data.append(title)
        test_data_transformed = vector_model.transform(test_data)
        # # Sample sentence for testing
        predictions = loaded_model.predict(test_data_transformed)
        print(predictions)
        if predictions[0]==1:
            val=True
        return render_template('stock.html',stockname=stockname,list_of_objects=list_of_objects,val=val)
    else:
         return render_template('error.html',stockname=stockname)
    

if __name__ == '__main__':
    app.run(debug=True)
