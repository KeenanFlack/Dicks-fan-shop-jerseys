import dash
from dash import dcc, html
import dash_table
import plotly.express as px
import pandas as pd
import os

# Initialize app
app = dash.Dash(__name__)
app.title = "Sports Jerseys Aggregation Dashboard"

# Csv import and read
csv_path = r"C:\Users\kflac\Desktop\Dicks sporting goods\DSG_final.csv"
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"The file at {csv_path} was not found. Please check the path.")
df = pd.read_csv(csv_path)

# Data Cleaning
# Drop unnecessary columns
df = df.drop(columns=['Unnamed: 4'], errors='ignore')

# Handle missing values if necessary
df = df.dropna(subset=['list_price', 'brand', 'city', 'fit'])

# Ensure correct data types
df['list_price'] = pd.to_numeric(df['list_price'], errors='coerce')
df = df.dropna(subset=['list_price'])

# Aggregations

# Total Listings
total_listings = len(df)

# Average Price by Brand
avg_price_brand = df.groupby('brand')['list_price'].mean().reset_index()
avg_price_brand.rename(columns={'list_price': 'Average Price'}, inplace=True)

# Listings by City
listings_city = df['city'].value_counts().reset_index()
listings_city.columns = ['City', 'Number of Listings']

# Fit Distribution
fit_distribution = df['fit'].value_counts().reset_index()
fit_distribution.columns = ['Fit', 'Count']

# New Aggregation: Top 5 Brands by Number of Listings
top_5_brands = df['brand'].value_counts().nlargest(5).reset_index()
top_5_brands.columns = ['Brand', 'Number of Listings']

# Calculate Average Price for Top 5 Brands
avg_price_top5 = df[df['brand'].isin(top_5_brands['Brand'])].groupby('brand')['list_price'].mean().reset_index()
avg_price_top5.rename(columns={'brand': 'Brand', 'list_price': 'Average Price'}, inplace=True)

# Sort the top5 brands by Average Price descending (optional enhancement)
avg_price_top5 = avg_price_top5.sort_values(by='Average Price', ascending=False)

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Sports Jerseys Aggregation Dashboard", style={'textAlign': 'center'}),
    
    # Total Listings
    html.Div([
        html.H2(f"Total Listings: {total_listings}", style={'textAlign': 'center', 'color': '#0074D9'})
    ], style={'padding': '20px'}),
    
    # Aggregated Charts
    html.Div([
        # Average Price by Brand
        html.Div([
            dcc.Graph(
                id='avg-price-brand',
                figure=px.bar(
                    avg_price_brand,
                    x='brand',
                    y='Average Price',
                    title='Average Listing Price by Brand',
                    labels={'brand': 'Brand', 'Average Price': 'Average Price ($)'},
                    color='brand',
                    text='Average Price',
                    category_orders={'brand': avg_price_brand.sort_values('Average Price', ascending=False)['brand']}
                ).update_traces(texttemplate='$%{text:.2f}', textposition='outside')
                 .update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '1%'}),
        
        # Listings by City
        html.Div([
            dcc.Graph(
                id='listings-city',
                figure=px.bar(
                    listings_city,
                    x='City',
                    y='Number of Listings',
                    title='Number of Listings by City',
                    labels={'City': 'City', 'Number of Listings': 'Listings'},
                    color='Number of Listings',
                    color_continuous_scale='Viridis'
                )
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '1%'}),
    ]),
    
    # Fit Distribution
    html.Div([
        dcc.Graph(
            id='fit-distribution',
            figure=px.pie(
                fit_distribution,
                names='Fit',
                values='Count',
                title='Distribution of Jersey Fits',
                hole=0.3
            )
        )
    ], style={'width': '50%', 'margin': '0 auto', 'padding': '1%'}),
    
    # Top 5 Brands: Average Price
    html.Div([
        html.H2("Top 5 Brands: Average Price", style={'textAlign': 'center'}),
        dcc.Graph(
            id='top5-average-price',
            figure=px.bar(
                avg_price_top5,
                x='Brand',
                y='Average Price',
                title='Average Price of Top 5 Brands',
                labels={'Average Price': 'Average Price ($)', 'Brand': 'Brand'},
                color='Brand',
                text='Average Price',
                category_orders={'Brand': avg_price_top5['Brand']}  # Preserves the sorted order
            ).update_traces(texttemplate='$%{text:.2f}', textposition='outside')
             .update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        ),
        
        # Number of Listings for Top 5 Brands
        html.Div([
            dash_table.DataTable(
                id='top5-listings-table',
                columns=[
                    {"name": "Brand", "id": "Brand"},
                    {"name": "Number of Listings", "id": "Number of Listings"}
                ],
                data=top_5_brands.to_dict('records'),
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'font_family': 'Arial, sans-serif',
                    'font_size': '14px'
                },
                style_header={
                    'backgroundColor': '#0074D9',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                style_table={
                    'width': '50%',
                    'margin': '0 auto',
                    'padding': '20px'
                },
                page_action='none',
                style_as_list_view=True
            )
        ])
    ], style={'width': '50%', 'margin': '0 auto', 'padding': '20px'})
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
