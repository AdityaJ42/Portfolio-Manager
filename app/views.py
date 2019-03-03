from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import Sign
import tweepy
from textblob import TextBlob
from .models import Company
import numpy as np
import os
from keras.models import Sequential
from keras.layers import Dense

# Insert keys here
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""


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
    else:
        return False


def predictor(ticker):
    base = os.getcwd()
    path = base + '/app/data/' + ticker + '.csv'
    fd = open(path)
    dataset = []
    for n, line in enumerate(fd):
        if n != 0:
            dataset.append(float(line.split(',')[4]))
    dataset = np.array(dataset)

    def create_dataset(dataset):
        data_x = [dataset[n + 1] for n in range(len(dataset) - 2)]
        return np.array(data_x), dataset[2:]

    trainX, trainY = create_dataset(dataset)

    model = Sequential()
    model.add(Dense(8, input_dim=1, activation='relu'))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, epochs=50, batch_size=10, verbose=0)

    return model.predict(np.array([dataset[len(dataset) - 1]]))


@login_required(login_url='app:login')
def home(request):
    return render(request, 'app/home.html')


@login_required(login_url='app:login')
def dashboard(request):
    update_item = []
    data = Company.objects.filter(user=request.user)
    for item in data:
        ticker = item.company_intial
        predicted_price = predictor(ticker.upper())
        if predicted_price[0][0] < item.stoploss:
            update_item.append(item.company_intial)

    for temp in data:
        if temp.company_intial in update_item:
            temp.to_sell = "Yes"
            temp.save()
        else:
            temp.to_sell = "No"
            temp.save()

    data = Company.objects.filter(user=request.user)
    return render(request, 'app/dashboard.html', {'data': data})


def register(request):
    if request.method == 'POST':
        user_form = Sign(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            email = user_form.cleaned_data['email']

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


@login_required(login_url='app:login')
def logout_user(request):
    logout(request)
    return redirect('/app/signin')


@login_required(login_url='app:login')
def company(request):
    if request.method == 'POST':
        user = request.user
        ticker = request.POST['ticker']
        name = request.POST['compname']
        amount_of_stock = request.POST['amt']
        pur_price = request.POST['ppps']
        stploss = request.POST['stopl']

        company = Company()
        if request.POST['rate']:
            rate = request.POST['rate']
            company.dividend_rate = rate
        company.user = user
        company.company_name = name
        company.company_intial = ticker
        company.amount_of_stock = amount_of_stock
        company.purchase_price = pur_price
        company.stoploss = stploss
        company.save()

        return redirect('/app/dashboard')
    return render(request, 'app/test.html')


@login_required(login_url='app:login')
def portfolio(request):
    companies = Company.objects.filter(user=request.user)
    costs = {}
    costs_pred = {}
    dividend = {}
    total = 0
    total2 = 0
    for company in companies:
        total += company.amount_of_stock * company.purchase_price

    for company in companies:
        pred = predictor(company.company_intial)
        percent1 = (company.purchase_price * company.amount_of_stock * 100) / total
        percent2 = (pred * company.amount_of_stock * 100) / total
        div_amt = (pred * company.amount_of_stock * company.dividend_rate) / 100
        dividend[company.company_name] = div_amt
        total2 += div_amt
        costs[company.company_name] = percent1
        costs_pred[company.company_name] = percent2

    return render(request, 'app/portfolio.html', {'costs': costs, 'total': total, 'dividend': dividend,
                                                'costs_pred': costs_pred, 'total2': total2})


@login_required(login_url='app:login')
def stock_update(request, id):
    company = Company.objects.filter(user=request.user)
    data = [x for x in company if x.id == id][0]

    if request.method == 'POST':
        new_amt = request.POST['amt']
        if request.POST["rate"]:
            new_rate = request.POST['rate']
            data.dividend_rate = new_rate
        new_stoploss = request.POST['stopl']

        data.amount_of_stock = new_amt
        data.stoploss = new_stoploss

        data.save()
        return redirect('/app/dashboard')
    return render(request, 'app/update_company.html', {'data': data})
