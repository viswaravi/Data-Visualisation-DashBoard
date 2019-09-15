import dash
import dash_core_components as dcc
import dash_html_components as html

print(dcc.__version__) # 0.6.0 or above is required



app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True

# Main Layout of Application
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
###

# HTML for Home Page
home_page = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    dcc.Link('Home', href='/',className='btn btn-info'),
    html.Br(),
    dcc.Link('Production Analysis', href='/productionAnalysis',className='btn btn-info'),

    # content will be rendered in this element
    # html.Div(id='page-content')
])
###

# Production Analysis Page
production_Analysis_Layout = html.Div([
     dcc.Location(id='url', refresh=False),
    html.H1('Hello Dash'),
    html.Div([
        html.P('Dash converts Python classes into HTML'),
        html.P('This conversion happens behind the scenes by Dash')
    ])
])
###

# URL Routing Function
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/productionAnalysis':
        return production_Analysis_Layout
    else:
        return home_page
###


# Initilize Server
if __name__ == '__main__':
    app.run_server()