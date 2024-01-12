import dash
from dash import html, Input, Output, callback

dash.register_page(__name__, path='/collateral', name='Collateral Assets', order=2)

######################### PAGE LAYOUT #########################
layout = html.Div(children=[
    html.Div(children=[
        html.H2('Collateral Assets'),
        'The following RWAs are whitelisted to serve as collateral to borrow against:'
    ]),
    html.Div(children=[
        html.Br(),
        html.H5('Vanguard High Yield Corporate Bond Fund'),
        html.Ul(children=[
            html.Li(children=[
                html.B('Symbol: '), 'hyVWEAX',]),
            html.Li(children=[
                html.B('RWA: '), 'Vanguard High-Yield Corporate Fund Admiral Shares (VWEAX)',]),
            html.Li(children=[
                html.B('Tokenization: '), 'HiYield',]),
            html.Li(children=[
                html.B('Deposited: '), html.Span(id='total-collateral-page')]),
        ]),
    ])
], className='bg-light p-4 m-2')