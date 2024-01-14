from dash.dependencies import Input, Output
from blockchain import get_data_from_blockchain
import plotly.graph_objects as go


# Helper functions
def borrow_interest_rate(utilization, base_rate, multiplier, kink, jump_multiplier):
    return multiplier * min(utilization, kink) + jump_multiplier * max(0, utilization - kink) + base_rate

def supply_interest_rate(utilization, base_rate, multiplier, kink, jump_multiplier, reserve_factor):
    return borrow_interest_rate(utilization, base_rate, multiplier, kink, jump_multiplier) * utilization * (1 - reserve_factor)


# Callback to update values from blockchain
def get_callbacks(app):
    @app.callback(
        [
        Output('total-supply', 'children'),
        Output('earning', 'children'),
        Output('borrowed', 'children'),
        Output('total-collateral', 'children'),
        Output('utilization', 'children'),
        Output('earn-apr', 'children'),
        Output('borrow-apr', 'children'),
        Output('reward-apr', 'children'),
        ],
        [Input('interval-component', 'n_intervals')]
    )
    def update_data(n_intervals):
        blockchain_data = get_data_from_blockchain()
        
        earning = (blockchain_data['vcNOTE']['total_supply'] * blockchain_data['vcNOTE']['exchange_rate_stored']
                * blockchain_data['vcNOTE']['underlying_price']) / 10**(18*3)
        borrowed = (blockchain_data['vcNOTE']['total_borrows'] * blockchain_data['vcNOTE']['underlying_price']) / 10**(18*2)

        collateral_vweax = (blockchain_data['chyVWEAX']['total_supply'] * blockchain_data['chyVWEAX']['underlying_price']) / 10**(18*2)
        # collateral_percent = ...
        total_collateral = collateral_vweax
        
        total_supply = earning + total_collateral
        
        utilization = blockchain_data['vcNOTE']['utilization']
        earn_apr = blockchain_data['cNOTE']['supply_rate'] + blockchain_data['vcNOTE']['supply_rate']
        borrow_apr = blockchain_data['cNOTE']['borrow_rate'] + blockchain_data['vcNOTE']['borrow_rate']

        reward_apr = blockchain_data['rewards']['rewards_per_week'] / 10**18 * 52 * blockchain_data['CANTO']['price'] / earning

        return f'${total_supply:,.0f}', f'${earning:,.0f}', f'${borrowed:,.0f}', f'${total_collateral:,.0f}',\
            f'{utilization:,.2%}', f'{earn_apr:,.2%}', f'{borrow_apr:,.2%}', f'{reward_apr:,.2%}'
    

    @app.callback(
    Output('utilization-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
    )
    def update_utilization_chart(n_intervals):
        blockchain_data = get_data_from_blockchain()
        
        # Extract interest rate model data
        utilization = blockchain_data['vcNOTE']['utilization']
        base_rate = blockchain_data['vcNOTE']['base_rate']
        multiplier = blockchain_data['vcNOTE']['multiplier']
        kink = blockchain_data['vcNOTE']['kink']
        jump_multiplier = blockchain_data['vcNOTE']['jump_multiplier']

        # Create Plotly figure
        fig = go.Figure()

        # Lines
        x_values = [x/100 for x in range(101)]
        borrow_values = [borrow_interest_rate(U, base_rate, multiplier, kink, jump_multiplier) + blockchain_data['cNOTE']['borrow_rate'] for U in x_values]
        supply_values = [supply_interest_rate(U, base_rate, multiplier, kink, jump_multiplier, 0.1) + blockchain_data['cNOTE']['supply_rate'] for U in x_values]

        fig.add_trace(go.Scatter(x=x_values, y=borrow_values, mode='lines', line=dict(color='purple', width=3), name='Borrow rate'))
        fig.add_trace(go.Scatter(x=x_values, y=supply_values, mode='lines', line=dict(color='blue', width=3), name='Supply rate'))

        # Dots
        borrow_rate_current = borrow_interest_rate(utilization, base_rate, multiplier, kink, jump_multiplier) + blockchain_data['cNOTE']['borrow_rate']
        dot_trace_borrow = go.Scatter(x=[utilization], y=[borrow_rate_current], mode='markers', marker=dict(size=10, color='purple'), showlegend=False, hoverinfo='none')
        fig.add_trace(dot_trace_borrow)

        supply_rate_current = supply_interest_rate(utilization, base_rate, multiplier, kink, jump_multiplier, 0.1) + blockchain_data['cNOTE']['supply_rate']
        dot_trace_supply = go.Scatter(x=[utilization], y=[supply_rate_current], mode='markers', marker=dict(size=10, color='blue'), showlegend=False, hoverinfo='none')
        fig.add_trace(dot_trace_supply)

        # Update layout
        fig.update_layout(
            showlegend=False,
            hovermode='x unified',
            hoverlabel=dict(bgcolor='white'),
            xaxis_title='Utilization',
            yaxis_tickformat='.2%',
            xaxis_tickformat='.0%',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    

    @app.callback(
        [
        Output('total-collateral-page', 'children'),
        ],
        [Input('interval-component', 'n_intervals')]
    )
    def update_data_collateral(n_intervals):
        blockchain_data = get_data_from_blockchain()
        
        collateral_vweax = (blockchain_data['chyVWEAX']['total_supply'] * blockchain_data['chyVWEAX']['underlying_price']) / 10**(18*2)
        # collateral_percent = ...
        total_collateral = collateral_vweax
        
        return f'${total_collateral:,.0f}',