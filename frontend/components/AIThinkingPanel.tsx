'use client';

import { useState, useEffect } from 'react';

interface AIAnalysis {
  firm_name: string;
  event_description: string;
  category: string;
  probability: number;
  confidence: number;
  sentiment_score: number | null;
  sentiment_analysis: string | null;
  news_score: number | null;
  news_analysis: string | null;
  technical_score: number | null;
  technical_analysis: string | null;
  fundamental_score: number | null;
  fundamental_analysis: string | null;
  volatility_score: number | null;
  volatility_analysis: string | null;
  execution_timestamp: string;
}

export default function AIThinkingPanel() {
  const [thinking, setThinking] = useState<AIAnalysis[]>([]);
  const [selectedAI, setSelectedAI] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const AI_COLORS: { [key: string]: string } = {
    'ChatGPT': '#3B82F6',
    'Gemini': '#8B5CF6',
    'Qwen': '#F97316',
    'Deepseek': '#000000',
    'Grok': '#06B6D4'
  };

  useEffect(() => {
    fetchAIThinking();
    const interval = setInterval(fetchAIThinking, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAIThinking = async () => {
    try {
      const response = await fetch('/api/ai-thinking');
      if (response.ok) {
        const data = await response.json();
        setThinking(data);
        setLoading(false);
      }
    } catch (error) {
      console.error('Error fetching AI thinking:', error);
      setLoading(false);
    }
  };

  const getScoreColor = (score: number | null) => {
    if (!score) return '#6B7280';
    if (score >= 7) return '#10B981';
    if (score >= 5) return '#F59E0B';
    return '#EF4444';
  };

  const selectedAnalysis = selectedAI 
    ? thinking.find(t => t.firm_name === selectedAI) 
    : null;

  return (
    <div style={{
      border: '2px solid #000',
      background: '#fff',
      marginTop: 0
    }}>
      <div style={{
        padding: '1rem 1.5rem',
        borderBottom: '2px solid #000',
        background: '#000',
        color: '#fff',
        fontWeight: 600,
        fontSize: '0.875rem',
        letterSpacing: '0.05em'
      }}>
        AI REAL-TIME ANALYSIS (5-AREA FRAMEWORK)
      </div>

      {loading ? (
        <div style={{ padding: '2rem', textAlign: 'center', color: '#6B7280' }}>
          Loading AI analysis...
        </div>
      ) : thinking.length === 0 ? (
        <div style={{ padding: '2rem', textAlign: 'center', color: '#6B7280' }}>
          No AI predictions yet. System will begin analysis when enabled.
        </div>
      ) : (
        <div style={{ padding: '1.5rem' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(5, 1fr)',
            gap: '0.75rem',
            marginBottom: '1.5rem'
          }}>
            {thinking.map((ai) => (
              <button
                key={ai.firm_name}
                onClick={() => setSelectedAI(ai.firm_name === selectedAI ? null : ai.firm_name)}
                style={{
                  padding: '0.75rem',
                  border: `2px solid ${selectedAI === ai.firm_name ? AI_COLORS[ai.firm_name] : '#E5E7EB'}`,
                  background: selectedAI === ai.firm_name ? `${AI_COLORS[ai.firm_name]}10` : '#fff',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  fontWeight: 500,
                  fontSize: '0.875rem'
                }}
              >
                <div style={{ color: AI_COLORS[ai.firm_name], marginBottom: '0.25rem' }}>
                  {ai.firm_name}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#6B7280' }}>
                  {ai.probability ? `${(ai.probability * 100).toFixed(0)}% confidence` : 'Analyzing...'}
                </div>
              </button>
            ))}
          </div>

          {selectedAnalysis && (
            <div style={{
              border: '2px solid #000',
              padding: '1.5rem',
              background: '#F9FAFB'
            }}>
              <div style={{
                marginBottom: '1rem',
                paddingBottom: '1rem',
                borderBottom: '1px solid #E5E7EB'
              }}>
                <h3 style={{
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color: '#000',
                  marginBottom: '0.5rem'
                }}>
                  EVENT: {selectedAnalysis.event_description}
                </h3>
                <div style={{ fontSize: '0.75rem', color: '#6B7280' }}>
                  Category: {selectedAnalysis.category} | Confidence: {selectedAnalysis.confidence}/10
                </div>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(5, 1fr)',
                gap: '1rem'
              }}>
                <div>
                  <div style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: '#000',
                    marginBottom: '0.5rem'
                  }}>
                    1. SENTIMENT
                  </div>
                  <div style={{
                    fontSize: '1.5rem',
                    fontWeight: 600,
                    color: getScoreColor(selectedAnalysis.sentiment_score),
                    marginBottom: '0.5rem'
                  }}>
                    {selectedAnalysis.sentiment_score ? `${selectedAnalysis.sentiment_score.toFixed(1)}/10` : 'N/A'}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#6B7280', lineHeight: '1.4' }}>
                    {selectedAnalysis.sentiment_analysis || 'No analysis available'}
                  </div>
                </div>

                <div>
                  <div style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: '#000',
                    marginBottom: '0.5rem'
                  }}>
                    2. NEWS
                  </div>
                  <div style={{
                    fontSize: '1.5rem',
                    fontWeight: 600,
                    color: getScoreColor(selectedAnalysis.news_score),
                    marginBottom: '0.5rem'
                  }}>
                    {selectedAnalysis.news_score ? `${selectedAnalysis.news_score.toFixed(1)}/10` : 'N/A'}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#6B7280', lineHeight: '1.4' }}>
                    {selectedAnalysis.news_analysis || 'No analysis available'}
                  </div>
                </div>

                <div>
                  <div style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: '#000',
                    marginBottom: '0.5rem'
                  }}>
                    3. TECHNICAL
                  </div>
                  <div style={{
                    fontSize: '1.5rem',
                    fontWeight: 600,
                    color: getScoreColor(selectedAnalysis.technical_score),
                    marginBottom: '0.5rem'
                  }}>
                    {selectedAnalysis.technical_score ? `${selectedAnalysis.technical_score.toFixed(1)}/10` : 'N/A'}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#6B7280', lineHeight: '1.4' }}>
                    {selectedAnalysis.technical_analysis || 'No analysis available'}
                  </div>
                </div>

                <div>
                  <div style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: '#000',
                    marginBottom: '0.5rem'
                  }}>
                    4. FUNDAMENTAL
                  </div>
                  <div style={{
                    fontSize: '1.5rem',
                    fontWeight: 600,
                    color: getScoreColor(selectedAnalysis.fundamental_score),
                    marginBottom: '0.5rem'
                  }}>
                    {selectedAnalysis.fundamental_score ? `${selectedAnalysis.fundamental_score.toFixed(1)}/10` : 'N/A'}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#6B7280', lineHeight: '1.4' }}>
                    {selectedAnalysis.fundamental_analysis || 'No analysis available'}
                  </div>
                </div>

                <div>
                  <div style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: '#000',
                    marginBottom: '0.5rem'
                  }}>
                    5. VOLATILITY
                  </div>
                  <div style={{
                    fontSize: '1.5rem',
                    fontWeight: 600,
                    color: getScoreColor(selectedAnalysis.volatility_score),
                    marginBottom: '0.5rem'
                  }}>
                    {selectedAnalysis.volatility_score ? `${selectedAnalysis.volatility_score.toFixed(1)}/10` : 'N/A'}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#6B7280', lineHeight: '1.4' }}>
                    {selectedAnalysis.volatility_analysis || 'No analysis available'}
                  </div>
                </div>
              </div>
            </div>

            {selectedAnalysis.probability_reasoning && (
              <div style={{
                marginTop: '1.5rem',
                padding: '1rem',
                background: '#FEF3C7',
                border: '2px solid #F59E0B'
              }}>
                <div style={{
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: '#92400E',
                  marginBottom: '0.5rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  💡 Probability Calculation Reasoning
                </div>
                <div style={{
                  fontSize: '0.875rem',
                  color: '#78350F',
                  lineHeight: '1.6'
                }}>
                  {selectedAnalysis.probability_reasoning}
                </div>
              </div>
            )}

            {selectedAnalysis.market_volume && (
              <div style={{
                marginTop: '1rem',
                padding: '0.75rem',
                background: '#EFF6FF',
                border: '1px solid #3B82F6',
                fontSize: '0.75rem',
                color: '#1E40AF'
              }}>
                <strong>Opinion.trade Market Volume:</strong> ${selectedAnalysis.market_volume.toLocaleString()}
              </div>
            )}
          )}

          {!selectedAnalysis && (
            <div style={{
              padding: '2rem',
              textAlign: 'center',
              color: '#6B7280',
              fontSize: '0.875rem'
            }}>
              Click on an AI above to view their detailed 5-area analysis and probability reasoning
            </div>
          )}
        </div>
      )}
    </div>
  );
}
