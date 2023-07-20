import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

def spam_detection(text):
    df=pd.read_csv('data.csv')
    df['Category'] = df['Category'].map({'ham': 0, 'spam': 1})
    x = df["Message"]
    y=df["Category"]
    x_train,x_test,y_train,y_test = train_test_split(x , y, test_size=0.20,random_state=27)
    cv = CountVectorizer()
    x_train_count = cv.fit_transform(x_train.values)
    model = MultinomialNB()
    model.fit(x_train_count,y_train)
    texts=[text]
    text_features = cv.transform(texts)
    a=model.predict(text_features)
    return a[0]
print(spam_detection("Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005. Text FA to 87121 to receive entry question(std txt rate)T&C's apply 08452810075over18's"))


    
    
