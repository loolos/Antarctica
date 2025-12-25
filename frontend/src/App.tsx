import React, { useState } from 'react';
import './App.css';
import { SimulationCanvas } from './components/SimulationCanvas';
import { ControlPanel } from './components/ControlPanel';
import { useWebSocket } from './hooks/useWebSocket';

function App() {
  const { state, connected, sendStep } = useWebSocket('ws://localhost:8000/ws');
  const [isRunning, setIsRunning] = useState(false);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Antarctic Ecosystem Simulation</h1>
      </header>
      <main className="App-main">
        <ControlPanel
          connected={connected}
          onStart={() => setIsRunning(true)}
          onStop={() => setIsRunning(false)}
          onReset={() => {
            setIsRunning(false);
            window.location.reload();
          }}
          onStep={sendStep}
        />
        <div className="canvas-container">
          <SimulationCanvas worldState={state} />
        </div>
      </main>
    </div>
  );
}

export default App;

