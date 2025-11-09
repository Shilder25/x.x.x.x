import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ChartData {
  [key: string]: {
    color: string;
    data: Array<{ date: string; value: number }>;
  };
}

interface PerformanceChartProps {
  data: ChartData;
  metrics: Array<{
    firm: string;
    color: string;
    total_value: number;
  }>;
}

export default function PerformanceChart({ data, metrics }: PerformanceChartProps) {
  // Prepare chart data for Recharts
  const prepareChartData = () => {
    if (!data || Object.keys(data).length === 0) return [];
    
    const firstFirm = Object.keys(data)[0];
    if (!data[firstFirm]) return [];
    
    return data[firstFirm].data.map((point, index) => {
      const dataPoint: any = { 
        date: formatDate(point.date),
        rawDate: point.date
      };
      Object.keys(data).forEach(firm => {
        dataPoint[firm] = data[firm].data[index]?.value || 0;
      });
      return dataPoint;
    });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return `${date.toLocaleDateString('en-US', { month: 'short' })} ${date.getDate()}`;
  };

  const formatYAxis = (value: number) => {
    return `$${(value / 1000).toFixed(0)}k`;
  };

  const chartData = prepareChartData();

  // Get the latest values for legend badges
  const getLatestValue = (firm: string) => {
    const metric = metrics.find(m => m.firm === firm);
    return metric ? metric.total_value : 0;
  };

  const firmColors: { [key: string]: string } = {
    'Gemini': '#8B5CF6',
    'ChatGPT': '#3B82F6',
    'Qwen': '#F97316',
    'Deepseek': '#000000',
    'Grok': '#06B6D4'
  };

  return (
    <div className="chart-panel">
      <div className="chart-header">
        <h3 className="chart-title">TOTAL ACCOUNT VALUE</h3>
        <div className="chart-controls">
          <div className="time-selector">
            <button className="time-option active">ALL</button>
            <button className="time-option">72H</button>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart 
          data={chartData} 
          margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
        >
          <CartesianGrid 
            strokeDasharray="0" 
            stroke="#E5E7EB" 
            vertical={true}
            horizontal={true}
          />
          <XAxis 
            dataKey="date"
            tick={{ fontSize: 11, fill: '#6B7280' }}
            tickLine={false}
            axisLine={{ stroke: '#E5E7EB' }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#6B7280' }}
            tickFormatter={formatYAxis}
            tickLine={false}
            axisLine={{ stroke: '#E5E7EB' }}
            domain={['dataMin - 1000', 'dataMax + 1000']}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '2px solid #000',
              borderRadius: '0px',
              padding: '8px 12px',
              fontSize: '12px'
            }}
            labelStyle={{ color: '#000', fontWeight: 600, marginBottom: '4px' }}
            formatter={(value: number) => [`$${value.toLocaleString()}`, '']}
          />
          
          {Object.keys(data).map(firm => (
            <Line
              key={firm}
              type="monotone"
              dataKey={firm}
              stroke={firmColors[firm] || '#000'}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, strokeWidth: 0 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      {/* Legend Badges */}
      <div className="legend-container">
        {Object.keys(data).map(firm => {
          const latestValue = getLatestValue(firm);
          const color = firmColors[firm] || '#000';
          
          return (
            <div key={firm} className="legend-badge">
              <div 
                className="legend-color" 
                style={{ backgroundColor: color }}
              />
              <span className="legend-label">{firm}</span>
              <span className="legend-value">
                ${latestValue.toLocaleString()}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}