"""
Multilingual and domain-aware response handling for the e-invoice chatbot.
This module generates appropriate responses based on query context and language.
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd

class ResponseHandler:
    """
    Handles multilingual and domain-aware responses for the e-invoice chatbot.
    """
    
    def __init__(self):
        # Define domain constraints
        self.domain_constraints = {
            'tax_compliance': {
                'en': [
                    "The response must focus on tax compliance aspects of e-invoices.",
                    "Include references to UAE tax regulations when relevant.",
                    "Highlight compliance requirements and best practices.",
                    "Mention potential compliance issues in the data if applicable."
                ],
                'ar': [
                    "يجب أن يركز الرد على جوانب الامتثال الضريبي للفواتير الإلكترونية.",
                    "قم بتضمين إشارات إلى اللوائح الضريبية في الإمارات العربية المتحدة عند الاقتضاء.",
                    "سلط الضوء على متطلبات الامتثال وأفضل الممارسات.",
                    "اذكر مشكلات الامتثال المحتملة في البيانات إذا كان ذلك ممكنًا."
                ]
            },
            'fraud_detection': {
                'en': [
                    "The response must focus on fraud detection aspects of e-invoices.",
                    "Highlight anomaly patterns and risk indicators in the data.",
                    "Explain potential fraud scenarios related to the query.",
                    "Include fraud prevention recommendations when relevant."
                ],
                'ar': [
                    "يجب أن يركز الرد على جوانب كشف الاحتيال في الفواتير الإلكترونية.",
                    "سلط الضوء على أنماط الشذوذ ومؤشرات المخاطر في البيانات.",
                    "اشرح سيناريوهات الاحتيال المحتملة المتعلقة بالاستعلام.",
                    "قم بتضمين توصيات منع الاحتيال عند الاقتضاء."
                ]
            },
            'revenue_analysis': {
                'en': [
                    "The response must focus on revenue analysis aspects of e-invoices.",
                    "Include financial metrics and trends from the data.",
                    "Provide insights on revenue distribution and patterns.",
                    "Compare financial data across different dimensions when relevant."
                ],
                'ar': [
                    "يجب أن يركز الرد على جوانب تحليل الإيرادات للفواتير الإلكترونية.",
                    "قم بتضمين المقاييس والاتجاهات المالية من البيانات.",
                    "قدم رؤى حول توزيع الإيرادات والأنماط.",
                    "قارن البيانات المالية عبر الأبعاد المختلفة عند الاقتضاء."
                ]
            },
            'geographic_distribution': {
                'en': [
                    "The response must focus on geographic distribution aspects of e-invoices.",
                    "Include emirate-specific data and comparisons.",
                    "Highlight regional patterns and anomalies.",
                    "Reference location-based insights from the data."
                ],
                'ar': [
                    "يجب أن يركز الرد على جوانب التوزيع الجغرافي للفواتير الإلكترونية.",
                    "قم بتضمين بيانات ومقارنات خاصة بالإمارة.",
                    "سلط الضوء على الأنماط والشذوذ الإقليمي.",
                    "الإشارة إلى الرؤى المستندة إلى الموقع من البيانات."
                ]
            }
        }
        
        # Define table descriptions for context
        self.table_descriptions = {
            'invoices': {
                'en': "The invoices table contains information about e-invoice transactions including buyer/seller details, amounts, tax information, and status.",
                'ar': "يحتوي جدول الفواتير على معلومات حول معاملات الفواتير الإلكترونية بما في ذلك تفاصيل المشتري/البائع والمبالغ ومعلومات الضرائب والحالة."
            },
            'items': {
                'en': "The items table contains line-item details for each invoice, including product information, quantities, prices, and tax amounts.",
                'ar': "يحتوي جدول العناصر على تفاصيل البنود لكل فاتورة، بما في ذلك معلومات المنتج والكميات والأسعار ومبالغ الضرائب."
            },
            'taxpayers': {
                'en': "The taxpayers table contains information about businesses registered for tax purposes, including registration details, business type, and compliance scores.",
                'ar': "يحتوي جدول دافعي الضرائب على معلومات حول الشركات المسجلة لأغراض الضرائب، بما في ذلك تفاصيل التسجيل ونوع الأعمال ودرجات الامتثال."
            },
            'audit_logs': {
                'en': "The audit logs table contains records of changes made to invoices, including timestamps, user information, and modification details.",
                'ar': "يحتوي جدول سجلات التدقيق على سجلات التغييرات التي تم إجراؤها على الفواتير، بما في ذلك الطوابع الزمنية ومعلومات المستخدم وتفاصيل التعديل."
            }
        }
        
        # Define system messages for different contexts
        self.system_messages = {
            'general': {
                'en': "You are an AI assistant specializing in UAE e-invoice data analysis. Provide helpful, accurate information based on the data available. Focus only on e-invoicing, tax compliance, and related financial topics.",
                'ar': "أنت مساعد ذكاء اصطناعي متخصص في تحليل بيانات الفواتير الإلكترونية في الإمارات العربية المتحدة. قدم معلومات مفيدة ودقيقة بناءً على البيانات المتاحة. ركز فقط على الفواتير الإلكترونية والامتثال الضريبي والمواضيع المالية ذات الصلة."
            },
            'out_of_domain': {
                'en': "I can only provide information related to e-invoicing, tax compliance, fraud detection, and financial analysis in the UAE context. For other topics, please consult a different resource.",
                'ar': "يمكنني فقط تقديم معلومات متعلقة بالفواتير الإلكترونية والامتثال الضريبي وكشف الاحتيال والتحليل المالي في سياق الإمارات العربية المتحدة. للموضوعات الأخرى، يرجى الرجوع إلى مصدر مختلف."
            }
        }
        
        # Define visualization suggestions based on query types
        self.visualization_suggestions = {
            'time_series': {
                'en': ['trend', 'over time', 'monthly', 'yearly', 'quarterly', 'history', 'historical'],
                'ar': ['اتجاه', 'مع مرور الوقت', 'شهريًا', 'سنويًا', 'ربع سنوي', 'تاريخ', 'تاريخي']
            },
            'comparison': {
                'en': ['compare', 'comparison', 'versus', 'vs', 'against', 'difference', 'highest', 'lowest'],
                'ar': ['قارن', 'مقارنة', 'مقابل', 'ضد', 'الفرق', 'الأعلى', 'الأدنى']
            },
            'distribution': {
                'en': ['distribution', 'breakdown', 'percentage', 'proportion', 'share', 'allocation'],
                'ar': ['توزيع', 'تقسيم', 'نسبة مئوية', 'نسبة', 'حصة', 'تخصيص']
            },
            'geographic': {
                'en': ['map', 'location', 'emirate', 'region', 'geographic', 'spatial', 'area'],
                'ar': ['خريطة', 'موقع', 'إمارة', 'منطقة', 'جغرافي', 'مكاني', 'منطقة']
            }
        }
    
    def get_system_prompt(self, query_context: Dict) -> str:
        """
        Generate a system prompt based on query context.
        
        Args:
            query_context: Dictionary with query context information
            
        Returns:
            System prompt string
        """
        lang = query_context['language']
        
        # Start with general system message
        system_prompt = self.system_messages['general'][lang] + "\n\n"
        
        # Add table descriptions for relevant tables
        for table in query_context['relevant_tables']:
            if table in self.table_descriptions:
                system_prompt += self.table_descriptions[table][lang] + "\n"
        
        # Add domain constraints
        for domain in query_context['relevant_domains']:
            if domain in self.domain_constraints:
                for constraint in self.domain_constraints[domain][lang]:
                    system_prompt += "- " + constraint + "\n"
        
        return system_prompt
    
    def is_out_of_domain(self, query: str) -> bool:
        """
        Check if a query is completely outside the e-invoice domain.
        
        Args:
            query: The user's query text
            
        Returns:
            Boolean indicating if query is out of domain
        """
        # List of topics that are definitely out of domain
        out_of_domain_topics_en = [
            'weather', 'sports', 'entertainment', 'movies', 'music', 'recipes', 
            'cooking', 'travel', 'vacation', 'hotel', 'flight', 'restaurant',
            'politics', 'election', 'news', 'celebrity', 'game', 'gaming'
        ]
        
        out_of_domain_topics_ar = [
            'طقس', 'رياضة', 'ترفيه', 'أفلام', 'موسيقى', 'وصفات', 
            'طبخ', 'سفر', 'عطلة', 'فندق', 'رحلة', 'مطعم',
            'سياسة', 'انتخابات', 'أخبار', 'مشاهير', 'لعبة', 'ألعاب'
        ]
        
        query_lower = query.lower()
        
        # Check English out-of-domain topics
        for topic in out_of_domain_topics_en:
            if topic in query_lower:
                return True
                
        # Check Arabic out-of-domain topics
        for topic in out_of_domain_topics_ar:
            if topic in query_lower:
                return True
        
        return False
    
    def get_visualization_type(self, query: str, query_context: Dict) -> Optional[str]:
        """
        Determine the appropriate visualization type based on the query.
        
        Args:
            query: The user's query text
            query_context: Dictionary with query context information
            
        Returns:
            Visualization type or None if no visualization is appropriate
        """
        lang = query_context['language']
        query_lower = query.lower()
        
        # Check for visualization keywords
        for viz_type, keywords in self.visualization_suggestions.items():
            if any(keyword in query_lower for keyword in keywords[lang]):
                return viz_type
        
        # Default visualizations based on domain
        domain_viz_mapping = {
            'tax_compliance': 'comparison',
            'fraud_detection': 'distribution',
            'revenue_analysis': 'time_series',
            'geographic_distribution': 'geographic'
        }
        
        primary_domain = query_context['primary_domain']
        if primary_domain in domain_viz_mapping:
            return domain_viz_mapping[primary_domain]
        
        return None
    
    def format_response_for_language(self, response: str, lang: str) -> str:
        """
        Format the response based on the language.
        
        Args:
            response: The response text
            lang: Language code ('en' or 'ar')
            
        Returns:
            Formatted response
        """
        if lang == 'ar':
            # For Arabic, ensure text is right-to-left
            return f'<div dir="rtl">{response}</div>'
        
        return response
    
    def prepare_response_context(self, query_context: Dict, data_tables: Dict[str, pd.DataFrame]) -> Dict:
        """
        Prepare comprehensive context for response generation.
        
        Args:
            query_context: Dictionary with query context information
            data_tables: Dictionary of available data tables
            
        Returns:
            Dictionary with response context
        """
        # Check if query is out of domain
        if self.is_out_of_domain(query_context['query']):
            return {
                'is_out_of_domain': True,
                'out_of_domain_message': self.system_messages['out_of_domain'][query_context['language']]
            }
        
        # Get system prompt
        system_prompt = self.get_system_prompt(query_context)
        
        # Determine visualization type
        viz_type = self.get_visualization_type(query_context['query'], query_context)
        
        # Prepare data samples for relevant tables
        data_samples = {}
        for table_name in query_context['relevant_tables']:
            if table_name in data_tables and not data_tables[table_name].empty:
                # Get a sample of the data (first 5 rows)
                data_samples[table_name] = data_tables[table_name].head(5).to_dict(orient='records')
        
        return {
            'is_out_of_domain': False,
            'system_prompt': system_prompt,
            'visualization_type': viz_type,
            'data_samples': data_samples,
            'query_context': query_context
        }


# Example usage
if __name__ == "__main__":
    from data_router import DataRouter
    
    router = DataRouter()
    handler = ResponseHandler()
    
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
        
        if response_context['is_out_of_domain']:
            print(f"Out of Domain: {response_context['out_of_domain_message']}")
        else:
            print(f"Visualization Type: {response_context['visualization_type']}")
            print(f"System Prompt: {response_context['system_prompt'][:100]}...")
        
        print("---")
