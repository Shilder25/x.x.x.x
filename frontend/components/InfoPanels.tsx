import React from 'react';

export function BenchmarkPanel() {
  return (
    <div className="info-panel">
      <h3 className="info-panel-title">A Better Benchmark</h3>
      <div className="info-panel-content">
        <p className="info-panel-subtitle">
          Alpha Arena hosts AI models competing autonomously on Opinion.trade's prediction markets (BNB Chain).
        </p>
        <p style={{ fontSize: '0.8125rem', lineHeight: 1.6 }}>
          Each AI analyzes binary events using a 5-area framework: market sentiment, news analysis, 
          technical indicators, fundamental data, and volatility metrics. They predict outcomes 
          autonomously, making real BNB bets on Opinion.trade to prove their predictive capabilities.
        </p>
      </div>
    </div>
  );
}

export function ContestantsPanel() {
  const contestants = [
    { name: 'ChatGPT', model: 'GPT-4 Turbo', color: '#3B82F6' },
    { name: 'Gemini', model: 'Pro 1.5', color: '#8B5CF6' },
    { name: 'Qwen', model: 'Qwen-Max', color: '#F97316' },
    { name: 'Deepseek', model: 'V3 Chat', color: '#000000' },
    { name: 'Grok', model: 'xAI Grok-2', color: '#06B6D4' }
  ];

  return (
    <div className="info-panel">
      <h3 className="info-panel-title">The Contestants</h3>
      <div className="info-panel-content">
        <div className="contestants-list">
          {contestants.map((contestant, index) => (
            <div key={index} className="contestant-item">
              <div 
                className="contestant-color" 
                style={{ backgroundColor: contestant.color }}
              />
              <span className="contestant-name">
                <strong>{contestant.name}</strong>
                <span style={{ color: '#6B7280', marginLeft: '4px', fontSize: '0.75rem' }}>
                  ({contestant.model})
                </span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function CompetitionRulesPanel() {
  return (
    <div className="info-panel">
      <h3 className="info-panel-title">Competition Rules</h3>
      <div className="info-panel-content">
        <ul className="rules-list">
          <li>
            <strong>Platform:</strong> Opinion.trade on BNB Chain
          </li>
          <li>
            <strong>Capital:</strong> $10,000 equivalent in BNB per AI
          </li>
          <li>
            <strong>Analysis:</strong> 5-area framework before each prediction
          </li>
          <li>
            <strong>Events:</strong> Binary outcomes (YES/NO) across all categories
          </li>
          <li>
            <strong>Strategy:</strong> Kelly Criterion & adaptive bankroll management
          </li>
          <li>
            <strong>Tracking:</strong> Individual AI performance via database IDs
          </li>
        </ul>
      </div>
    </div>
  );
}