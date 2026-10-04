import { useState } from 'react';

const CELL_META = [
  { row: 0, col: 0, label: 'True Negative', shortLabel: 'TN', className: 'correct' },
  { row: 0, col: 1, label: 'False Positive', shortLabel: 'FP', className: 'error' },
  { row: 1, col: 0, label: 'False Negative', shortLabel: 'FN', className: 'error' },
  { row: 1, col: 1, label: 'True Positive', shortLabel: 'TP', className: 'correct' }
];

export default function ConfusionMatrix({ matrix }) {
  const [hoveredCell, setHoveredCell] = useState(null);
  const values = matrix || [[0, 0], [0, 0]];
  const activeCell = CELL_META.find((cell) => cell.label === hoveredCell);

  return (
    <div className="confusion-matrix-wrap">
      <svg className="confusion-matrix" viewBox="0 0 240 154" role="grid" aria-label="Confusion matrix">
        <text className="cm-axis-title" x="139" y="12" textAnchor="middle">Predicted</text>
        <text className="cm-axis-title" x="12" y="84" textAnchor="middle" transform="rotate(-90 12 84)">Actual</text>
        <text className="cm-axis-label" x="109" y="30" textAnchor="middle">0</text>
        <text className="cm-axis-label" x="176" y="30" textAnchor="middle">1</text>
        <text className="cm-axis-label" x="35" y="67" textAnchor="middle">0</text>
        <text className="cm-axis-label" x="35" y="121" textAnchor="middle">1</text>
        {CELL_META.map(({ row, col, label, shortLabel, className }) => {
          const x = 76 + col * 67;
          const y = 40 + row * 54;
          const count = values[row]?.[col] ?? 0;
          const isHovered = hoveredCell === label;

          return (
            <g
              key={label}
              className={`cm-svg-cell ${className} ${isHovered ? 'is-hovered' : ''}`}
              role="gridcell"
              tabIndex="0"
              onMouseEnter={() => setHoveredCell(label)}
              onMouseLeave={() => setHoveredCell(null)}
              onFocus={() => setHoveredCell(label)}
              onBlur={() => setHoveredCell(null)}
              aria-label={`${label}: ${count}`}
            >
              <rect x={x} y={y} width="61" height="47" rx="5" />
              <text className="cm-cell-count" x={x + 30.5} y={y + 22} textAnchor="middle">{count}</text>
              <text className="cm-cell-label" x={x + 30.5} y={y + 36} textAnchor="middle">{shortLabel}</text>
            </g>
          );
        })}
      </svg>
      <div className={`cm-hover-detail ${activeCell ? 'is-visible' : ''}`} aria-live="polite">
        {activeCell ? `${activeCell.label}: ${values[activeCell.row]?.[activeCell.col] ?? 0}` : 'Hover a cell for details'}
      </div>
    </div>
  );
}
