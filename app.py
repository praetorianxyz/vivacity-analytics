from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from callbacks import get_callbacks
import dash


external_css = ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css', ]

app = Dash(__name__, pages_folder='pages', use_pages=True, external_stylesheets=external_css)

app.layout = html.Div([
    html.Br(),
    html.P('Vivacity Analytics', className='text-dark text-center fw-bold fs-1'),
    html.Div(children=[
        dcc.Link(page['name'], href=page['relative_path'], className='btn btn-dark m-2 fs-5')\
            for page in dash.page_registry.values()]
    ),
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # Update every 1 hour (3600 seconds)
        n_intervals=0
    ),
    dash.page_container,
], className='col-8 mx-auto')


get_callbacks(app)


if __name__ == '__main__':
    app.run_server(debug=True)