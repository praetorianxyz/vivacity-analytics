import dash
from dash import html
from dash.dependencies import Input, Output

dash.register_page(__name__, path='/', name='Overview', order=0)

######################### PAGE LAYOUT #########################
layout = html.Div(children=[
    html.Div(children=[
        html.H2('Overview'),
        'Vivacity is an RWA lending market on Canto. Test',
        html.Br(), html.Br(),
        'Users can supply NOTE to earn interest.',
        html.Br(), html.Br(),
        'RWAs can be deposited as collateral to borrow NOTE.',
    ]),
    html.Div(children=[
        html.Br(),
        html.H2('Market Stats'),
        html.Br(),
        html.B('Total Supply: '), html.Span(id='total-supply'),
        html.Br(), html.Br(),
        html.B('Earning: '), html.Span(id='earning'),
        ' | ', html.B('Borrowed: '), html.Span(id='borrowed'),
        ' | ', html.B('Collateral: '), html.Span(id='total-collateral'),
        ' | ', html.B('Collateral Assets: '), 1,
        html.Br(), html.Br(),
        html.B('Utilization: '), html.Span(id='utilization'),
        ' | ', html.B('Net Earn APR: '), html.Span(id='earn-apr'), ' (+',html.Span(id='reward-apr'), ' CANTO reward)',
        ' | ', html.B('Net Borrow APR: '), html.Span(id='borrow-apr'),
        html.Br(), html.Br(),
    ])
], className='bg-light p-4 m-2')

