import React from 'react';

interface NavigationTabsProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export default function NavigationTabs({ activeSection, onSectionChange }: NavigationTabsProps) {
  const sections = ['LIVE', 'LEADERBOARD', 'BLOG', 'MODELS'];

  return (
    <div className="nav-container">
      {sections.map((section, index) => (
        <React.Fragment key={section}>
          <button
            className={`nav-tab ${activeSection === section ? 'active' : ''}`}
            onClick={() => onSectionChange(section)}
          >
            {section}
          </button>
          {index < sections.length - 1 && <div className="nav-separator" />}
        </React.Fragment>
      ))}
    </div>
  );
}