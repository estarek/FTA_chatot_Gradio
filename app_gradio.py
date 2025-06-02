"""
Main Gradio application for the e-invoice chatbot.
This module integrates all components and provides the user interface.
"""

import gradio as gr
import pandas as pd
import numpy as np
import os
import json
import time
import functools
from typing import Dict, List, Tuple, Optional, Any

# Import custom modules
from data_router import DataRouter
from response_handler import ResponseHandler
from response_generator import ResponseGenerator
from visualization_generator import VisualizationGenerator

# Initialize components
router = DataRouter()
response_handler = ResponseHandler()
viz_generator = VisualizationGenerator()

# Function to load data
@functools.lru_cache(maxsize=1)
def load_data():
    """Load sample data for the chatbot"""
    try:
        # Check if real data files exist
        data_dir = "output"
        if os.path.exists(data_dir):
            data = {}
            
            # Try to load invoices data
            invoices_path = os.path.join(data_dir, "invoices.csv")
            if os.path.exists(invoices_path):
                data['invoices'] = pd.read_csv(invoices_path, low_memory=False, on_bad_lines='skip')
            
            # Try to load items data
            items_path = os.path.join(data_dir, "items.csv")
            if os.path.exists(items_path):
                data['items'] = pd.read_csv(items_path, low_memory=False, on_bad_lines='skip')
            
            # Try to load taxpayers data
            taxpayers_path = os.path.join(data_dir, "taxpayers.csv")
            if os.path.exists(taxpayers_path):
                data['taxpayers'] = pd.read_csv(taxpayers_path, low_memory=False, on_bad_lines='skip')
            
            # Try to load audit logs data
            audit_logs_path = os.path.join(data_dir, "invoice_audit_logs.csv")
            if os.path.exists(audit_logs_path):
                data['audit_logs'] = pd.read_csv(audit_logs_path, low_memory=False, on_bad_lines='skip')
            
            if data:
                return data
        
        # If real data not available, generate synthetic data
        return generate_synthetic_data()
    
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return generate_synthetic_data()

def generate_synthetic_data():
    """Generate synthetic data for demonstration"""
    # Generate invoices data
    invoices = pd.DataFrame({
        'invoice_number': [f'INV{i:03d}' for i in range(1, 101)],
        'invoice_datetime': pd.date_range(start='2025-01-01', periods=100),
        'buyer_emirate': np.random.choice(['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Fujairah', 'Ras Al Khaimah', 'Umm Al Quwain'], 100),
        'seller_emirate': np.random.choice(['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Fujairah', 'Ras Al Khaimah', 'Umm Al Quwain'], 100),
        'invoice_tax_amount': np.random.uniform(50, 500, 100),
        'invoice_without_tax': np.random.uniform(1000, 10000, 100),
        'invoice_type': np.random.choice(['Standard', 'Credit Note', 'Debit Note'], 100),
        'invoice_category': np.random.choice(['Goods', 'Services', 'Mixed'], 100),
        'invoice_sales_type': np.random.choice(['B2B', 'B2C', 'B2G'], 100),
        'document_status': np.random.choice(['Issued', 'Paid', 'Cancelled'], 100),
        'buyer_name': [f'Company {i}' for i in range(1, 101)],
        'buyer_trn': [f'TRN{i:06d}' for i in range(1, 101)],
        'seller_name': [f'Vendor {i % 20 + 1}' for i in range(1, 101)],
        'seller_trn': [f'TRN{i % 20 + 1:06d}' for i in range(1, 101)],
        'vat_rate': np.random.choice([5.0, 0.0], 100, p=[0.95, 0.05]),
        'vat_category': np.random.choice(['Standard', 'Zero Rated', 'Exempt'], 100, p=[0.95, 0.03, 0.02]),
        'is_anomaly': np.random.choice([0, 1], 100, p=[0.9, 0.1]),
        'anomaly_type': np.random.choice([None, 'Duplicate', 'Round Amount', 'Just Under Limit', 'Foreign Bank'], 100, p=[0.9, 0.025, 0.025, 0.025, 0.025]),
        'anomaly_risk_score': np.random.uniform(0, 1, 100)
    })
    
    # Generate items data
    items = pd.DataFrame({
        'item_id': [f'ITEM{i:04d}' for i in range(1, 301)],
        'invoice_id': [f'INV{np.random.randint(1, 101):03d}' for _ in range(1, 301)],
        'item_name': [f'Product {i % 50 + 1}' for i in range(1, 301)],
        'item_description': [f'Description for Product {i % 50 + 1}' for i in range(1, 301)],
        'quantity': np.random.randint(1, 10, 300),
        'unit_price': np.random.uniform(100, 1000, 300),
        'line_discount': np.random.uniform(0, 50, 300),
        'line_total': np.random.uniform(100, 5000, 300),
        'line_vat_amount': np.random.uniform(5, 250, 300),
        'hs_code': [f'HS{np.random.randint(1000, 9999)}' for _ in range(1, 301)]
    })
    
    # Generate taxpayers data
    taxpayers = pd.DataFrame({
        'tax_number': [f'TRN{i:06d}' for i in range(1, 51)],
        'name': [f'Company {i}' for i in range(1, 51)],
        'registration_date': pd.date_range(start='2020-01-01', periods=50),
        'vat_registration_date': pd.date_range(start='2020-01-15', periods=50),
        'legal_entity_type': np.random.choice(['LLC', 'FZE', 'Sole Proprietorship', 'Partnership'], 50),
        'business_size': np.random.choice(['Small', 'Medium', 'Large'], 50),
        'sector': np.random.choice(['Retail', 'Manufacturing', 'Services', 'Construction', 'Technology'], 50),
        'number_of_employees': np.random.randint(5, 500, 50),
        'ownership_type': np.random.choice(['Local', 'Foreign', 'Mixed'], 50),
        'tax_compliance_score': np.random.uniform(60, 100, 50),
        'bank_account': [f'AE{np.random.randint(100000000, 999999999)}' for _ in range(1, 51)],
        'bank_country': np.random.choice(['UAE', 'UAE', 'UAE', 'UAE', 'Other'], 50)
    })
    
    # Generate audit logs data
    audit_logs = pd.DataFrame({
        'log_id': [f'LOG{i:05d}' for i in range(1, 201)],
        'invoice_id': [f'INV{np.random.randint(1, 101):03d}' for _ in range(1, 201)],
        'timestamp': pd.date_range(start='2025-01-01', periods=200),
        'user_id': [f'USER{np.random.randint(1, 11):02d}' for _ in range(1, 201)],
        'action_type': np.random.choice(['Create', 'Update', 'Delete', 'View'], 200),
        'field_changed': np.random.choice(['Amount', 'Status', 'Date', 'Description', None], 200),
        'old_value': [f'Old Value {i}' for i in range(1, 201)],
        'new_value': [f'New Value {i}' for i in range(1, 201)],
        'system_notes': [f'System note {i}' for i in range(1, 201)]
    })
    
    return {
        'invoices': invoices,
        'items': items,
        'taxpayers': taxpayers,
        'audit_logs': audit_logs
    }

# Function to get example questions
def get_example_questions(lang):
    if lang == 'ar':
        return [
            "ما هو إجمالي ضريبة القيمة المضافة المحصلة في دبي؟",
            "أظهر لي توزيع الفواتير حسب الإمارة",
            "ما هي أنواع الشذوذ الأكثر شيوعًا في الفواتير؟",
            "قارن بين معدلات الامتثال الضريبي عبر القطاعات المختلفة",
            "أظهر لي اتجاه الإيرادات الشهرية على مدار العام الماضي"
        ]
    else:
        return [
            "What is the total VAT collected in Dubai?",
            "Show me the distribution of invoices by emirate",
            "What are the most common anomaly types in invoices?",
            "Compare tax compliance rates across different sectors",
            "Show me the monthly revenue trend over the past year"
        ]

# Function to get UI text based on language
def get_ui_text(key, lang='en'):
    ui_text = {
        'title': {
            'en': "E-Invoice Chatbot",
            'ar': "روبوت محادثة الفواتير الإلكترونية"
        },
        'subtitle': {
            'en': "Ask questions about e-invoice data in English or Arabic",
            'ar': "اطرح أسئلة حول بيانات الفواتير الإلكترونية باللغة الإنجليزية أو العربية"
        },
        'language_selector': {
            'en': "Select Language",
            'ar': "اختر اللغة"
        },
        'table_filter': {
            'en': "Filter by Table",
            'ar': "تصفية حسب الجدول"
        },
        'domain_filter': {
            'en': "Filter by Domain",
            'ar': "تصفية حسب المجال"
        },
        'api_key': {
            'en': "OpenAI API Key",
            'ar': "مفتاح API لـ OpenAI"
        },
        'api_key_help': {
            'en': "Enter your OpenAI API key to enable the chatbot",
            'ar': "أدخل مفتاح API الخاص بك لـ OpenAI لتمكين روبوت المحادثة"
        },
        'model_selector': {
            'en': "Select Model",
            'ar': "اختر النموذج"
        },
        'temperature': {
            'en': "Response Creativity",
            'ar': "إبداع الاستجابة"
        },
        'chat_placeholder': {
            'en': "Chat with the e-invoice assistant...",
            'ar': "تحدث مع مساعد الفواتير الإلكترونية..."
        },
        'send_button': {
            'en': "Send",
            'ar': "إرسال"
        },
        'clear_button': {
            'en': "Clear Chat",
            'ar': "مسح المحادثة"
        },
        'examples_button': {
            'en': "Show Examples",
            'ar': "عرض أمثلة"
        },
        'welcome_message': {
            'en': "👋 Hello! I'm your e-invoice assistant. Ask me anything about the e-invoice data, tax compliance, or fraud detection.",
            'ar': "👋 مرحبًا! أنا مساعدك للفواتير الإلكترونية. اسألني أي شيء عن بيانات الفواتير الإلكترونية أو الامتثال الضريبي أو كشف الاحتيال."
        },
        'api_key_missing': {
            'en': "⚠️ Please enter your OpenAI API key in the sidebar to enable AI responses.",
            'ar': "⚠️ الرجاء إدخال مفتاح API الخاص بك لـ OpenAI في الشريط الجانبي لتمكين ردود الذكاء الاصطناعي."
        },
        'tables': {
            'en': {
                'All': "All Tables",
                'invoices': "Invoices",
                'items': "Items",
                'taxpayers': "Taxpayers",
                'audit_logs': "Audit Logs"
            },
            'ar': {
                'All': "جميع الجداول",
                'invoices': "الفواتير",
                'items': "العناصر",
                'taxpayers': "دافعي الضرائب",
                'audit_logs': "سجلات التدقيق"
            }
        },
        'domains': {
            'en': {
                'All': "All Domains",
                'tax_compliance': "Tax Compliance",
                'fraud_detection': "Fraud Detection",
                'revenue_analysis': "Revenue Analysis",
                'geographic_distribution': "Geographic Distribution"
            },
            'ar': {
                'All': "جميع المجالات",
                'tax_compliance': "الامتثال الضريبي",
                'fraud_detection': "كشف الاحتيال",
                'revenue_analysis': "تحليل الإيرادات",
                'geographic_distribution': "التوزيع الجغرافي"
            }
        }
    }
    
    return ui_text.get(key, {}).get(lang, ui_text.get(key, {}).get('en', key))

# Function to handle chat input
def handle_chat_input(user_input, chat_history, api_key, language, selected_table, selected_domain, temperature):
    if not user_input.strip():
        return chat_history
    
    # Add user message to chat history
    chat_history.append((user_input, None))
    
    # Initialize response generator with API key
    response_generator = ResponseGenerator(api_key)
    
    # Get data
    data = load_data()
    
    # Get query context
    query_context = router.get_query_context(
        user_input, 
        selected_table if selected_table != 'All' else None
    )
    
    # Override domain if selected in UI
    if selected_domain != 'All':
        query_context['relevant_domains'] = [selected_domain]
        query_context['primary_domain'] = selected_domain
    
    # Prepare response context
    response_context = response_handler.prepare_response_context(query_context, data)
    
    # Generate response
    if response_generator.has_valid_api_key():
        # Use real API
        response = response_generator.generate_response(
            user_input, 
            response_context,
            model="gpt-3.5-turbo",
            temperature=temperature
        )
    else:
        # Use mock response
        response = response_generator.generate_mock_response(user_input, response_context)
    
    # Format response for language
    if response['success'] and response['response_text']:
        formatted_response = response_handler.format_response_for_language(
            response['response_text'], 
            query_context['language']
        )
    else:
        error_message = response.get('message', 'An error occurred')
        formatted_response = response_handler.format_response_for_language(
            error_message, 
            query_context['language']
        )
    
    # Update the last message with the response
    chat_history[-1] = (user_input, formatted_response)
    
    # Generate visualization if applicable
    viz_type = response.get('visualization_type')
    
    return chat_history, viz_type, query_context

# Function to generate visualization
def generate_visualization(viz_type, query_context):
    if not viz_type:
        return None
    
    data = load_data()
    primary_table = query_context['primary_table']
    
    if primary_table not in data:
        return None
    
    table_data = data[primary_table]
    
    if viz_type == 'time_series':
        return viz_generator.create_time_series_chart(table_data, query_context)
    elif viz_type == 'comparison':
        return viz_generator.create_comparison_chart(table_data, query_context)
    elif viz_type == 'distribution':
        return viz_generator.create_distribution_chart(table_data, query_context)
    elif viz_type == 'geographic':
        return viz_generator.create_geographic_chart(table_data, query_context)
    
    return None

# Function to clear chat history
def clear_chat_history(language):
    welcome_message = get_ui_text('welcome_message', language)
    return [(None, welcome_message)]

# Function to set example question
def set_example(example, textbox):
    return example

# Main function to create the Gradio interface
def create_interface():
    # Load data
    load_data()
    
    # Define theme
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="indigo",
    )
    
    # Create Gradio blocks
    with gr.Blocks(theme=theme, title="E-Invoice Chatbot") as demo:
        # Initialize state variables
        language_state = gr.State(value="en")
        selected_table_state = gr.State(value="All")
        selected_domain_state = gr.State(value="All")
        viz_type_state = gr.State(value=None)
        query_context_state = gr.State(value=None)
        
        # Create layout with two columns (left panel and main content)
        with gr.Row():
            # Left panel (sidebar equivalent)
            with gr.Column(scale=1):
                # App title
                gr.Markdown("# E-Invoice Chatbot")
                
                # Language selector
                gr.Markdown("### Select Language")
                with gr.Row():
                    en_button = gr.Button("English")
                    ar_button = gr.Button("العربية")
                
                gr.Markdown("---")
                
                # Data filters
                table_label = gr.Markdown("### Filter by Table")
                table_options = ["All", "invoices", "items", "taxpayers", "audit_logs"]
                table_dropdown = gr.Dropdown(
                    choices=table_options,
                    value="All",
                    label="Select Table"
                )
                
                domain_label = gr.Markdown("### Filter by Domain")
                domain_options = ["All", "tax_compliance", "fraud_detection", "revenue_analysis", "geographic_distribution"]
                domain_dropdown = gr.Dropdown(
                    choices=domain_options,
                    value="All",
                    label="Select Domain"
                )
                
                gr.Markdown("---")
                
                # API configuration
                api_label = gr.Markdown("### OpenAI API Key")
                api_key = gr.Textbox(
                    placeholder="Enter your OpenAI API key",
                    type="password",
                    label="API Key"
                )
                
                model_label = gr.Markdown("### Model Settings")
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    label="Response Creativity"
                )
            
            # Main content area
            with gr.Column(scale=3):
                # Chat interface
                welcome_message = get_ui_text('welcome_message', "en")
                chatbot = gr.Chatbot(
                    value=[(None, welcome_message)],
                    height=400,
                    bubble_full_width=False
                )
                
                # Input area
                with gr.Row():
                    chat_input = gr.Textbox(
                        placeholder=get_ui_text('chat_placeholder', "en"),
                        lines=2,
                        scale=4
                    )
                    send_button = gr.Button(get_ui_text('send_button', "en"), scale=1)
                
                # Action buttons
                with gr.Row():
                    clear_button = gr.Button(get_ui_text('clear_button', "en"))
                    examples_dropdown = gr.Dropdown(
                        choices=get_example_questions("en"),
                        label=get_ui_text('examples_button', "en")
                    )
                
                # Visualization area
                viz_output = gr.Plot(label="Visualization")
        
        # Event handlers
        
        # Language selection
        def update_language(lang, chat_history):
            # Update UI text based on language
            welcome_message = get_ui_text('welcome_message', lang)
            
            # If chat history is empty or only has welcome message, update it
            if not chat_history or len(chat_history) == 1 and chat_history[0][0] is None:
                return lang, [(None, welcome_message)]
            return lang, chat_history
        
        en_button.click(
            fn=update_language,
            inputs=[gr.State("en"), chatbot],
            outputs=[language_state, chatbot]
        )
        
        ar_button.click(
            fn=update_language,
            inputs=[gr.State("ar"), chatbot],
            outputs=[language_state, chatbot]
        )
        
        # Table selection
        table_dropdown.change(
            fn=lambda x: x,
            inputs=[table_dropdown],
            outputs=[selected_table_state]
        )
        
        # Domain selection
        domain_dropdown.change(
            fn=lambda x: x,
            inputs=[domain_dropdown],
            outputs=[selected_domain_state]
        )
        
        # Chat input handling
        def process_chat(user_input, chat_history, api_key, language, selected_table, selected_domain, temperature):
            new_chat_history, viz_type, query_context = handle_chat_input(
                user_input, chat_history, api_key, language, selected_table, selected_domain, temperature
            )
            return "", new_chat_history, viz_type, query_context
        
        send_button.click(
            fn=process_chat,
            inputs=[
                chat_input, chatbot, api_key, language_state, 
                selected_table_state, selected_domain_state, temperature
            ],
            outputs=[chat_input, chatbot, viz_type_state, query_context_state]
        )
        
        chat_input.submit(
            fn=process_chat,
            inputs=[
                chat_input, chatbot, api_key, language_state, 
                selected_table_state, selected_domain_state, temperature
            ],
            outputs=[chat_input, chatbot, viz_type_state, query_context_state]
        )
        
        # Visualization update
        def update_visualization(viz_type, query_context):
            if viz_type and query_context:
                return generate_visualization(viz_type, query_context)
            return None
        
        viz_type_state.change(
            fn=update_visualization,
            inputs=[viz_type_state, query_context_state],
            outputs=[viz_output]
        )
        
        # Clear chat
        clear_button.click(
            fn=clear_chat_history,
            inputs=[language_state],
            outputs=[chatbot]
        )
        
        # Example questions
        examples_dropdown.change(
            fn=set_example,
            inputs=[examples_dropdown],
            outputs=[chat_input]
        )
        
    return demo

# Main execution
if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
