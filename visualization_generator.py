"""
Interactive visualization generator for the e-invoice chatbot.
This module creates appropriate visualizations based on query context and data.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from typing import Dict, List, Tuple, Optional, Any

class VisualizationGenerator:
    """
    Generates interactive visualizations based on query context and data.
    """
    
    def __init__(self):
        # Define color schemes
        self.color_schemes = {
            'blues': px.colors.sequential.Blues,
            'reds': px.colors.sequential.Reds,
            'greens': px.colors.sequential.Greens,
            'purples': px.colors.sequential.Purples,
            'categorical': px.colors.qualitative.Safe
        }
        
        # Define emirate coordinates for maps
        self.emirate_coords = {
            'Abu Dhabi': (24.4539, 54.3773),
            'Dubai': (25.2048, 55.2708),
            'Sharjah': (25.3463, 55.4209),
            'Ajman': (25.4111, 55.4354),
            'Umm Al Quwain': (25.5647, 55.5534),
            'Ras Al Khaimah': (25.7895, 55.9432),
            'Fujairah': (25.1288, 56.3265)
        }
        
        # Define translations for common labels
        self.label_translations = {
            'en': {
                'invoice_count': 'Invoice Count',
                'invoice_amount': 'Invoice Amount',
                'tax_amount': 'Tax Amount',
                'date': 'Date',
                'month': 'Month',
                'year': 'Year',
                'quarter': 'Quarter',
                'emirate': 'Emirate',
                'anomaly_type': 'Anomaly Type',
                'count': 'Count',
                'percentage': 'Percentage',
                'amount': 'Amount',
                'risk_score': 'Risk Score',
                'taxpayer': 'Taxpayer',
                'sector': 'Sector',
                'compliance_score': 'Compliance Score'
            },
            'ar': {
                'invoice_count': 'عدد الفواتير',
                'invoice_amount': 'مبلغ الفاتورة',
                'tax_amount': 'مبلغ الضريبة',
                'date': 'تاريخ',
                'month': 'شهر',
                'year': 'سنة',
                'quarter': 'ربع سنة',
                'emirate': 'إمارة',
                'anomaly_type': 'نوع الشذوذ',
                'count': 'عدد',
                'percentage': 'نسبة مئوية',
                'amount': 'مبلغ',
                'risk_score': 'درجة المخاطرة',
                'taxpayer': 'دافع الضرائب',
                'sector': 'قطاع',
                'compliance_score': 'درجة الامتثال'
            }
        }
    
    def get_translated_label(self, key: str, lang: str) -> str:
        """
        Get a translated label for a given key and language.
        
        Args:
            key: The label key
            lang: Language code ('en' or 'ar')
            
        Returns:
            Translated label
        """
        if lang in self.label_translations and key in self.label_translations[lang]:
            return self.label_translations[lang][key]
        return key
    
    def create_time_series_chart(self, data: pd.DataFrame, query_context: Dict) -> go.Figure:
        """
        Create a time series chart based on the data and query context.
        
        Args:
            data: DataFrame containing time series data
            query_context: Dictionary with query context information
            
        Returns:
            Plotly figure object
        """
        lang = query_context['language']
        
        # Check if we have the necessary columns
        if 'invoice_datetime' not in data.columns:
            # Create a default time series chart with sample data
            sample_data = pd.DataFrame({
                'date': pd.date_range(start='2025-01-01', periods=12, freq='M'),
                'value': np.random.randint(100, 1000, 12)
            })
            
            fig = px.line(
                sample_data, 
                x='date', 
                y='value',
                title=self.get_translated_label('invoice_amount', lang) + ' ' + 
                      self.get_translated_label('over_time', lang)
            )
            
            fig.update_layout(
                xaxis_title=self.get_translated_label('date', lang),
                yaxis_title=self.get_translated_label('amount', lang),
                template='plotly_white'
            )
            
            return fig
        
        # Convert datetime column if needed
        if not pd.api.types.is_datetime64_any_dtype(data['invoice_datetime']):
            data['invoice_datetime'] = pd.to_datetime(data['invoice_datetime'], errors='coerce')
        
        # Group by month and calculate metrics
        data['month'] = data['invoice_datetime'].dt.to_period('M')
        
        # Determine what to plot based on available columns
        if 'invoice_tax_amount' in data.columns:
            y_column = 'invoice_tax_amount'
            y_label = self.get_translated_label('tax_amount', lang)
        elif 'invoice_without_tax' in data.columns:
            y_column = 'invoice_without_tax'
            y_label = self.get_translated_label('invoice_amount', lang)
        else:
            # Count invoices if no amount columns are available
            y_column = 'count'
            y_label = self.get_translated_label('invoice_count', lang)
        
        # Aggregate data
        if y_column == 'count':
            time_series_data = data.groupby('month').size().reset_index(name='count')
            time_series_data['month'] = time_series_data['month'].astype(str)
        else:
            time_series_data = data.groupby('month')[y_column].sum().reset_index()
            time_series_data['month'] = time_series_data['month'].astype(str)
        
        # Create the figure
        fig = px.line(
            time_series_data,
            x='month',
            y=y_column,
            title=f"{y_label} {self.get_translated_label('over_time', lang)}",
            markers=True
        )
        
        fig.update_layout(
            xaxis_title=self.get_translated_label('month', lang),
            yaxis_title=y_label,
            template='plotly_white'
        )
        
        # Add hover data
        fig.update_traces(
            hovertemplate=f"{self.get_translated_label('month', lang)}: %{x}<br>" +
                          f"{y_label}: %{y:,.2f}<extra></extra>"
        )
        
        return fig
    
    def create_comparison_chart(self, data: pd.DataFrame, query_context: Dict) -> go.Figure:
        """
        Create a comparison chart based on the data and query context.
        
        Args:
            data: DataFrame containing comparison data
            query_context: Dictionary with query context information
            
        Returns:
            Plotly figure object
        """
        lang = query_context['language']
        
        # Determine what to compare based on available columns
        if 'buyer_emirate' in data.columns:
            category_column = 'buyer_emirate'
            category_label = self.get_translated_label('emirate', lang)
        elif 'seller_sector' in data.columns:
            category_column = 'seller_sector'
            category_label = self.get_translated_label('sector', lang)
        elif 'invoice_type' in data.columns:
            category_column = 'invoice_type'
            category_label = self.get_translated_label('invoice_type', lang)
        else:
            # Create a default comparison chart with sample data
            sample_data = pd.DataFrame({
                'category': ['A', 'B', 'C', 'D', 'E'],
                'value': np.random.randint(100, 1000, 5)
            })
            
            fig = px.bar(
                sample_data, 
                x='category', 
                y='value',
                title=self.get_translated_label('comparison', lang),
                color='value',
                color_continuous_scale=self.color_schemes['blues']
            )
            
            fig.update_layout(
                xaxis_title=self.get_translated_label('category', lang),
                yaxis_title=self.get_translated_label('value', lang),
                template='plotly_white'
            )
            
            return fig
        
        # Determine what metric to use
        if 'invoice_tax_amount' in data.columns:
            value_column = 'invoice_tax_amount'
            value_label = self.get_translated_label('tax_amount', lang)
            agg_func = 'sum'
        elif 'invoice_without_tax' in data.columns:
            value_column = 'invoice_without_tax'
            value_label = self.get_translated_label('invoice_amount', lang)
            agg_func = 'sum'
        elif 'is_anomaly' in data.columns:
            value_column = 'is_anomaly'
            value_label = self.get_translated_label('anomaly_count', lang)
            agg_func = 'sum'
        else:
            # Count if no specific value column is available
            value_column = 'count'
            value_label = self.get_translated_label('count', lang)
            agg_func = 'count'
        
        # Aggregate data
        if agg_func == 'count':
            comparison_data = data.groupby(category_column).size().reset_index(name='count')
            comparison_data = comparison_data.sort_values('count', ascending=False)
            value_column = 'count'
        else:
            comparison_data = data.groupby(category_column)[value_column].agg(agg_func).reset_index()
            comparison_data = comparison_data.sort_values(value_column, ascending=False)
        
        # Create the figure
        fig = px.bar(
            comparison_data,
            x=category_column,
            y=value_column,
            title=f"{value_label} {self.get_translated_label('by', lang)} {category_label}",
            color=value_column,
            color_continuous_scale=self.color_schemes['blues']
        )
        
        fig.update_layout(
            xaxis_title=category_label,
            yaxis_title=value_label,
            template='plotly_white'
        )
        
        # Add hover data
        fig.update_traces(
            hovertemplate=f"{category_label}: %{x}<br>" +
                          f"{value_label}: %{y:,.2f}<extra></extra>"
        )
        
        return fig
    
    def create_distribution_chart(self, data: pd.DataFrame, query_context: Dict) -> go.Figure:
        """
        Create a distribution chart based on the data and query context.
        
        Args:
            data: DataFrame containing distribution data
            query_context: Dictionary with query context information
            
        Returns:
            Plotly figure object
        """
        lang = query_context['language']
        
        # Determine what to distribute based on available columns
        if 'anomaly_type' in data.columns and data['anomaly_type'].notna().any():
            category_column = 'anomaly_type'
            category_label = self.get_translated_label('anomaly_type', lang)
        elif 'buyer_emirate' in data.columns:
            category_column = 'buyer_emirate'
            category_label = self.get_translated_label('emirate', lang)
        elif 'invoice_type' in data.columns:
            category_column = 'invoice_type'
            category_label = self.get_translated_label('invoice_type', lang)
        elif 'vat_category' in data.columns:
            category_column = 'vat_category'
            category_label = self.get_translated_label('vat_category', lang)
        else:
            # Create a default pie chart with sample data
            sample_data = pd.DataFrame({
                'category': ['A', 'B', 'C', 'D', 'E'],
                'value': np.random.randint(100, 1000, 5)
            })
            
            fig = px.pie(
                sample_data, 
                values='value', 
                names='category',
                title=self.get_translated_label('distribution', lang),
                color_discrete_sequence=self.color_schemes['categorical']
            )
            
            fig.update_layout(template='plotly_white')
            
            return fig
        
        # Count occurrences of each category
        distribution_data = data[category_column].value_counts().reset_index()
        distribution_data.columns = [category_column, 'count']
        
        # Create the figure
        fig = px.pie(
            distribution_data,
            values='count',
            names=category_column,
            title=f"{self.get_translated_label('distribution', lang)} {self.get_translated_label('by', lang)} {category_label}",
            color_discrete_sequence=self.color_schemes['categorical']
        )
        
        fig.update_layout(template='plotly_white')
        
        # Add percentage to hover
        total = distribution_data['count'].sum()
        distribution_data['percentage'] = distribution_data['count'] / total * 100
        
        # Update hover template
        fig.update_traces(
            hovertemplate=f"{category_label}: %{label}<br>" +
                          f"{self.get_translated_label('count', lang)}: %{value}<br>" +
                          f"{self.get_translated_label('percentage', lang)}: %{percent:.1f}%<extra></extra>"
        )
        
        return fig
    
    def create_geographic_chart(self, data: pd.DataFrame, query_context: Dict) -> go.Figure:
        """
        Create a geographic chart based on the data and query context.
        
        Args:
            data: DataFrame containing geographic data
            query_context: Dictionary with query context information
            
        Returns:
            Plotly figure object
        """
        lang = query_context['language']
        
        # Check if we have emirate data
        emirate_column = None
        if 'buyer_emirate' in data.columns:
            emirate_column = 'buyer_emirate'
        elif 'seller_emirate' in data.columns:
            emirate_column = 'seller_emirate'
        
        if emirate_column is None:
            # Create a default map with sample data
            sample_data = pd.DataFrame({
                'emirate': list(self.emirate_coords.keys()),
                'value': np.random.randint(100, 1000, len(self.emirate_coords))
            })
            
            # Create a map dataframe with coordinates
            map_data = []
            for _, row in sample_data.iterrows():
                emirate = row['emirate']
                if emirate in self.emirate_coords:
                    lat, lon = self.emirate_coords[emirate]
                    map_data.append({
                        'emirate': emirate,
                        'value': row['value'],
                        'lat': lat,
                        'lon': lon
                    })
            
            map_df = pd.DataFrame(map_data)
            
            # Create the map
            fig = px.scatter_mapbox(
                map_df,
                lat='lat',
                lon='lon',
                size='value',
                color='value',
                hover_name='emirate',
                hover_data={'value': True, 'lat': False, 'lon': False},
                color_continuous_scale=self.color_schemes['blues'],
                size_max=50,
                zoom=6,
                center={"lat": 24.7, "lon": 54.5},
                title=self.get_translated_label('geographic_distribution', lang)
            )
            
            fig.update_layout(
                mapbox_style='open-street-map',
                template='plotly_white'
            )
            
            return fig
        
        # Determine what metric to use
        if 'invoice_tax_amount' in data.columns:
            value_column = 'invoice_tax_amount'
            value_label = self.get_translated_label('tax_amount', lang)
            agg_func = 'sum'
        elif 'invoice_without_tax' in data.columns:
            value_column = 'invoice_without_tax'
            value_label = self.get_translated_label('invoice_amount', lang)
            agg_func = 'sum'
        elif 'is_anomaly' in data.columns:
            value_column = 'is_anomaly'
            value_label = self.get_translated_label('anomaly_count', lang)
            agg_func = 'sum'
        else:
            # Count if no specific value column is available
            value_column = 'count'
            value_label = self.get_translated_label('count', lang)
            agg_func = 'count'
        
        # Aggregate data by emirate
        if agg_func == 'count':
            emirate_data = data.groupby(emirate_column).size().reset_index(name='value')
        else:
            emirate_data = data.groupby(emirate_column)[value_column].agg(agg_func).reset_index()
            emirate_data = emirate_data.rename(columns={value_column: 'value'})
        
        # Create a map dataframe with coordinates
        map_data = []
        for _, row in emirate_data.iterrows():
            emirate = row[emirate_column]
            if emirate in self.emirate_coords:
                lat, lon = self.emirate_coords[emirate]
                map_data.append({
                    'emirate': emirate,
                    'value': row['value'],
                    'lat': lat,
                    'lon': lon
                })
        
        map_df = pd.DataFrame(map_data)
        
        # Create the map
        fig = px.scatter_mapbox(
            map_df,
            lat='lat',
            lon='lon',
            size='value',
            color='value',
            hover_name='emirate',
            hover_data={'value': True, 'lat': False, 'lon': False},
            color_continuous_scale=self.color_schemes['blues'],
            size_max=50,
            zoom=6,
            center={"lat": 24.7, "lon": 54.5},
            title=f"{value_label} {self.get_translated_label('by', lang)} {self.get_translated_label('emirate', lang)}"
        )
        
        fig.update_layout(
            mapbox_style='open-street-map',
            template='plotly_white'
        )
        
        return fig
    
    def generate_visualization(self, viz_type: str, data: Dict[str, pd.DataFrame], query_context: Dict) -> Optional[go.Figure]:
        """
        Generate an appropriate visualization based on the type and data.
        
        Args:
            viz_type: Type of visualization to generate
            data: Dictionary of available data tables
            query_context: Dictionary with query context information
            
        Returns:
            Plotly figure object or None if visualization cannot be generated
        """
        # Get the primary table from query context
        primary_table = query_context['primary_table']
        
        # Check if we have data for the primary table
        if primary_table not in data or data[primary_table].empty:
            return None
        
        # Get the data for the primary table
        table_data = data[primary_table]
        
        # Generate the appropriate visualization based on type
        if viz_type == 'time_series':
            return self.create_time_series_chart(table_data, query_context)
        elif viz_type == 'comparison':
            return self.create_comparison_chart(table_data, query_context)
        elif viz_type == 'distribution':
            return self.create_distribution_chart(table_data, query_context)
        elif viz_type == 'geographic':
            return self.create_geographic_chart(table_data, query_context)
        else:
            # Default to comparison chart if type is not recognized
            return self.create_comparison_chart(table_data, query_context)


# Example usage
if __name__ == "__main__":
    from data_router import DataRouter
    
    router = DataRouter()
    viz_generator = VisualizationGenerator()
    
    # Test with sample queries
    test_queries = [
        "Show me the trend of VAT collection over time",
        "Which emirate has the highest number of fraudulent invoices?",
        "أظهر لي توزيع الإيرادات حسب الإمارة",
        "What's the distribution of invoice types?"
    ]
    
    # Mock data tables
    mock_data = {
        'invoices': pd.DataFrame({
            'invoice_number': [f'INV{i:03d}' for i in range(1, 101)],
            'invoice_datetime': pd.date_range(start='2025-01-01', periods=100),
            'buyer_emirate': np.random.choice(['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Fujairah', 'Ras Al Khaimah', 'Umm Al Quwain'], 100),
            'invoice_tax_amount': np.random.uniform(50, 500, 100),
            'invoice_without_tax': np.random.uniform(1000, 10000, 100),
            'invoice_type': np.random.choice(['Standard', 'Credit Note', 'Debit Note'], 100),
            'is_anomaly': np.random.choice([0, 1], 100, p=[0.9, 0.1]),
            'anomaly_type': np.random.choice([None, 'Duplicate', 'Round Amount', 'Just Under Limit', 'Foreign Bank'], 100, p=[0.9, 0.025, 0.025, 0.025, 0.025])
        })
    }
    
    for query in test_queries:
        print(f"Query: {query}")
        
        # Get query context
        query_context = router.get_query_context(query)
        print(f"Language: {query_context['language']}")
        
        # Determine visualization type
        if "trend" in query.lower() or "over time" in query.lower():
            viz_type = 'time_series'
        elif "highest" in query.lower() or "compare" in query.lower():
            viz_type = 'comparison'
        elif "distribution" in query.lower():
            viz_type = 'distribution'
        elif "emirate" in query.lower() or "map" in query.lower():
            viz_type = 'geographic'
        else:
            viz_type = 'comparison'  # Default
        
        print(f"Visualization Type: {viz_type}")
        
        # Generate visualization
        fig = viz_generator.generate_visualization(viz_type, mock_data, query_context)
        
        if fig:
            print("Visualization generated successfully")
        else:
            print("Failed to generate visualization")
        
        print("---")
