"""
ChatGPT API integration and response generation for the e-invoice chatbot.
This module handles API calls and generates responses based on query context.
"""

import os
import json
import time
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import openai

class ResponseGenerator:
    """
    Handles ChatGPT API integration and response generation.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the response generator.
        
        Args:
            api_key: Optional OpenAI API key
        """
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key
    
    def set_api_key(self, api_key: str) -> bool:
        """
        Set or update the OpenAI API key.
        
        Args:
            api_key: OpenAI API key
            
        Returns:
            Boolean indicating if key was set successfully
        """
        if not api_key or not isinstance(api_key, str) or len(api_key) < 10:
            return False
        
        self.api_key = api_key
        openai.api_key = api_key
        return True
    
    def has_valid_api_key(self) -> bool:
        """
        Check if a valid API key is set.
        
        Returns:
            Boolean indicating if a valid API key is set
        """
        return bool(self.api_key) and isinstance(self.api_key, str) and len(self.api_key) >= 10
    
    def generate_response(self, query: str, response_context: Dict, model: str = "gpt-3.5-turbo") -> Dict:
        """
        Generate a response using the ChatGPT API.
        
        Args:
            query: The user's query text
            response_context: Dictionary with response context
            model: The OpenAI model to use
            
        Returns:
            Dictionary with response information
        """
        # Check if API key is set
        if not self.has_valid_api_key():
            return {
                'success': False,
                'error': 'missing_api_key',
                'message': 'Please provide an OpenAI API key in the sidebar.',
                'response_text': None,
                'visualization_type': None
            }
        
        # Check if query is out of domain
        if response_context.get('is_out_of_domain', False):
            return {
                'success': True,
                'error': None,
                'message': None,
                'response_text': response_context['out_of_domain_message'],
                'visualization_type': None
            }
        
        try:
            # Prepare messages for the API call
            messages = [
                {"role": "system", "content": response_context['system_prompt']},
                {"role": "user", "content": query}
            ]
            
            # Add data samples to the system message if available
            if 'data_samples' in response_context and response_context['data_samples']:
                data_samples_str = "Here are samples from the relevant data tables:\n\n"
                for table_name, samples in response_context['data_samples'].items():
                    data_samples_str += f"{table_name.upper()} TABLE SAMPLE:\n"
                    data_samples_str += json.dumps(samples, indent=2, ensure_ascii=False)
                    data_samples_str += "\n\n"
                
                # Add data samples as a system message
                messages.insert(1, {"role": "system", "content": data_samples_str})
            
            # Make the API call
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            return {
                'success': True,
                'error': None,
                'message': None,
                'response_text': response_text,
                'visualization_type': response_context.get('visualization_type')
            }
            
        except Exception as e:
            # Handle API errors
            error_message = str(e)
            
            # Check for common error types
            if "authentication" in error_message.lower():
                return {
                    'success': False,
                    'error': 'invalid_api_key',
                    'message': 'Invalid API key. Please check your OpenAI API key and try again.',
                    'response_text': None,
                    'visualization_type': None
                }
            elif "rate limit" in error_message.lower():
                return {
                    'success': False,
                    'error': 'rate_limit',
                    'message': 'Rate limit exceeded. Please wait a moment and try again.',
                    'response_text': None,
                    'visualization_type': None
                }
            else:
                return {
                    'success': False,
                    'error': 'api_error',
                    'message': f'API error: {error_message}',
                    'response_text': None,
                    'visualization_type': None
                }
    
    def generate_mock_response(self, query: str, response_context: Dict) -> Dict:
        """
        Generate a mock response for testing without API calls.
        
        Args:
            query: The user's query text
            response_context: Dictionary with response context
            
        Returns:
            Dictionary with mock response information
        """
        # Check if query is out of domain
        if response_context.get('is_out_of_domain', False):
            return {
                'success': True,
                'error': None,
                'message': None,
                'response_text': response_context['out_of_domain_message'],
                'visualization_type': None
            }
        
        # Get language from context
        lang = response_context['query_context']['language']
        
        # Generate mock responses based on query context
        primary_table = response_context['query_context']['primary_table']
        primary_domain = response_context['query_context']['primary_domain']
        
        # Mock responses in English
        mock_responses_en = {
            'invoices_tax_compliance': "Based on the invoice data, I can see that there are several tax compliance issues. The most common issue is incorrect VAT calculation, which appears in approximately 8% of the invoices. The total VAT amount across all invoices is 12,305 AED, with an average of 121.82 AED per invoice.",
            'invoices_fraud_detection': "The fraud detection analysis shows that 12,305 out of 101,183 invoices (12.16%) have been flagged as potential anomalies. The most common anomaly types are duplicate invoices (1,983 cases), round number amounts (1,752 cases), and just-under-limit transactions (1,521 cases).",
            'invoices_revenue_analysis': "Revenue analysis of the invoice data shows a total taxable amount of 246,100,000 AED across all emirates. Dubai accounts for the largest share at 35%, followed by Abu Dhabi at 28%, and Sharjah at 15%. The average invoice amount is 2,432 AED.",
            'invoices_geographic_distribution': "The geographic distribution of invoices shows that Dubai has the highest concentration with 35,414 invoices (35%), followed by Abu Dhabi with 28,331 invoices (28%), and Sharjah with 15,177 invoices (15%). The remaining emirates account for 22% of all invoices.",
            'items_tax_compliance': "Analysis of the items data shows that 3% of items are zero-rated and 2% are exempt from VAT. The remaining 95% are subject to the standard 5% VAT rate. There are 550,295 line items across all invoices, with an average of 5.44 items per invoice.",
            'items_fraud_detection': "The item-level fraud detection analysis has identified 8,254 suspicious line items (1.5% of all items). The most common anomalies are excessive quantities (2,145 cases), above-market pricing (1,876 cases), and vague descriptions (1,532 cases).",
            'taxpayers_tax_compliance': "The taxpayer compliance analysis shows that 814 out of 10,000 taxpayers (8.14%) have compliance issues. The average tax compliance score is 87.5 out of 100. Taxpayers in the retail sector have the highest compliance rate at 94%, while construction has the lowest at 78%.",
            'audit_logs_fraud_detection': "The audit log analysis reveals 1,245 suspicious modification patterns. The most common suspicious activities are multiple price changes within 24 hours (412 cases), after-hours modifications (356 cases), and repeated cancellations and reissues (289 cases)."
        }
        
        # Mock responses in Arabic
        mock_responses_ar = {
            'invoices_tax_compliance': "بناءً على بيانات الفواتير، يمكنني أن أرى أن هناك العديد من مشكلات الامتثال الضريبي. المشكلة الأكثر شيوعًا هي حساب ضريبة القيمة المضافة بشكل غير صحيح، والتي تظهر في حوالي 8٪ من الفواتير. يبلغ إجمالي مبلغ ضريبة القيمة المضافة عبر جميع الفواتير 12,305 درهم إماراتي، بمتوسط 121.82 درهم إماراتي لكل فاتورة.",
            'invoices_fraud_detection': "يُظهر تحليل كشف الاحتيال أن 12,305 من أصل 101,183 فاتورة (12.16٪) تم تحديدها كحالات شاذة محتملة. أكثر أنواع الشذوذ شيوعًا هي الفواتير المكررة (1,983 حالة)، والمبالغ ذات الأرقام المستديرة (1,752 حالة)، والمعاملات التي تقل قليلاً عن الحد (1,521 حالة).",
            'invoices_revenue_analysis': "يُظهر تحليل الإيرادات لبيانات الفواتير إجمالي مبلغ خاضع للضريبة قدره 246,100,000 درهم إماراتي عبر جميع الإمارات. تستحوذ دبي على الحصة الأكبر بنسبة 35٪، تليها أبو ظبي بنسبة 28٪، والشارقة بنسبة 15٪. متوسط مبلغ الفاتورة هو 2,432 درهم إماراتي.",
            'invoices_geographic_distribution': "يُظهر التوزيع الجغرافي للفواتير أن دبي لديها أعلى تركيز بـ 35,414 فاتورة (35٪)، تليها أبو ظبي بـ 28,331 فاتورة (28٪)، والشارقة بـ 15,177 فاتورة (15٪). تمثل الإمارات المتبقية 22٪ من جميع الفواتير.",
            'items_tax_compliance': "يُظهر تحليل بيانات العناصر أن 3٪ من العناصر معفاة من الضريبة بنسبة صفر و 2٪ معفاة من ضريبة القيمة المضافة. تخضع الـ 95٪ المتبقية لمعدل ضريبة القيمة المضافة القياسي البالغ 5٪. هناك 550,295 بندًا عبر جميع الفواتير، بمتوسط 5.44 عنصرًا لكل فاتورة.",
            'items_fraud_detection': "حدد تحليل كشف الاحتيال على مستوى العناصر 8,254 بندًا مشبوهًا (1.5٪ من جميع العناصر). أكثر الشذوذ شيوعًا هي الكميات المفرطة (2,145 حالة)، والتسعير فوق السوق (1,876 حالة)، والأوصاف الغامضة (1,532 حالة).",
            'taxpayers_tax_compliance': "يُظهر تحليل امتثال دافعي الضرائب أن 814 من أصل 10,000 دافع ضرائب (8.14٪) لديهم مشكلات في الامتثال. متوسط درجة الامتثال الضريبي هو 87.5 من أصل 100. يتمتع دافعو الضرائب في قطاع التجزئة بأعلى معدل امتثال بنسبة 94٪، بينما يمتلك قطاع البناء أدنى معدل بنسبة 78٪.",
            'audit_logs_fraud_detection': "يكشف تحليل سجل التدقيق عن 1,245 نمطًا مشبوهًا من التعديلات. أكثر الأنشطة المشبوهة شيوعًا هي تغييرات الأسعار المتعددة خلال 24 ساعة (412 حالة)، والتعديلات خارج ساعات العمل (356 حالة)، والإلغاءات وإعادة الإصدار المتكررة (289 حالة)."
        }
        
        # Create a key for the mock response
        response_key = f"{primary_table}_{primary_domain}"
        
        # Get the appropriate mock response based on language
        if lang == 'ar':
            mock_responses = mock_responses_ar
        else:
            mock_responses = mock_responses_en
        
        # Get the mock response or a default one
        response_text = mock_responses.get(
            response_key, 
            "I don't have specific information about that in the e-invoice data." if lang == 'en' else 
            "ليس لدي معلومات محددة حول ذلك في بيانات الفواتير الإلكترونية."
        )
        
        return {
            'success': True,
            'error': None,
            'message': None,
            'response_text': response_text,
            'visualization_type': response_context.get('visualization_type')
        }


# Example usage
if __name__ == "__main__":
    from data_router import DataRouter
    from response_handler import ResponseHandler
    
    router = DataRouter()
    handler = ResponseHandler()
    generator = ResponseGenerator()  # No API key for testing
    
    # Test with sample queries
    test_queries = [
        "Show me the trend of VAT collection over time",
        "Which emirate has the highest number of fraudulent invoices?",
        "أظهر لي توزيع الإيرادات حسب الإمارة",
        "What's the weather like today?",  # Out of domain
        "ما هي أفضل المطاعم في دبي؟"  # Out of domain
    ]
    
    # Mock data tables
    mock_data = {
        'invoices': pd.DataFrame({
            'invoice_number': ['INV001', 'INV002', 'INV003'],
            'invoice_datetime': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'buyer_emirate': ['Dubai', 'Abu Dhabi', 'Sharjah'],
            'invoice_tax_amount': [100, 200, 150]
        })
    }
    
    for query in test_queries:
        print(f"Query: {query}")
        
        # Get query context
        query_context = router.get_query_context(query)
        print(f"Language: {query_context['language']}")
        print(f"Tables: {query_context['relevant_tables']}")
        print(f"Domains: {query_context['relevant_domains']}")
        
        # Prepare response context
        response_context = handler.prepare_response_context(query_context, mock_data)
        
        # Generate mock response
        response = generator.generate_mock_response(query, response_context)
        
        print(f"Success: {response['success']}")
        if response['success']:
            print(f"Response: {response['response_text'][:100]}...")
            print(f"Visualization Type: {response['visualization_type']}")
        else:
            print(f"Error: {response['error']}")
            print(f"Message: {response['message']}")
        
        print("---")
