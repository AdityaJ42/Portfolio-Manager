from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import Sign
import tweepy
from textblob import TextBlob
from datetime import date
from nsepy import get_history
import numpy as np
from keras.models import Sequential
from keras.layers import Dense

consumer_key = "k3pEbBjtma2rzFUOebGxaSKq0"
consumer_secret = "gF8u5ypWPr2EMNTfhujEI4X9uWlM1ROv6dxWzCHOMkmbjKBOU4"
access_token = "1101314053589233664-Ahed5wAS2hDCqdcnV40J6eCYgnRNOv"
access_token_secret = "GNOhScWWbhpBn4F5lwSlIqviHe8UCfE7J80mlGOnqqRja"


@login_required(login_url='app:login')
def home(request):
    return HttpResponse('<h1>Hello</h1>')


def register(request):
    if request.method == 'POST':
        user_form = Sign(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            email = user_form.cleaned_data['email']
            print(email)
            user.set_password(password)
            user.save()
            login(request, authenticate(username=username, password=password,
                                        email=email))
            return redirect('/app/home')
    else:
        user_form = Sign()

    return render(request, 'app/register.html', {'user_form': user_form})


def login_user(request):
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/app/home')
    return render(request, 'app/login.html')


def get_sentiment(company_name):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    public_tweets = api.search(company_name, count=50)
    positive, null = 0, 0

    for tweet in public_tweets:
        blob = TextBlob(tweet.text).sentiment
        if blob.subjectivity == 0:
            null += 1
            next
        if blob.polarity > 0:
            positive += 1

    if positive > (len(public_tweets) - null) / 2:
        return True


def predictor(ticker):
    stock_opt = get_history(symbol=ticker, start=date(2019, 1, 1),
                            end=date(2019, 3, 1))
    opening_prices = stock_opt['Open']
    dataset = np.array(opening_prices)

    def create_dataset(dataset):
        data_x = [dataset[n + 1] for n in range(len(dataset) - 2)]
        return np.array(data_x), dataset[2:]

    trainX, trainY = create_dataset(dataset)

    model = Sequential()
    model.add(Dense(8, input_dim=1, activation='relu'))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, epochs=200, batch_size=2, verbose=0)

    prediction = model.predict(np.array(dataset[len(dataset - 1)]))
    return prediction


def company(request):
    if request.method == 'POST':
        ticker = request.POST['ticker']
        name = request.POST['compname']

        sentiment = get_sentiment(name)
        predicted_price = predictor(ticker)
        print(sentiment, predicted_price)
