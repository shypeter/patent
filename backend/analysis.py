from typing import List, Dict, Optional
from dataclasses import dataclass
import openai
from datetime import datetime
from models import db, Patent, Company

@dataclass
class InfringingProduct:
    product_name: str
    infringement_likelihood: str
    relevant_claims: List[str]
    explanation: str
    specific_features: List[str]

class PatentAnalyzer:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key

    def _get_relevant_claims(self, patent: Patent, product_description: str) -> List[str]:
        """分析產品描述與專利權利要求的相關性"""
        relevant_claims = []

        for claim in patent.claims:
            prompt = f"""
            Analyze if this product potentially infringes the following patent claim.

            Product description: {product_description}

            Patent claim: {claim['num']}: {claim['text']}


            Answer only YES or NO.
            """

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            if "YES" in response.choices[0].message.content.upper():
                relevant_claims.append(claim['text'])

        return relevant_claims

    def _analyze_infringement_level(self, num_relevant_claims: int) -> str:
        """基於相關權利要求數量判斷侵權可能性"""
        if num_relevant_claims > 5:
            return "High"
        elif num_relevant_claims > 2:
            return "Moderate"
        return "Low"

    def _generate_explanation(self,
                              Patent: Patent,
                              product_name: str,
                              product_description: str,
                              relevant_claims: List[str],) -> str:
        """生成侵權分析說明"""
        prompt = f"""
        Generate a concise explanation of why this product potentially infringes the patent.

        Product: {product_name}
        Description: {product_description}
        Patent title: {patent.title}
        Relevant claims: {', '.join(relevant_claims)}

        Format the explanation in 2-3 sentences focusing on specific technical similarities.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()
    
    def _extract_specific_features(self,
                                   product_description: str,
                                   patent: Patent) -> List[str]:
        """提取產品中可能侵權的具體特徵"""
        prompt = f"""
        List 3-5 specific technical features from the product that might infringe the patent.

        Product descriptin: {product_description}
        Patent title: {patent.title}
        Patent abstract: {patent.abstract}

        Format as a simple list of features, one per line.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        features = response.choices[0].message.content.strip().split('\n')
        return [f.strip('- ') for f in features]

    def analyze_product(self,
                        patent: Patent,
                        product_name: str,
                        product_description: str) -> InfringingProduct:
        """分析單個產品的侵權情況"""
        # 1. 找出相關的權利要求
        relevant_claims = self._get_relevant_claims(patent, product_description)
        # 2. 判斷親權程度
        infringement_likelihood = self._analyze_infringement_level(len(relevant_claims))
        # 3. 生成解釋說明
        explanation = self._generate_explanation(patent, product_name, product_description, relevant_claims)
        # 4. 提取具體特徵
        specific_features = self._extract_specific_features(product_description, patent)

        return InfringingProduct(
            product_name=product_name,
            infringement_likelihood=infringement_likelihood,
            relevant_claims=relevant_claims,
            explanation=explanation,
            specific_features=specific_features
        )

    def generate_infringement_report(self,
                                     patent_id: str,
                                     company_name: str) -> Optional[Dict]:
        """生成完整的侵權分析報告"""
        patent = Patent.query.filter_by(publication_number=patent_id).first()
        company = Company.query.filter_by(name=company_name).first()

        if not patent or not company:
            return None

        # 分析所有產品 
        product_analysis = []
        for product in company.products:
            analysis = self.analyze_product(patent, product['name'], product['description'])
            product_analysis.append(analysis)

        # 選出侵權可能性最高的兩個產品
        top_product = sorted(
            product_analysis,
            key=lambda x: (
                {"High": 3, "Moderate": 2, "Low": 1}[x.infringement_likelihood],
                len(x.relevant_claims)
            ),
            reverse=True
        )[:2]

        # 生成總體風險評估
        risk_prompt = f"""
        Generate an overall risk assessment for patent infringement based on these products:
        
        Patent: {patent.title} ({patent.publication_number})
        Company: {company.name}
        
        Products analyzed:
        {[p.product_name for p in product_analyses]}
        
        Top potentially infringing products:
        1. {top_products[0].product_name} - {top_products[0].infringement_likelihood} likelihood
        2. {top_products[1].product_name} - {top_products[1].infringement_likelihood} likelihood
        
        Format the assessment in 2-3 sentences.
        """

        risk_response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": risk_prompt}]
        )

        return {
            "analysis_id": str(hash(datetime.now().isoformat())),
            "patent_id": patent.publication_number,
            "patent_title": patent.title,
            "company_name": company.name,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "top_infringing_products": [
                {
                    "product_name": p.product_name,
                    "infringement_likelihood": p.infringement_likelihood,
                    "relevant_claims": p.relevant_claims,
                    "explanation": p.explanation,
                    "specific_features": p.specific_features
                }
                for p in top_products
            ],
            "overall_risk_assessment": risk_response.choices[0].message.content.strip()
        }