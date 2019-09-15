import dash
import dash_core_components as dcc
import dash_html_components as html
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.pyplot import figure
import datetime
from dash.dependencies import Input,Output
import psycopg2
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
    
# Intializing Dash Object
app = dash.Dash()
year_filter = 2018
months = ['All','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
global pie_labels
global pie_values
global loaded
loaded = False

#app.config['suppress_callback_exceptions']=True
# pt_date,pt_count,pt_mcode,pt_hanks,pt_dlvrs,pt_stdhnk,pt_nomhnk,pt_idlespnper,pt_tc,pt_crsec,pt_ssdur,pt_lsdur,pt_stdgpss


# Calculating Columns
def calculate_df(df):
    df['std_prod'] = (0.4536*df['pt_stdhnk']*df['pt_dlvrs'])/(df['pt_nomhnk'])
    df['act_prod'] =  ((0.4536*df['pt_hanks']*df['pt_dlvrs'])/(df['pt_nomhnk']))*((100-df['pt_tc'])/100)
    return df

# Fill Data on Dataframe from Database
conn = psycopg2.connect(database="ProLnx", user = "postgres", password = "brougekick77", host = "127.0.0.1", port = "5432")
cur = conn.cursor()
# Query to fetch from DB
cur.execute('SELECT  pt_date,pt_count,pt_mcode,pt_hanks,pt_dlvrs,pt_stdhnk,pt_nomhnk,pt_idlespnper,pt_tc,pt_crsec,pt_ssdur,pt_lsdur,pt_stdgpss FROM pt WHERE EXTRACT(year FROM "pt_date") ='+str(year_filter)+' ORDER BY pt_date;')
df=pd.DataFrame(cur.fetchall(),columns=['pt_date','pt_count','pt_mcode','pt_hanks','pt_dlvrs','pt_stdhnk','pt_nomhnk','pt_idlespnper','pt_tc','pt_crsec','pt_ssdur','pt_lsdur','pt_stdgpss'])
df['std_prod'] = (0.4536*df['pt_stdhnk']*df['pt_dlvrs'])/(df['pt_nomhnk'])
df['act_prod'] =  ((0.4536*df['pt_hanks']*df['pt_dlvrs'])/(df['pt_nomhnk']))*((100-df['pt_tc'])/100)
conn.close()   
###



# Fetching Count Codes from df
count_codes = []
count_codes =list(df['pt_count'].unique())
# Adding Count Options
count_options = []
for code in count_codes:
    count_options.append({'label':code,'value':code})
# Adding Month Options
month_options = []
for month in months:
    month_options.append({'label':month,'value':month})
###

### FrontEnd Layout for DashBoard
app.layout = html.Div([

        html.Div([
        dcc.Dropdown(id='count-picker',
                    options=count_options,
                    value=count_codes[0]),
        ],style={'width':'30%','display':'inline-block'}),
        html.Div([
        dcc.Dropdown(id='month-picker',
                    options=month_options,
                    value=months[0]),
        ],style={'width':'30%','display':'inline-block'}),
        dcc.Graph(id='bar-graph'),
        dcc.Graph(id='pie-graph')
],style={'padding':10})


###

### UPDATE PIE,BAR GRAPH
@app.callback([Output('pie-graph','figure'),
               Output('bar-graph','figure')],
              [Input('count-picker','value'),
               Input('month-picker','value')
              ])
def update_bar_graph(selected_count,selected_month):
    if months.index(selected_month) > 0: #Check if its a Month
        mon_grouped_flags = df['pt_date'].map(lambda x: x.month) == months.index(selected_month)
        mon_grouped = df[mon_grouped_flags]
        filtered_df = mon_grouped[mon_grouped['pt_count']==selected_count]
    else: # Whole Year Data
        filtered_df = df[df['pt_count']==selected_count]

    machine_wise_df = filtered_df.groupby('pt_mcode', as_index=False)
    machine_wise_df = machine_wise_df['std_prod','act_prod'].agg(np.sum)
    graph_data = []
    trace1 = go.Bar(
        x=list(machine_wise_df['pt_mcode']),
        y=list(machine_wise_df['std_prod']),
        name='Standard'
        )
    trace2 = go.Bar(
        x=list(machine_wise_df['pt_mcode']),
        y=list(machine_wise_df['act_prod']),
        name='Actual'
        )
    graph_data = [trace1,trace2]
    graph_layout = go.Layout(
        title='Production Data Machine Wise',
        barmode='group'
        )
    bar =  {
            'data':graph_data,
            'layout':graph_layout
            }
    # Pie Chart Data
    trace = go.Pie(labels=list(machine_wise_df['pt_mcode']), values=list(machine_wise_df['act_prod']),textinfo='label+percent')
    pie =  {
            'data':[trace],
            'layout':go.Layout(title='Pie Chart Production Data Analysis')
            }
    ###
    return pie,bar
###

### Starting the Server
if __name__ == '__main__':
    app.run_server()
###