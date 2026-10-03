import React, { useRef, useEffect, useState, useCallback } from 'react';
import './Canvas.css';
import Toolbar from './Toolbar';

export default function Canvas({
  points,
  setPoints,
  activeClass,
  setActiveClass,
  isEraser,
  setIsEraser,
  boundaryData,
  onResetPoints,
  onLoadPreset
}) {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const [showGrid, setShowGrid] = useState(true);
  const [hoverCoord, setHoverCoord] = useState(null);
  const [hoveredPointIndex, setHoveredPointIndex] = useState(null);
  const isMouseDownRef = useRef(false);
  const lastPlacedRef = useRef(null);

  // Undo stack
  const [history, setHistory] = useState([]);

  // Push current state to undo stack before mutating
  const recordHistory = useCallback(() => {
    setHistory((prev) => [...prev.slice(-30), points]);
  }, [points]);

  const handleUndo = useCallback(() => {
    if (history.length > 0) {
      const previous = history[history.length - 1];
      setHistory((prev) => prev.slice(0, -1));
      setPoints(previous);
    }
  }, [history, setPoints]);

  // Keyboard shortcut for Undo (Ctrl+Z / Cmd+Z)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        handleUndo();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleUndo]);

  // Add point with distance throttle to prevent clutter during drag
  const addPointAt = useCallback((clientX, clientY) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const px = clientX - rect.left;
    const py = clientY - rect.top;

    if (px < 0 || px > rect.width || py < 0 || py > rect.height) return;

    if (isEraser) {
      // Erase points within 20px radius
      const normalizedRadius = 20 / Math.min(rect.width, rect.height);
      const normX = px / rect.width;
      const normY = py / rect.height;

      setPoints((prev) =>
        prev.filter((p) => {
          const dx = p.x - normX;
          const dy = p.y - normY;
          return Math.sqrt(dx * dx + dy * dy) > normalizedRadius;
        })
      );
      return;
    }

    // Normal placement
    const normX = Math.max(0.02, Math.min(0.98, px / rect.width));
    const normY = Math.max(0.02, Math.min(0.98, py / rect.height));

    if (lastPlacedRef.current) {
      const dx = (normX - lastPlacedRef.current.x) * rect.width;
      const dy = (normY - lastPlacedRef.current.y) * rect.height;
      if (Math.sqrt(dx * dx + dy * dy) < 22) {
        return; // Throttle: too close to last placed point
      }
    }

    recordHistory();
    lastPlacedRef.current = { x: normX, y: normY };
    setPoints((prev) => [...prev, { x: normX, y: normY, label: activeClass }]);
  }, [activeClass, isEraser, recordHistory, setPoints]);

  // Mouse / Pointer handlers
  const handlePointerDown = (e) => {
    if (e.button !== 0) return; // Only left click
    isMouseDownRef.current = true;
    lastPlacedRef.current = null;
    addPointAt(e.clientX, e.clientY);
  };

  const handlePointerMove = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const px = e.clientX - rect.left;
    const py = e.clientY - rect.top;

    if (px >= 0 && px <= rect.width && py >= 0 && py <= rect.height) {
      const nx = px / rect.width;
      const ny = py / rect.height;
      setHoverCoord({ x: nx, y: 1 - ny }); // Display standard Cartesian Y (0 at bottom)

      // Check for point hover
      const hitRadius = 14 / Math.min(rect.width, rect.height);
      const hitIndex = points.findIndex((p) => {
        const dx = p.x - nx;
        const dy = p.y - ny;
        return Math.sqrt(dx * dx + dy * dy) <= hitRadius;
      });
      setHoveredPointIndex(hitIndex >= 0 ? hitIndex : null);
    } else {
      setHoverCoord(null);
      setHoveredPointIndex(null);
    }

    if (isMouseDownRef.current) {
      addPointAt(e.clientX, e.clientY);
    }
  };

  const handlePointerUp = () => {
    isMouseDownRef.current = false;
    lastPlacedRef.current = null;
  };

  // High-DPI Canvas Rendering Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = container.getBoundingClientRect();

    canvas.width = Math.floor(rect.width * dpr);
    canvas.height = Math.floor(rect.height * dpr);
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    ctx.save();
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;

    // 1. Clear background
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, w, h);

    // 2. Render Boundary Grid if available
    if (boundaryData && boundaryData.grid && boundaryData.resolution) {
      const res = boundaryData.resolution;
      const cellW = w / res;
      const cellH = h / res;
      const grid = boundaryData.grid; // 2D array of predictions [0 or 1] or probabilities

      for (let r = 0; r < res; r++) {
        for (let c = 0; c < res; c++) {
          const val = grid[r][c];
          // Semi-transparent pastel fill for regions
          ctx.fillStyle = val === 0 ? 'rgba(37, 99, 235, 0.16)' : 'rgba(249, 115, 22, 0.16)';
          ctx.fillRect(c * cellW, r * cellH, cellW + 0.6, cellH + 0.6);
        }
      }
    }

    // 3. Render Subtle Coordinate Grid
    if (showGrid) {
      ctx.strokeStyle = '#F1F5F9';
      ctx.lineWidth = 1;
      const step = 40;

      for (let x = step; x < w; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = step; y < h; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      // Center crosshair (0.5, 0.5)
      ctx.strokeStyle = '#E2E8F0';
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(w / 2, 0);
      ctx.lineTo(w / 2, h);
      ctx.moveTo(0, h / 2);
      ctx.lineTo(w, h / 2);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // 4. Render Data Points
    points.forEach((p, index) => {
      const cx = p.x * w;
      const cy = p.y * h;
      const isClassA = p.label === 0;
      const isHovered = hoveredPointIndex === index;

      // Glow halo
      ctx.beginPath();
      ctx.arc(cx, cy, isHovered ? 12 : 9, 0, Math.PI * 2);
      ctx.fillStyle = isClassA ? 'rgba(37, 99, 235, 0.22)' : 'rgba(249, 115, 22, 0.22)';
      ctx.fill();

      // Main Point Circle
      ctx.beginPath();
      ctx.arc(cx, cy, 5.5, 0, Math.PI * 2);
      ctx.fillStyle = isClassA ? '#2563EB' : '#F97316';
      ctx.fill();

      // White outline & inner dot for crisp enterprise aesthetic
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#FFFFFF';
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(cx, cy, 1.5, 0, Math.PI * 2);
      ctx.fillStyle = '#FFFFFF';
      ctx.fill();
    });

    ctx.restore();
  }, [points, boundaryData, showGrid, hoveredPointIndex]);

  return (
    <div className="vlab-canvas-host">
      {/* Canvas Action Bar */}
      <Toolbar
        activeClass={activeClass}
        setActiveClass={setActiveClass}
        isEraser={isEraser}
        setIsEraser={setIsEraser}
        onClear={() => {
          recordHistory();
          setPoints([]);
        }}
        onUndo={handleUndo}
        canUndo={history.length > 0}
        onLoadPreset={(id) => {
          recordHistory();
          onLoadPreset(id);
        }}
        showGrid={showGrid}
        setShowGrid={setShowGrid}
        hoverCoord={hoverCoord}
      />

      {/* Main Drawing Surface */}
      <div 
        className={`canvas-viewport ${isEraser ? 'cursor-eraser' : 'cursor-crosshair'}`} 
        ref={containerRef}
      >
        <canvas
          ref={canvasRef}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerLeave={handlePointerUp}
        />

        {/* Empty Canvas Friendly Overlay Hint */}
        {points.length === 0 && (
          <div className="canvas-empty-overlay">
            <div className="empty-icon-card">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
            </div>
            <div className="empty-title">Canvas is Ready</div>
            <div className="empty-subtitle">
              Click anywhere to add <b>Class A</b> or <b>Class B</b> points, or select a preset above.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
