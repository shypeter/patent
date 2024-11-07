import { useState } from 'react';

interface AnalysisResult {
  analysis_id: string;
  patent_id: string;
  patent_title: string;
  company_name: string;
  analysis_date: string;
  top_infringing_products: Array<{
    product_name: string;
    infringement_likelihood: string;
    relevant_claims: string[];
    explanation: string;
    specific_features: string[];
  }>;
  overall_risk_assessment: string;
}

export default function PatentAnalysis() {
  const [patentId, setPatentId] = useState<string>('');
  const [companyName, setCompanyName] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>('');

  const analyzePatent = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:4000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patent_id: patentId,
          company_name: companyName,
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed');
      }

      setResult(data as AnalysisResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="bg-white shadow-lg rounded-lg p-6">
        <div className="flex items-center gap-2 mb-6">
          <h1 className="text-2xl font-bold">Patent Infringement Analysis</h1>
        </div>

        <form onSubmit={analyzePatent} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2" htmlFor="patentId">
              Patent ID
            </label>
            <input
              id="patentId"
              type="text"
              value={patentId}
              onChange={(e) => setPatentId(e.target.value)}
              placeholder="e.g. US-RE49889-E1"
              className="w-full p-2 border rounded"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2" htmlFor="companyName">
              Company Name
            </label>
            <input
              id="companyName"
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Walmart Inc."
              className="w-full p-2 border rounded"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:bg-blue-300"
          >
            {loading ? 'Analyzing...' : 'Analyze Patent'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-4 space-y-4">
            <h3 className="text-lg font-medium">Analysis Result</h3>
            <div className="bg-gray-50 p-4 rounded border">
              <pre className="whitespace-pre-wrap overflow-x-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}