# SSEPython - Plugin for Qlik

![Forecasing](docs/img/App%20Icon.png)

![Linear Regresssion](docs/img/Sheet_LinearRegression.png)
![Forecasing](docs/img/Sheet_Forecasting.png)

## About
Plugin to add machine learning capabilities in Qlik usine SSE( Server Side Extension)

## Setup

### Qlik Sense Desktop

1) Install Qlik Sense Desktop (June 2017 release or later).
2) Make sure you have Python 3.4 (or later) installed as well as the grpcio package.
3) Add SSEPlugin=SSEPython,localhost:50052 on a new line in your Settings.ini file located at C:\Users\[user]\Documents\Qlik\Sense or C:\user\[user]\AppData\Local\Programs\Qlik\Sense\Engine.
4) Copy the .qvf file from the selected example folder to C:\Users\[user]\Documents\Qlik\Sense\Apps.
5) Run the corresponding SSEPython.py package.
6) Start Qlik Sense Desktop and open the app for the examples.


### Qlik Sense Enterprise

1) Install Qlik Sense Enterprise (June 2017 release or later).
2) Make sure you have Python 3.4 (or later) installed as well as the grpcio package.
3) Add the SSE plugin settings in QMC under Analytic connections by inserting the following values: name:SSEPython, host: localhost, port:50052
4) Add the .qvf file from the selected example folder to QMC.
5) Run the corresponding SSEPython.py python package.
6) Start Qlik Sense Enterprise and open the app for the examples.



## Output Samples

![Linear Regression](docs/img/Conclusion_Linear_Regression_compact.PNG)
![Time Series Forecasting](docs/img/Conclusion_Time_Series_Dynamic_compact.PNG)
![Time Series Forecasing with Bounds](docs/img/Conclusion_Time_Series_with_Bounds_Compact.PNG)

## Capability Call from Qlik
![](/docs/img/Measure_Plugin_call_code.PNG)

![](/docs/img/Extract_Plugin_call_code.PNG)

## Code Samples

Link to Plugin Code - [SSEPython.py](main/SSEPython.py)

### Linear Regression
![Linear Regresssion Code](/docs/img/Main_Code_LinearRegression.PNG)

### Time Series Forecasting Using Prophet
![Forecasting](/docs/img/Main_Code_Prophet.PNG)

### Time Series Forecasting Using Prophet - Multi Fields
![Forecasting](/docs/img/Main_Code_Prophet_Extract.PNG)

### Plugin Function Declaration JSON
![](/docs/img/Main_Functions_Def_JSON.PNG)

### Qlik BundleRow Sample Data
![](/docs/img/Main_Qlik_BundleRow_Sample_Data.PNG)


