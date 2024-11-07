from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from models import db, Patent, Company
import logging
import json
import openai

@dataclass
class InfringingProduct:
    product_name: str
    infringement_likelihood: str
    relevant_claims: List[str]
    explanation: str
    specific_features: List[str]

class PatentAnalyzer:
    def __init__(self, openai_api_key: str , log_level: int = logging.INFO):
        openai.api_key = openai_api_key
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

    def _get_relevant_claims(self, patent: Patent, product_description: str) -> List[str]:
        """分析產品描述與專利權利要求的相關性"""
        claims = json.loads(patent.claims)
        
        BATCH_SIZE = 5
        claim_batches = [claims[i:i + BATCH_SIZE] for i in range(0, len(claims), BATCH_SIZE)]

        relevant_claims = []

        for batch in claim_batches:
            # 構建批次處理的prompt
            claims_text = "\n".join([
                f"Claim {claim['num']}: {claim['text']}"
                for claim in batch
            ])

            prompt = f"""
            Analyze if the product potentially infringes each of the following patent claims.
            Respond with ONLY a comma-separated list of YES or NO for each claim in order.

            Product description: {product_description}
 
            Claims to analyze:
            {claims_text}
            """

            response = openai.Completion.create( 
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=60,
                temperature=0.3
            )

            # 解析回應
            results = [r.strip().upper() for r in response.choices[0].text.split(',')]
        
            # 將相關的claims加入結果
            for claim, result in zip(batch, results):
                if 'YES' in result:
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
                              patent: Patent,
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

        response = openai.Completion.create( 
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )

        return response.choices[0].text.strip()
    
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

        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=150,
            temperature=0.5
        )

        features = response.choices[0].text.strip().split('\n')
        return [f.strip('- ') for f in features]

    def analyze_product(self,
                        patent: Patent,
                        product_name: str,
                        product_description: str) -> InfringingProduct:
        """分析單個產品的侵權情況"""
        # 1. 找出相關的權利要求

        self.logger.info(f"fox")
        relevant_claims = self._get_relevant_claims(patent, product_description)
        # 2. 判斷親權程度

        self.logger.info(f"fox1")
        infringement_likelihood = self._analyze_infringement_level(len(relevant_claims))
        # 3. 生成解釋說明

        self.logger.info(f"fox2")
        explanation = self._generate_explanation(patent, product_name, product_description, relevant_claims)
        # 4. 提取具體特徵

        self.logger.info(f"fox3")
        specific_features = self._extract_specific_features(product_description, patent)


        self.logger.info(f"fox4")
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
        product = company.products[0]
        #for product in company.products:
        analysis = self.analyze_product(patent, product['name'], product['description'])
        product_analysis.append(analysis)

        self.logger.info(f"fox5")

        # 選出侵權可能性最高的兩個產品
        top_products = sorted(
            product_analysis,
            key=lambda x: (
                {"High": 3, "Moderate": 2, "Low": 1}[x.infringement_likelihood],
                len(x.relevant_claims)
            ),
            reverse=True
        )[:2]

        all_products_list = "\n".join([p.product_name for p in product_analysis])

        top_products_list = []
        for i, p in enumerate(top_products, 1):
            top_products_list.append(f"{i}. {p.product_name} - {p.infringement_likelihood} likelihood")
        top_products_text = "\n".join(top_products_list)

        # 生成總體風險評估
        risk_prompt = f"""
        Generate an overall risk assessment for patent infringement based on these products:
        
        Patent: {patent.title} ({patent.publication_number})
        Company: {company.name}
        
        Products analyzed:
        {all_products_list}
        
        Top potentially infringing products:
        {top_products_text}

        Format the assessment in 2-3 sentences.
        """

        risk_response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=risk_prompt,
            max_tokens=200,
            temperature=0.7
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
            "overall_risk_assessment": risk_response.choices[0].text.strip()
        }