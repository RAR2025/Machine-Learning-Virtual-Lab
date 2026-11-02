import React from 'react';
import './NavigationBar.css';

const NAV_ITEMS = ['Aim', 'Theory', 'Pretest', 'Simulation', 'Posttest', 'Conclusion'];

export default function NavigationBar({ activeTab, onTabChange }) {
  return (
    <nav className="vlab-navigation" aria-label="Virtual lab sections">
      <div className="navigation-brand">ML Virtual Lab</div>
      <div className="navigation-tabs">
        {NAV_ITEMS.map((item) => {
          const tabId = item.toLowerCase();
          return (
            <button
              key={tabId}
              className={`navigation-tab ${activeTab === tabId ? 'active' : ''}`}
              onClick={() => onTabChange(tabId)}
              type="button"
            >
              {item}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
