"""
Data routing and table filtering logic for the e-invoice chatbot.
This module analyzes user queries and routes them to the appropriate data tables.
"""

import re
import pandas as pd
from typing import Dict, List, Tuple, Set, Optional

class DataRouter:
    """
    Routes user queries to the appropriate data tables based on content analysis.
    """
    
    def __init__(self):
        # Define table-specific keywords for routing
        self.table_keywords = {
            'invoices': {
                'en': ['invoice', 'invoices', 'bill', 'bills', 'receipt', 'receipts', 'transaction', 
                       'transactions', 'payment', 'payments', 'vat', 'tax', 'emirate', 'buyer', 'seller'],
                'ar': ['فاتورة', 'فواتير', 'إيصال', 'إيصالات', 'معاملة', 'معاملات', 'دفع', 'مدفوعات', 
                       'ضريبة القيمة المضافة', 'ضريبة', 'إمارة', 'مشتري', 'بائع']
            },
            'items': {
                'en': ['item', 'items', 'product', 'products', 'goods', 'service', 'services', 
                       'quantity', 'price', 'unit', 'description', 'line item'],
                'ar': ['عنصر', 'عناصر', 'منتج', 'منتجات', 'بضائع', 'خدمة', 'خدمات', 
                       'كمية', 'سعر', 'وحدة', 'وصف', 'بند']
            },
            'taxpayers': {
                'en': ['taxpayer', 'taxpayers', 'company', 'companies', 'business', 'businesses', 
                       'vendor', 'vendors', 'supplier', 'suppliers', 'customer', 'customers', 'trn'],
                'ar': ['دافع الضرائب', 'دافعي الضرائب', 'شركة', 'شركات', 'عمل', 'أعمال', 
                       'بائع', 'بائعين', 'مورد', 'موردين', 'عميل', 'عملاء', 'رقم التسجيل الضريبي']
            },
            'audit_logs': {
                'en': ['audit', 'log', 'logs', 'history', 'tracking', 'changes', 'modification', 
                       'timestamp', 'user', 'action', 'event'],
                'ar': ['تدقيق', 'سجل', 'سجلات', 'تاريخ', 'تتبع', 'تغييرات', 'تعديل', 
                       'طابع زمني', 'مستخدم', 'إجراء', 'حدث']
            }
        }
        
        # Define domain-specific keywords for routing
        self.domain_keywords = {
            'tax_compliance': {
                'en': ['compliance', 'regulation', 'law', 'legal', 'requirement', 'rule', 'standard', 
                       'vat', 'tax', 'authority', 'audit', 'filing', 'report'],
                'ar': ['امتثال', 'تنظيم', 'قانون', 'قانوني', 'متطلب', 'قاعدة', 'معيار', 
                       'ضريبة القيمة المضافة', 'ضريبة', 'سلطة', 'تدقيق', 'تقديم', 'تقرير']
            },
            'fraud_detection': {
                'en': ['fraud', 'anomaly', 'suspicious', 'risk', 'detection', 'unusual', 'pattern', 
                       'outlier', 'irregular', 'fake', 'false', 'duplicate', 'manipulation'],
                'ar': ['احتيال', 'شذوذ', 'مشبوه', 'خطر', 'كشف', 'غير عادي', 'نمط', 
                       'قيمة متطرفة', 'غير منتظم', 'مزيف', 'خاطئ', 'مكرر', 'تلاعب']
            },
            'revenue_analysis': {
                'en': ['revenue', 'income', 'profit', 'sales', 'financial', 'analysis', 'trend', 
                       'forecast', 'projection', 'growth', 'decline', 'comparison'],
                'ar': ['إيرادات', 'دخل', 'ربح', 'مبيعات', 'مالي', 'تحليل', 'اتجاه', 
                       'توقع', 'إسقاط', 'نمو', 'انخفاض', 'مقارنة']
            },
            'geographic_distribution': {
                'en': ['geographic', 'location', 'region', 'emirate', 'city', 'area', 'distribution', 
                       'map', 'spatial', 'territory', 'zone', 'abu dhabi', 'dubai', 'sharjah', 'ajman', 
                       'umm al quwain', 'ras al khaimah', 'fujairah'],
                'ar': ['جغرافي', 'موقع', 'منطقة', 'إمارة', 'مدينة', 'منطقة', 'توزيع', 
                       'خريطة', 'مكاني', 'إقليم', 'منطقة', 'أبو ظبي', 'دبي', 'الشارقة', 'عجمان', 
                       'أم القيوين', 'رأس الخيمة', 'الفجيرة']
            }
        }
        
        # Define table-specific fields for more precise routing
        self.table_fields = {
            'invoices': [
                'invoice_number', 'invoice_datetime', 'invoice_type', 'invoice_category', 
                'invoice_sales_type', 'invoice_collection_type', 'document_status', 
                'buyer_name', 'buyer_trn', 'buyer_address', 'buyer_emirate', 
                'seller_name', 'seller_trn', 'seller_address', 'seller_emirate',
                'invoice_discount_amount', 'invoice_without_tax', 'invoice_tax_amount',
                'vat_rate', 'taxable_amount', 'emirate_revenue_share', 'is_anomaly'
            ],
            'items': [
                'item_id', 'invoice_id', 'item_name', 'item_description', 'quantity',
                'unit_price', 'line_discount', 'line_total', 'line_vat_amount', 'hs_code'
            ],
            'taxpayers': [
                'tax_number', 'name', 'registration_date', 'vat_registration_date',
                'legal_entity_type', 'business_size', 'sector', 'number_of_employees',
                'ownership_type', 'tax_compliance_score', 'bank_account', 'bank_country'
            ],
            'audit_logs': [
                'log_id', 'invoice_id', 'timestamp', 'user_id', 'action_type',
                'field_changed', 'old_value', 'new_value', 'system_notes'
            ]
        }
    
    def detect_language(self, query: str) -> str:
        """
        Detect if the query is in Arabic or English.
        
        Args:
            query: The user's query text
            
        Returns:
            'ar' for Arabic, 'en' for English (default)
        """
        # Simple detection based on Arabic character presence
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
        if arabic_pattern.search(query):
            return 'ar'
        return 'en'
    
    def route_query(self, query: str, selected_table: Optional[str] = None) -> Tuple[List[str], List[str]]:
        """
        Route a user query to the appropriate data tables and domains.
        
        Args:
            query: The user's query text
            selected_table: User-selected table from UI (if any)
            
        Returns:
            Tuple of (relevant_tables, relevant_domains)
        """
        # If user explicitly selected a table, prioritize it
        if selected_table and selected_table.lower() != 'all':
            return [selected_table.lower()], self._get_relevant_domains(query)
        
        # Detect language
        lang = self.detect_language(query)
        query_lower = query.lower()
        
        # Check for explicit table mentions
        relevant_tables = []
        for table, keywords in self.table_keywords.items():
            # Check if any keyword for this table is in the query
            if any(keyword in query_lower for keyword in keywords[lang]):
                relevant_tables.append(table)
        
        # Check for field mentions if no tables found yet
        if not relevant_tables:
            for table, fields in self.table_fields.items():
                # Check if any field for this table is mentioned in the query
                field_pattern = '|'.join([re.escape(field.replace('_', ' ')) for field in fields])
                if re.search(field_pattern, query_lower):
                    relevant_tables.append(table)
        
        # Default to invoices table if nothing specific was found
        if not relevant_tables:
            relevant_tables = ['invoices']
        
        # Get relevant domains
        relevant_domains = self._get_relevant_domains(query)
        
        return relevant_tables, relevant_domains
    
    def _get_relevant_domains(self, query: str) -> List[str]:
        """
        Identify relevant domains based on the query.
        
        Args:
            query: The user's query text
            
        Returns:
            List of relevant domain names
        """
        lang = self.detect_language(query)
        query_lower = query.lower()
        
        relevant_domains = []
        for domain, keywords in self.domain_keywords.items():
            # Check if any keyword for this domain is in the query
            if any(keyword in query_lower for keyword in keywords[lang]):
                relevant_domains.append(domain)
        
        # Default to all domains if nothing specific was found
        if not relevant_domains:
            relevant_domains = list(self.domain_keywords.keys())
        
        return relevant_domains
    
    def get_query_context(self, query: str, selected_table: Optional[str] = None) -> Dict:
        """
        Get comprehensive context about a query for the response generator.
        
        Args:
            query: The user's query text
            selected_table: User-selected table from UI (if any)
            
        Returns:
            Dictionary with query context information
        """
        lang = self.detect_language(query)
        tables, domains = self.route_query(query, selected_table)
        
        return {
            'query': query,
            'language': lang,
            'relevant_tables': tables,
            'relevant_domains': domains,
            'primary_table': tables[0] if tables else 'invoices',
            'primary_domain': domains[0] if domains else 'tax_compliance'
        }


# Example usage
if __name__ == "__main__":
    router = DataRouter()
    
    # Test with English queries
    test_queries_en = [
        "Show me all invoices with VAT issues",
        "What items have the highest price?",
        "List taxpayers with compliance issues",
        "Show me the audit log for invoice #12345",
        "What's the revenue distribution across emirates?",
        "How many fraudulent transactions were detected last month?"
    ]
    
    # Test with Arabic queries
    test_queries_ar = [
        "أظهر لي جميع الفواتير التي بها مشاكل في ضريبة القيمة المضافة",
        "ما هي العناصر ذات السعر الأعلى؟",
        "قائمة دافعي الضرائب الذين لديهم مشاكل في الامتثال",
        "أظهر لي سجل التدقيق للفاتورة رقم 12345",
        "ما هو توزيع الإيرادات عبر الإمارات؟",
        "كم عدد المعاملات الاحتيالية التي تم اكتشافها الشهر الماضي؟"
    ]
    
    print("English Query Routing:")
    for query in test_queries_en:
        context = router.get_query_context(query)
        print(f"Query: {query}")
        print(f"Language: {context['language']}")
        print(f"Tables: {context['relevant_tables']}")
        print(f"Domains: {context['relevant_domains']}")
        print("---")
    
    print("\nArabic Query Routing:")
    for query in test_queries_ar:
        context = router.get_query_context(query)
        print(f"Query: {query}")
        print(f"Language: {context['language']}")
        print(f"Tables: {context['relevant_tables']}")
        print(f"Domains: {context['relevant_domains']}")
        print("---")
