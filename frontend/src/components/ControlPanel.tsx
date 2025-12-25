import React from 'react';

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

