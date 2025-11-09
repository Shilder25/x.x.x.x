import React from 'react';

type MarketData = {
  symbol: string;
  price: number;
  change: number;
};

interface MarketHeaderProps {
  data: MarketData[];
}

export default function MarketHeader({ data }: MarketHeaderProps) {
  // Ensure we show the right cryptos in the right order
  const orderedSymbols = ['BTC', 'ETH', 'SOL', 'BNB', 'DOGE', 'XRP'];
  
  const orderedData = orderedSymbols.map(symbol => {
    const found = data.find(d => d.symbol === symbol);
    return found || { symbol, price: 0, change: 0 };
  });

  return (
    <div className="market-header">
      <div className="alpha-container">
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          {orderedData.map((item) => (
            <div key={item.symbol} className="market-ticker">
              <span className="market-ticker-symbol">
                {getSymbolIcon(item.symbol)} {item.symbol}
              </span>
              <span className="market-ticker-price">
                ${item.price.toLocaleString()}
              </span>
              <span className={`market-ticker-change ${item.change >= 0 ? 'positive' : 'negative'}`}>
                {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function getSymbolIcon(symbol: string): string {
  const icons: { [key: string]: string } = {
    BTC: '₿',
    ETH: '♦',
    SOL: '◉',
    BNB: '◆',
    DOGE: 'Ð',
    XRP: '✕'
  };
  return icons[symbol] || '●';
}