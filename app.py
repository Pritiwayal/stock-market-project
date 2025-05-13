from flask import Flask, render_template, request, redirect, url_for, session
import yfinance as yf
import numpy as np
import joblib
import os

app = Flask(__name__)
app.secret_key = 'secret-key'  # for session management

# Load trained model
model_path = 'stock_model.pkl'
if not os.path.exists(model_path):
    raise FileNotFoundError("The trained model 'stock_model.pkl' was not found!")

model = joblib.load(model_path)

# Dummy user data (replace with database for production)
users = {}

@app.route('/')
def index():
    if not session.get("username"):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return render_template('signup.html', error="User already exists")
        users[username] = password
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/analyze', methods=['POST'])
def analyze():
    stock_symbol = request.form['symbol'].upper()
    stock_data = yf.Ticker(stock_symbol)

    df = stock_data.history(period='6mo')

    if df.empty:
        return render_template('index.html', error="Invalid Stock Symbol or No Data Available")

    df['50_MA'] = df['Close'].rolling(window=50, min_periods=1).mean()
    df['200_MA'] = df['Close'].rolling(window=200, min_periods=1).mean()
    df['Volume_Trend'] = df['Volume'].diff().fillna(0)

    latest = df.iloc[-1]
    features = np.array([[latest['Close'], latest['50_MA'], latest['200_MA'], latest['Volume_Trend']]])
    features = np.nan_to_num(features)

    prediction = model.predict(features)[0]

    return render_template('index.html',
                           prediction=prediction,
                           stock=stock_symbol,
                           price=latest['Close'],
                           ma_50=latest['50_MA'],
                           ma_200=latest['200_MA'],
                           chart_button=True)

@app.route('/chart/<symbol>/<period>')
def show_chart(symbol, period):
    symbol = symbol.upper()
    df = yf.Ticker(symbol).history(period=period)

    if df.empty:
        return render_template('chart.html', error="No chart data")

    df['50_MA'] = df['Close'].rolling(window=50, min_periods=1).mean()
    df['200_MA'] = df['Close'].rolling(window=200, min_periods=1).mean()

    chart_data = {
        'dates': df.index.strftime('%Y-%m-%d').tolist(),
        'price': df['Close'].tolist(),
        'ma_50': df['50_MA'].tolist(),
        'ma_200': df['200_MA'].tolist()
    }

    return render_template('chart.html', symbol=symbol, period=period, chart_data=chart_data)

if __name__ == '__main__':
    app.run(debug=True)
