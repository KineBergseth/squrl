import pandas as pd
import base64
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import Namespace

# import data into dataframe and remove useless columns
census = pd.read_csv('squirrel_data.csv')
squirrel_census = pd.DataFrame(census)
squirrel_census.drop(['Hectare', 'Above Ground Sighter Measurement', 'Hectare Squirrel Number',
                      'Combination of Primary and Highlight Color', 'Color notes', 'Specific Location',
                      'Other Activities', 'Other Interactions', 'Lat/Long'], axis=1, inplace=True)
squirrel_census.rename(columns={"X": "lon", "Y": "lat"}, inplace=True)

# clean up data, replace missing data with the value unknown
squirrel_census["Age"].replace("?", "Unknown", inplace=True)
squirrel_census["Age"].fillna("Unknown", inplace=True)
squirrel_census["Primary Fur Color"].fillna("Unknown", inplace=True)
squirrel_census["Highlight Fur Color"].fillna("Unknown", inplace=True)
squirrel_census["Location"].fillna("Unknown", inplace=True)

# dropping missing values to avoid errors, drop rows where at least one element is missing
squirrel_census.dropna(inplace=True)

# convert dataframe to a list of dictionaries [{column -> value}, … , {column -> value}]
squirrel_data = squirrel_census.to_dict('records')

# Encode the local sound files
# https://life.hawkeoptics.com/woodland-stalking/
kuk_sound = 'assets/squirrel-kuk.wav'
quaa_sound = 'assets/squirrel-quaa.wav'
moan_sound = 'assets/squirrel-moan.mp3'

encoded_kuk_sound = base64.b64encode(open(kuk_sound, 'rb').read())
encoded_quaa_sound = base64.b64encode(open(quaa_sound, 'rb').read())
encoded_moan_sound = base64.b64encode(open(moan_sound, 'rb').read())

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'SQURL'
server = app.server

# Find Lat Long center to set map center
lat_center = sum(squirrel_census['lat']) / len(squirrel_census['lat'])
long_center = sum(squirrel_census['lon']) / len(squirrel_census['lon'])

data = dlx.geojson_to_geobuf(dlx.dicts_to_geojson(squirrel_data))

ns = Namespace("myNamespace", "mySubNamespace")
nz = Namespace("dlx", "scatter")

# get map style
url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

app.layout = html.Div(
    children=[

        # HEADER
        html.Div(
            children=[
                html.H1('SQURL', id='header-text'),

                # SOUNDS
                html.Div(
                    children=
                    [
                        html.Div(html.Img(src='assets/sound1.png', id='sound-kuks'),
                                 className="audio-btn"),
                        html.Div(html.Img(src='assets/sound2.png', id='sound-quaas'),
                                 className="audio-btn"),
                        html.Div(html.Img(src='assets/sound3.png', id='sound-moans'),
                                 className="audio-btn"),
                    ],
                    className="squirrel-sounds",
                ),
            ],
            className="header",
        ),

        # MAP
        html.Div(
            children=
            [
                dl.Map(center=[lat_center, long_center], zoom=14, children=[
                    dl.TileLayer(url=url, attribution=attribution, maxZoom=20),
                    dl.GeoJSON(data=data, id="unique-squirrel-id", format="geobuf", cluster=True,
                               zoomToBoundsOnClick=True, superClusterOptions={"radius": 50},
                               options=dict(pointToLayer=ns("pointToLayer"))),
                ], className="squirrel-map", style={'display': 'block'}, id="map"),
            ],
            className="squirrel-map-container",
        ),
        # SQUIRREL INFO
        html.Div(id="squirrel-facts"),

        # invisible sound containers
        html.Div(id="placeholder1", style={"display": "none"}),
        html.Div(id="placeholder2", style={"display": "none"}),
        html.Div(id="placeholder3", style={"display": "none"}),

    ],
    className="main"
)


# print squirrel fact table when a marker is clicked
@app.callback(Output("squirrel-facts", "children"), [Input("unique-squirrel-id", "click_feature")])
def squirrel_click(feature):
    # user must have clicker on a squirrel marker
    if (feature is not None) and not (feature['properties']['cluster']):
        # get data for marker
        facts = feature['properties']
        # get coords for clicked marker ;)
        coords = feature['geometry']
        latitude = coords['coordinates'][1]
        longitude = coords['coordinates'][0]

        # choose image paths based on the fact that applies to a certain squirrel
        if facts['Primary Fur Color'] == 'Gray':
            primary_color = "assets/color_gray.png"
        elif facts['Primary Fur Color'] == 'Cinnamon':
            primary_color = "assets/color_cinnamon.png"
        elif facts['Primary Fur Color'] == 'Black':
            primary_color = "assets/color_black.png"
        elif facts['Primary Fur Color'] == 'White':
            primary_color = "assets/color_white.png"
        else:
            primary_color = "assets/color_gray.png"

        if facts['Highlight Fur Color'].startswith('Gray'):
            highlight_color = "assets/color_gray.png"
        elif facts['Highlight Fur Color'].startswith('Cinnamon'):
            highlight_color = "assets/color_cinnamon.png"
        elif facts['Highlight Fur Color'].startswith('Black'):
            highlight_color = "assets/color_black.png"
        elif facts['Highlight Fur Color'].startswith('White'):
            highlight_color = "assets/color_white.png"
        else:
            highlight_color = "assets/color_gray.png"

        if facts['Age'] == 'Adult':
            age_image1 = html.Div([html.Img(src="assets/age_juvenile.png", className='age hidden'), html.P("juvenile")],
                                  className="div6 hidden")
            age_image2 = html.Div([html.Img(src="assets/age_adult.png", className='age'), html.P("adult")],
                                  className="div62")
        elif facts['Age'] == 'Juvenile':
            age_image1 = html.Div([html.Img(src="assets/age_juvenile.png", className='age'), html.P("juvenile")],
                                  className="div6")
            age_image2 = html.Div([html.Img(src="assets/age_adult.png", className='age hidden'), html.P("adult")],
                                  className="div62 hidden")
        else:
            age_image1 = html.Div([html.Img(src="assets/age_juvenile.png", className='age hidden'), html.P("juvenile")],
                                  className="div6 hidden")
            age_image2 = html.Div([html.Img(src="assets/age_adult.png", className='age hidden'), html.P("adult")],
                                  className="div62 hidden")

        if facts['Location'] == 'Ground Plane':
            location_image1 = html.Div(
                [html.Img(src="assets/ground.png", className='location hidden'), html.P("Ground")],
                className="div7 hidden")
            location_image2 = html.Div([html.Img(src="assets/tree.png", className='location'), html.P("tree")],
                                       className="div72")
        elif facts['Location'] == 'Above Ground':
            location_image1 = html.Div([html.Img(src="assets/ground.png", className='location'), html.P("Ground")],
                                       className="div7")
            location_image2 = html.Div([html.Img(src="assets/tree.png", className='location hidden'), html.P("tree")],
                                       className="div72 hidden")
        else:
            location_image1 = html.Div(
                [html.Img(src="assets/ground.png", className='location hidden'), html.P("Ground")],
                className="div7 hidden")
            location_image2 = html.Div([html.Img(src="assets/tree.png", className='location hidden'), html.P("tree")],
                                       className="div72 hidden")

        # choose html code based on action of the squirrel. not active alternatives will be colorless
        if facts['Running']:
            running_image = html.Div([html.Img(src="assets/running.png", className='activity'), html.P("Running")],
                                     className="div8")
        else:
            running_image = html.Div(
                [html.Img(src="assets/running.png", className='activity hidden'), html.P("Running")],
                className="div8 hidden")

        if facts['Chasing']:
            chasing_image = html.Div([html.Img(src="assets/chasing.png", className='activity'), html.P("Chasing")],
                                     className="div9")
        else:
            chasing_image = html.Div(
                [html.Img(src="assets/chasing.png", className='activity hidden'), html.P("Chasing")],
                className="div9 hidden")

        if facts['Climbing']:
            climbing_image = html.Div([html.Img(src="assets/climbing.png", className='activity'), html.P("Climbing")],
                                      className="div10")
        else:
            climbing_image = html.Div(
                [html.Img(src="assets/climbing.png", className='activity hidden'), html.P("Climbing")],
                className="div10 hidden")

        if facts['Eating']:
            eating_image = html.Div([html.Img(src="assets/eating.png", className='activity'), html.P("Eating")],
                                    className="div11")
        else:
            eating_image = html.Div([html.Img(src="assets/eating.png", className='activity hidden'), html.P("Eating")],
                                    className="div11 hidden")

        if facts['Foraging']:
            foraging_image = html.Div([html.Img(src="assets/foraging.png", className='activity'), html.P("Foraging")],
                                      className="div12")
        else:
            foraging_image = html.Div(
                [html.Img(src="assets/foraging.png", className='activity hidden'), html.P("Foraging")],
                className="div12 hidden")

        date = str(facts['Date'])
        date = date[:2] + '.' + date[2:4] + '.' + date[6:8]

        # the HTML for squirrel info panel
        return html.Div(children=[
            html.P('fur', id='div01'),
            html.Div([html.P("PRIMARY COLOR  "), html.Span(facts['Primary Fur Color'])], className="div1"),
            html.Div(html.Img(src=primary_color,
                              className='color_circle'), className="div2"),
            html.Div([html.P("HIGHLIGHT COLOR"), html.Span(facts['Highlight Fur Color'])], className="div3"),
            html.Div(html.Img(src=highlight_color,
                              className='color_circle'), className="div4"),
            html.P('POSITION', id='div45'),
            html.Div([html.Section([html.P("latitude "), html.Span(f"{latitude}°")]),
                      html.Section([html.P("longitude "), html.Span(f"{longitude}°")]),
                      html.Section([html.P("datetime "), html.Span(f"{date}, {facts['Shift']}")])], className="div5"),
            html.P('AGE', id='div56'),
            age_image1,
            age_image2,
            html.P('ELEVATION', id='div67'),
            location_image1,
            location_image2,
            html.P('Activity', id='div78'),
            running_image, chasing_image, climbing_image, eating_image, foraging_image,

        ], className='squirrel-data', )


#         html.Table([html.Tr([])])


@app.callback(Output("placeholder1", "children"),
              [Input("sound-kuks", "n_clicks")],
              )
def play(n_clicks):
    if n_clicks is None:
        n_clicks = 0
    if n_clicks % 2 != 0:
        return html.Audio(src='data:audio/mpeg;base64,{}'.format(encoded_kuk_sound.decode()),
                          controls=False,
                          autoPlay=True,
                          )


@app.callback(Output("placeholder2", "children"),
              [Input("sound-quaas", "n_clicks")],
              )
def play(n_clicks):
    if n_clicks is None:
        n_clicks = 0
    if n_clicks % 2 != 0:
        return html.Audio(src='data:audio/mpeg;base64,{}'.format(encoded_quaa_sound.decode()),
                          controls=False,
                          autoPlay=True,
                          )


@app.callback(Output("placeholder3", "children"),
              [Input("sound-moans", "n_clicks")],
              )
def play(n_clicks):
    if n_clicks is None:
        n_clicks = 0
    if n_clicks % 2 != 0:
        return html.Audio(src='data:audio/mpeg;base64,{}'.format(encoded_moan_sound.decode()),
                          controls=False,
                          autoPlay=True,
                          )


if __name__ == '__main__':
    app.run_server(debug=True)
