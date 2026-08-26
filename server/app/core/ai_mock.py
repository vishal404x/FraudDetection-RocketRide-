from typing import Any, Dict
from .ai_provider import AIProvider

class MockAIProvider(AIProvider):
    def analyze_invoice(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        # Simple heuristics to produce explainable findings
        findings = []
        score_factors = []
        amount = float(invoice.get('total_amount', 0) or 0)
        if amount > 1000000:
            findings.append('Invoice amount is unusually high for this organization')
            score_factors.append({'reason': 'high_amount', 'weight': 30})
        if 'suspicious' in invoice.get('invoice_number','').lower():
            findings.append('Invoice number contains suspicious token')
            score_factors.append({'reason': 'suspicious_invoice_number', 'weight': 20})
        explanation = {
            'summary': 'Mock analysis provided as fallback provider',
            'findings': findings,
            'factors': score_factors,
        }
        return explanation

    def analyze_email(self, email_payload: Dict[str, Any]) -> Dict[str, Any]:
        reasons = []
        if 'urgent' in (email_payload.get('subject','') or '').lower():
            reasons.append('Email contains urgency language')
        if email_payload.get('from') and email_payload['from'].endswith('@gmail.com'):
            reasons.append('External free email domain detected')
        return {'summary': 'Mock email analysis', 'reasons': reasons}

    def analyze_vendor_change(self, change_payload: Dict[str, Any]) -> Dict[str, Any]:
        reasons = []
        if change_payload.get('new_bank_account') and change_payload.get('new_bank_account').endswith('9876'):
            reasons.append('New account matches known suspicious suffix')
        return {'summary': 'Mock vendor change analysis', 'reasons': reasons}

    def explain_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Return structured explanation for why risk is raised
        reasons = []
        if context.get('deterministic_rules'):
            for r in context['deterministic_rules']:
                reasons.append({'type': 'rule', 'detail': r})
        if context.get('invoice') and float(context['invoice'].get('total_amount',0) or 0) > 500000:
            reasons.append({'type': 'ai', 'detail': 'Amount exceeds organization typical range'})
        return {'explanation': reasons, 'model': 'mock-v1'}

    def analyze_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        return {'summary': 'Mock transaction analysis', 'issues': []}
