__author__ = 'saurabh'

import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream
from pymongo import MongoClient
from alchemyapi import AlchemyAPI

searchedKeyword = ""

#   This function helps setup connection to the twitter using the twitter API
#   Twitter requires a set of access and consumer keys to access its data
def setupTwitterConnection():
    try:
        consumer_key = 'Z83nGoWCVnZe86Fv4cOW8wOQ6'
        consumer_secret = '9QOG55JL8LyGpNxjDOjsIkwltTJ1LGywRIxNslNPm42ibXxxkl'
        access_token = '4259505552-caNdqwWkMwWF19OvQsmjEOXBrPPbYr2x9Bm04K9'
        access_token_secret = 'Zy5ITHtYAed8NesEATKjnE1HqmbYn8ciZLbA8L3AEmLlP'

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return tweepy.API(auth)
    except:
        print("Unable to establish connection to twitter API!!!\n")
        print("Please check internet connectivity")


#   This function establishes connection to mongoDB server
#   It creates/extracts the required collection based on the keyword being searched
def database_connection(searchTerm):
    try:
        connection = MongoClient('localhost', 27017)
        dbconn = connection.get_database('tweetsDB')
        if not dbconn.get_collection(searchTerm):
            dbconn.create_collection(searchTerm)
        return dbconn.get_collection(searchTerm)
    except:
        print("Unable to establish connection to mongoDB server")
        print("Please ensure that the mongoDB server is running on mongod process")


#   This function extracts the twitter feeds by searching the twitter for a specific profile matching the keyword
#   It  pulls out the 20 most recent tweets on the user page
def getProfileTweets(searchTerm):
    try:
        api = setupTwitterConnection()
        public_tweets = api.user_timeline(id = searchTerm)
        tweetsCollection = database_connection(searchTerm)

        for tweet in public_tweets:
            if not tweetsCollection.find_one({"text":tweet._json["text"]}):
                tweetsCollection.insert(tweet._json)
    except:
        print("Please enter a valid product name!")
#   This function analyzes the sentiments of a tweet by using the Alchemy API and
#   appends the sentiment data obtained to the tweet aggregate in mongoDB collection
def AnalyzeSentiment(searchTerm):
    analysisAPI = AlchemyAPI()
    pos, neg, neu = (0,0,0)
    dataCollection = database_connection(searchTerm)
    dataDocuments = dataCollection.find()
    tweets = []
    sentimentByCountry = {}
    tweetLocation = ""
    for document in dataDocuments:
        try:
            if document.get("sentiment", None) == None:
                analysisResponse = analysisAPI.sentiment("text", document["text"])
                documentSentiment = analysisResponse["docSentiment"]["type"]
                dataCollection.update_one({"_id":document["_id"]}, {"$set": {"sentiment": analysisResponse["docSentiment"]}})
            else:
                documentSentiment = document["sentiment"]["type"]

            if documentSentiment == "positive":
                pos=pos+1
            elif documentSentiment == "negative":
                neg=neg+1
            else:
                neu=neu+1

            tweets.append(document["text"].strip()+"\n\n***Tweet-Sentiment: "+documentSentiment+"***\n"+"-"*70)
        except:
            print("Unable to parse a Tweet as the language is not understood\n")
            dataCollection.delete_one({'text':document['text']})
    return pos,neg,neu,tweets