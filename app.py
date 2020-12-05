import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas_datareader.data as web
from datetime import datetime
from datetime import timedelta
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots

#pandas_datareader is to get a data from internet

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

#companay name and cymbol
nsdq = pd.read_csv('./data/NASDAQcompanylist.csv')
nsdq.set_index('Symbol', inplace=True)
options = []
for tic in nsdq.index:
    options.append({'label':'{} {}'.format(tic,nsdq.loc[tic]['Name']), 'value':tic})

today = datetime.today()
BeforeToday = today - timedelta(weeks = 104)

md_dshbd = '''
This is a test site for real time dashboard using python plotly dash.
Data is stock price and is pulled from [Tiingo API](https://api.tiingo.com/).
Stock symbol are from companies in NASDAQ and could be multi-sortable.
Data could be dug up back in 2014. Code is at [github](https://github.com/Tak113/dshbd_dash_heroku_stock).
'''

app.layout = dbc.Container([
	#first row
	dbc.Row([
		dbc.Col([
			html.H1('Stock Ticker Dashboard',className='mt-2'),
			dcc.Markdown(md_dshbd)
		])
	]),
	
	dbc.Row([
		dbc.Col([
			html.P('Enter a stock symbol:',className='mb-0'),
			dcc.Dropdown(id='my_ticker_symbol',
					options = options,
					value = ['TSLA'],
					multi = True
			)
		])
	]),

	#secondary row
	dbc.Row([
		dbc.Col([
			html.P('Select a start and end date:',className='mb-0 mt-3'),
			dcc.DatePickerRange(id='my_date_picker',
					min_date_allowed=datetime(2014,1,1),
					max_date_allowed=datetime.today(),
					start_date=BeforeToday,
					end_date=today,
					className='inline-block mt-0'),
			dbc.Button('Submit',
					id='submit-button',
					color='dark',
					n_clicks=0,
					className='inline-block ml-3')
		])
	]),	
	
	#third row
	dbc.Row([
		dbc.Col([
			dcc.Graph(id='my_1stgraph',
				figure={
					#this is variable to be filled once symbol and time are selected as an inputs
				}
			),
			dcc.Graph(id='my_2ndgraph',
				figure={
					#this will be fill up
				},
				style={'height':'300px'}
			)
		])
	])
])

#1st graph callback
@app.callback(Output('my_1stgraph','figure'),
			[Input('submit-button','n_clicks')],
			[State('my_ticker_symbol','value'),
				State('my_date_picker','start_date'),
				State('my_date_picker','end_date')
			])
def update_graph(n_clicks,stock_ticker,start_date,end_date):
	start = datetime.strptime(start_date[:10],'%Y-%m-%d')
	end = datetime.strptime(end_date[:10],'%Y-%m-%d')

	traces = []
	for tic in stock_ticker:
		df = web.get_data_tiingo(tic, start, end, api_key="45a001c507ffe97a1f8781ba47249357fc9551bf")
		df.index = df.index.get_level_values('date') 
		traces.append(
	        {'x': df.index, 'y': df['close'], 'name': tic}
		)

	fig1 = {
	    'data': traces,
	    'layout': go.Layout(
	    	title = ', '.join(stock_ticker) + ' Closing Prices',
	    	yaxis={'title':'Stock Prices in USD'})
	}
	return fig1

#2nd graph callback
@app.callback(Output('my_2ndgraph','figure'),
			[Input('submit-button','n_clicks')],
			[State('my_ticker_symbol','value'),
				State('my_date_picker','start_date'),
				State('my_date_picker','end_date')
			])
def update_graph(n_clicks,stock_ticker,start_date,end_date):
	start = datetime.strptime(start_date[:10],'%Y-%m-%d')
	end = datetime.strptime(end_date[:10],'%Y-%m-%d')

	traces = []
	for tic in stock_ticker:
		df = web.get_data_tiingo(tic, start, end, api_key="45a001c507ffe97a1f8781ba47249357fc9551bf")
		df=df.assign(changes = df['close'].diff()/100)
		# print(df)
		# print(df.columns)
		df.index = df.index.get_level_values('date') 
		traces.append(
	        {'x': df.index, 'y': df['changes'], 'name': tic}
		)

	fig2 = {
	    'data': traces,
	    'layout': go.Layout(
	    	title = ', '.join(stock_ticker) + ' Daily Changes',
	    	yaxis={'title':'Daily changes in %'},
	    	xaxis={'showticklabels':False})
	}
	return fig2


if __name__ == '__main__':
	app.run_server(debug=True)
