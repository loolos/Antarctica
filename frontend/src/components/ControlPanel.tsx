import React, { useState, useEffect } from 'react';

interface ControlPanelProps {
  connected: boolean;
  onStart: () => void;
  onStop: () => void;
  onReset: () => void;
  onStep: () => void;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({
  connected,
  onStart,
  onStop,
  onReset,
  onStep,
}) => {
  const [speed, setSpeed] = useState(1.0);
  const [speedDisplay, setSpeedDisplay] = useState('1.0x');

  // Load current speed from backend on mount
  useEffect(() => {
    if (connected) {
      fetch('http://localhost:8000/speed')
        .then(res => res.json())
        .then(data => {
          setSpeed(data.speed);
          setSpeedDisplay(`${data.speed.toFixed(1)}x`);
        })
        .catch(err => console.error('Failed to get speed:', err));
    }
  }, [connected]);

  const handleSpeedChange = async (newSpeed: number) => {
    setSpeed(newSpeed);
    setSpeedDisplay(`${newSpeed.toFixed(1)}x`);
    
    try {
      const response = await fetch('http://localhost:8000/speed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ speed: newSpeed }),
      });
      if (!response.ok) {
        console.error('Failed to set speed');
      }
    } catch (error) {
      console.error('Failed to set speed:', error);
    }
  };

  const handleStart = async () => {
    try {
      const response = await fetch('http://localhost:8000/start', {
        method: 'POST',
      });
      if (response.ok) {
        onStart();
      }
    } catch (error) {
      console.error('Failed to start simulation:', error);
    }
  };

  const handleStop = async () => {
    try {
      const response = await fetch('http://localhost:8000/stop', {
        method: 'POST',
      });
      if (response.ok) {
        onStop();
      }
    } catch (error) {
      console.error('Failed to stop simulation:', error);
    }
  };

  const handleReset = async () => {
    try {
      const response = await fetch('http://localhost:8000/reset', {
        method: 'POST',
      });
      if (response.ok) {
        onReset();
      }
    } catch (error) {
      console.error('Failed to reset simulation:', error);
    }
  };

  return (
    <div
      style={{
        padding: '20px',
        background: '#2a2a3a',
        borderRadius: '8px',
        marginBottom: '20px',
      }}
    >
      <div style={{ marginBottom: '10px', color: connected ? '#00ff00' : '#ff0000' }}>
        Connection Status: {connected ? 'Connected' : 'Disconnected'}
      </div>
      
      {/* Speed Control */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', color: '#ffffff' }}>
          Simulation Speed: {speedDisplay}
        </label>
        <input
          type="range"
          min="0.1"
          max="10"
          step="0.1"
          value={speed}
          onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
          disabled={!connected}
          style={{
            width: '100%',
            height: '8px',
            borderRadius: '4px',
            background: connected ? '#4a9eff' : '#666',
            outline: 'none',
            opacity: connected ? 1 : 0.5,
            cursor: connected ? 'pointer' : 'not-allowed',
          }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '12px', color: '#aaa' }}>
          <span>0.1x (Slow)</span>
          <span>1.0x (Normal)</span>
          <span>10x (Fast)</span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button
          onClick={handleStart}
          disabled={!connected}
          style={{
            padding: '10px 20px',
            background: '#4a9eff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: connected ? 'pointer' : 'not-allowed',
            opacity: connected ? 1 : 0.5,
          }}
        >
          Start
        </button>
        <button
          onClick={handleStop}
          disabled={!connected}
          style={{
            padding: '10px 20px',
            background: '#ff6b6b',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: connected ? 'pointer' : 'not-allowed',
            opacity: connected ? 1 : 0.5,
          }}
        >
          Stop
        </button>
        <button
          onClick={handleReset}
          disabled={!connected}
          style={{
            padding: '10px 20px',
            background: '#ffa500',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: connected ? 'pointer' : 'not-allowed',
            opacity: connected ? 1 : 0.5,
          }}
        >
          Reset
        </button>
        <button
          onClick={onStep}
          disabled={!connected}
          style={{
            padding: '10px 20px',
            background: '#51cf66',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: connected ? 'pointer' : 'not-allowed',
            opacity: connected ? 1 : 0.5,
          }}
        >
          Step
        </button>
      </div>
    </div>
  );
};

