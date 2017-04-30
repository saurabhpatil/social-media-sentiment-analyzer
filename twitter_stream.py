__author__ = 'saurabh'

#Import the necessary methods from tweepy library
import tweepy, ETLOperations, json
from tweepy.streaming import StreamListener
from tweepy import Stream

dataCollection = None
tweetCount = 0


#   This class defines a basic listener catches extractions from the twitter stream
#   It overrides the StreamListener class of twitter API to implement data handling and error handling functionalities
class TweetListener(StreamListener):
    def on_data(self, data):
        global tweetCount, dataCollection
        print(data.decode('utf-8'))
        tweet = json.loads(data.decode('utf-8'))
        if not dataCollection.find_one({"text":tweet["text"]}):
            dataCollection.insert(tweet)
            print("Tweet Inserted!")
        tweetCount = tweetCount + 1
        if tweetCount == 10:
            tweetCount = 0
            return False

    def on_error(self, status):
        print("Error Occured "+str(status))


#   This function calls functions for database connection and twitter authentication
#   It establishes connection to live twitter data stream and extracts tweets matching the specific keyword
def extract_keyword_match_tweets(searchTerm):
    global dataCollection
    dataCollection = ETLOperations.DBConnection(searchTerm)

    api = ETLOperations.setupTwitterConnection()
    stream = Stream(auth = api.auth, listener = TweetListener())
    keywords = []
    keywords.append(searchTerm)
    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    stream.filter(track=keywords)