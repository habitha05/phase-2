<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<title>Cracking the Market - AI Stock Price Predictor</title>
<style>
  /* Reset & base */
  * {
    box-sizing: border-box;
  }
  body {
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: #efefef;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
    padding: 10px;
  }
  h1 {
    margin: 15px 0 5px;
    font-weight: 900;
    font-size: 1.8rem;
    color: #00d4ff;
    text-align: center;
  }
  h2 {
    margin: 0 0 20px;
    font-weight: 400;
    font-size: 1rem;
    text-align: center;
    color: #99e9ff;
  }
  #app {
    background: rgba(0, 0, 0, 0.35);
    border-radius: 15px;
    padding: 15px 20px 30px;
    width: 100%;
    max-width: 370px;
    box-shadow: 0 0 15px #00d4ff88;
    flex-shrink: 0;
  }
  label {
    font-weight: 600;
    font-size: 0.9rem;
    display: block;
    margin-bottom: 5px;
    color: #aad4e0;
  }
  input[type="text"] {
    width: 100%;
    padding: 10px 12px;
    border-radius: 8px;
    border: 1.5px solid #00d4ffaa;
    background-color: #0d1f26;
    color: #d6f4ff;
    font-size: 1rem;
    transition: border-color 0.3s ease;
  }
  input[type="text"]:focus {
    outline: none;
    border-color: #00f0ff;
    box-shadow: 0 0 6px #00f0ff77;
  }
  button {
    margin-top: 15px;
    width: 100%;
    padding: 12px;
    font-size: 1.1rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00d4ff, #0057a3);
    color: #000;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: background 0.3s ease;
    box-shadow: 0 2px 10px #0083b0aa;
  }
  button:hover {
    background: linear-gradient(90deg, #0099ff, #003d6b);
  }
  .loading {
    margin-top: 15px;
    font-weight: 600;
    font-size: 1rem;
    color: #00c3ff;
    text-align: center;
  }
  #error {
    margin-top: 15px;
    color: #ff4c4c;
    font-weight: 700;
    text-align: center;
  }
  #chart {
    margin-top: 20px;
  }
  footer {
    margin-top: auto;
    font-size: 0.75rem;
    color: #6098bb;
    text-align: center;
    user-select: none;
  }
  /* Responsive for mobile screen fitted to max height 600px and width 350px */
  @media (max-width: 400px) {
    #app {
      padding: 12px 15px 25px;
      max-width: 340px;
    }
    h1 {
      font-size: 1.5rem;
    }
    button {
      font-size: 1rem;
      padding: 11px;
    }
  }
</style>
);
  const loadingDiv = document.getElementById('loading'); </head>
<body>
  <h1>Cracking the Market</h1>
  <h2>AI-Driven Stock Price Prediction</h2>
  <div id="app" role="main" aria-label="Stock price prediction application">
    <label for="tickerInput">Enter Stock Ticker Symbol (e.g. TSLA, AAPL)</label>
    <input type="text" id="tickerInput" placeholder="TSLA" autocomplete="off" aria-describedby="error" />
    <button id="predictBtn" aria-live="polite" aria-busy="false">Predict</button>
    <div id="loading" class="loading" role="alert" aria-live="assertive" style="display:none;">Loading data and training model...</div>
    <div id="error" role="alert" aria-live="assertive"></div>
    <div id="chart"></div>
  </div>
  <footer>© 2024 Cracking the Market AI</footer>

<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.5.0/dist/tf.min.js"></script>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
  const predictBtn = document.getElementById('predictBtn');
  const tickerInput = document.getElementById('tickerInput'
  const errorDiv = document.getElementById('error');
  const chartDiv = document.getElementById('chart');

  // Alpha Vantage API - free tier has rate limits, requires your own API key
  // Using demo API key but user should use their own for better reliability
  const ALPHA_VANTAGE_API_KEY = 'demo'; // Replace 'demo' with your own API Key if you want
  const API_URL = 'https://www.alphavantage.co/query';

  // Clear previous outputs
  function resetUI() {
    errorDiv.textContent = '';
    loadingDiv.style.display = 'none';
    chartDiv.innerHTML = '';
  }

  // Fetch stock data function: daily adjusted close prices last 100 days
  async function fetchStockData(ticker) {
    const url = ${API_URL}?function=TIME_SERIES_DAILY_ADJUSTED&symbol=${encodeURIComponent(ticker)}&outputsize=compact&apikey=${ALPHA_VANTAGE_API_KEY};
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(Network error: ${response.status});
    }
    const data = await response.json();
    if (!data['Time Series (Daily)']) {
      throw new Error(data['Error Message'] || 'Failed to fetch stock data. Please check the ticker symbol.');
    }
    return data['Time Series (Daily)'];
  }

  // Prepare data: sort dates ascending and extract close prices
  function prepareData(timeSeries) {
    const dates = Object.keys(timeSeries).sort((a,b) => new Date(a) - new Date(b));
    const closePrices = dates.map(date => parseFloat(timeSeries[date]['5. adjusted close']));
    return {dates, closePrices};
  }

  // Normalize data using min-max scaling
  function normalizeData(data) {
    const min = Math.min(...data);
    const max = Math.max(...data);
    const scaled = data.map(d => (d - min) / (max - min));
    return {scaled, min, max};
  }

  // Create sequences for input to LSTM
  function createSequences(data, seqLen=30) {
    const xs = [];
    const ys = [];
    for(let i=seqLen; i < data.length; i++){
      xs.push(data.slice(i-seqLen, i));
      ys.push(data[i]);
    }
    return {xs, ys};
  }

  // Build LSTM Model
  function buildModel(seqLen) {
    const model = tf.sequential();
    model.add(tf.layers.lstm({
      units: 50,
      inputShape: [seqLen, 1],
      returnSequences: false,
    }));
    model.add(tf.layers.dense({units: 1}));
    model.compile({
      optimizer: tf.train.adam(),
      loss: 'meanSquaredError'
    });
    return model;
  }

  // Plot actual and predicted prices
  function plotResults(dates, actual, predicted, forecastDates) {
    const actualTrace = {
      x: dates,
      y: actual,
      name: 'Actual Prices',
      mode: 'lines+markers',
      line: {color: '#00d4ff'},
      marker: { size: 4 }
    };
    const predictedTrace = {
      x: forecastDates,
      y: predicted,
      name: 'Predicted Prices',
      mode: 'lines+markers',
      line: {dash: 'dot', color: '#ff9f00'},
      marker: { size: 4 }
    };
    const layout = {
      title: 'Stock Price Prediction',
      xaxis: {title: 'Date', tickangle: -45, rangeslider: { visible: false }},
      yaxis: {title: 'Price (USD)', fixedrange: false},
      legend: {orientation: 'h', y: -0.25},
      margin: {t: 40, b: 80},
      plot_bgcolor: '#0d1f26',
      paper_bgcolor: '#0d1f26',
      font: {color: '#aad4e0'}
    };
    Plotly.newPlot(chartDiv, [actualTrace, predictedTrace], layout, {responsive: true});
  }

  async function runPrediction(ticker) {
    resetUI();
    loadingDiv.style.display = 'block';
    predictBtn.setAttribute('aria-busy', 'true');

    try {
      const rawData = await fetchStockData(ticker);
      const { dates, closePrices } = prepareData(rawData);

      // Normalize data
      const { scaled, min, max } = normalizeData(closePrices);

      // Create sequences
      const seqLen = 30;
      const { xs, ys } = createSequences(scaled, seqLen);

      // Convert to tensors
      const xsTensor = tf.tensor3d(xs.map(seq => seq.map(v => [v])));
      const ysTensor = tf.tensor2d(ys.map(v => [v]));

      // Build and train the model
      const model = buildModel(seqLen);
      await model.fit(xsTensor, ysTensor, {
        epochs: 25,
        batchSize: 16,
        verbose: 0,
        callbacks: {
          onEpochEnd: (epoch, logs) => {
            loadingDiv.textContent = Training model... Epoch ${epoch+1} of 25, Loss: ${logs.loss.toFixed(5)};
          }
        }
      });

      // Predict next 7 days price recursively
      let inputSequence = scaled.slice(scaled.length - seqLen);
      const predictions = [];
      const forecastDates = [];
      let lastDate = new Date(dates[dates.length - 1]);
      for (let i=0; i<7; i++) {
        const inputTensor = tf.tensor3d([inputSequence.map(v => [v])]);
        const pred = model.predict(inputTensor);
        const predValue = pred.dataSync()[0];
        predictions.push(predValue);
        // Update sequence by appending prediction and removing first element
        inputSequence = inputSequence.slice(1);
        inputSequence.push(predValue);

        // Compute next forecast date skipping weekends
        do {
          lastDate.setDate(lastDate.getDate() + 1);
        } while (lastDate.getDay() === 0 || lastDate.getDay() === 6); // skip Sunday(0) and Saturday(6)
        forecastDates.push(lastDate.toISOString().split('T')[0]);

        pred.dispose();
        inputTensor.dispose();
      }

      // Denormalize predicted values
      const denormPredictions = predictions.map(p => p * (max - min) + min);

      // Plot results
      plotResults(dates, closePrices, denormPredictions, forecastDates);

    } catch(error) {
      errorDiv.textContent = error.message || 'An error occurred during prediction.';
    } finally {
      loadingDiv.style.display = 'none';
      predictBtn.setAttribute('aria-busy', 'false');
    }
  }

  // Event listener
  predictBtn.addEventListener('click', () => {
    const ticker = tickerInput.value.trim().toUpperCase();
    if (!ticker.match(/^[A-Z0-9]{1,5}$/)) {
      errorDiv.textContent = 'Please enter a valid stock ticker symbol (1-5 uppercase letters or numbers).';
      return;
    }
    runPrediction(ticker);
  });

  // Accessibility: run prediction on Enter key
  tickerInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      predictBtn.click();
    }
  });
</script>
</body>
</html>
</content>
</create_file>
