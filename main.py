__author__ = 'saurabh'

import webbrowser, ETLOperations, TwitterStream, ExcelReport

from flask import Flask, render_template, request

app = Flask(__name__)

#   Setup the html file to be rendered at a specific route
#   Handle the button click events and make the appropriate function calls based on button used
@app.route('/', methods = ['GET', 'POST'])
def renderHome():
    barGraph = {}
    keyword = ""
    tweets = []
    if request.method == 'POST':
        keyword = request.form['searchKeyword']
        if keyword != "" and request.form['submit'] == 'Search':
            if request.form['searchType'] == "profileSearch":
                ETLOperations.getProfileTweets(keyword.lower())
            elif request.form['searchType'] == "matchSearch":
                TwitterStream.extractKeywordMatchTweets(keyword.lower())
            barGraph, tweets = createBarGraph(keyword.lower())
        elif request.form['submit'] == 'Analytics':
            ExcelReport.displayExcel(keyword.lower())
        elif request.form['submit'] == 'Cancel':
            keyword = ""
    return render_template('homepage.html', barGraph = barGraph, tweets = tweets, keyword=keyword)


#   Plot charts of analysis using HighCharts
def createBarGraph(searchTerm):
    barGraph = {}
    positive,negative,neutral,tweets = ETLOperations.AnalyzeSentiment(searchTerm)
    barGraph["chartID"] = "barchart"
    barGraph["chart"] = {"renderTo": "barchart", "type": "bar", "backgroundColor": '#CDE3F5'}
    barGraph["series"] = [{"name": 'Number Of Tweets', "data": [positive, neutral, negative]}]
    barGraph["title"] = {"text": 'Twitter Analytics Graph'}
    barGraph["xAxis"] = {"categories": ['Positive', 'Neutral', 'Negative']}
    barGraph["yAxis"] = {"title": {"text": 'Tweets'}}
    return barGraph, tweets


if __name__ == '__main__':
    webbrowser.open("http://localhost:5000/")
    app.run(debug = True, port=5000)