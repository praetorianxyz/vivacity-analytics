import dash
from dash import html, dcc

dash.register_page(__name__, path='/interest-rate-model', name='Interest Rate Model', order=1)

######################### PAGE LAYOUT #########################
layout = html.Div(children=[
    html.Div(children=[
        html.H2('Interest Rate Model'),
        dcc.Loading(
            type='circle',
            children=dcc.Graph(id='utilization-chart'),
        ),
    ]),
], className='bg-light p-4 m-2')