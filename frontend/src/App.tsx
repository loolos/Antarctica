import React from 'react';
import './App.css';
import { SimulationCanvas } from './components/SimulationCanvas';
import { ControlPanel } from './components/ControlPanel';
import { useWebSocket } from './hooks/useWebSocket';
import { WS_URL } from './config';

function App() {
  const { state, connected, sendStep } = useWebSocket(WS_URL);
  return (
    <div className="App">
      <header className="App-header">
        <h1>Antarctic Ecosystem Simulation</h1>
      </header>
      <main className="App-main">
        <ControlPanel
          connected={connected}
          onReset={() => {
            window.location.reload();
          }}
          onStep={sendStep}
        />
        <p className="mobile-scroll-hint">
          Drag horizontally on mobile to view the full simulation area
        </p>
        <div className="canvas-container">
          <SimulationCanvas
            worldState={state}
            width={state?.environment?.width ?? 1280}
            height={state?.environment?.height ?? 960}
          />
        </div>
      </main>
    </div>
  );
}

export default App;

