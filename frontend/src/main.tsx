import React from 'react';
import ReactDOM from 'react-dom/client';
import './style.css';

function App() {
  return (
    <main className="screen">
      <section className="status-card" aria-labelledby="page-title">
        <div className="status-icon" aria-hidden="true">✓</div>
        <p className="eyebrow">ENVIRONNEMENT DE DÉVELOPPEMENT</p>
        <h1 id="page-title">REVMA V2</h1>
        <p className="status-message">— Environnement opérationnel</p>
        <div className="service-status"><span className="pulse" /> Services prêts</div>
      </section>
      <footer>Infrastructure Docker · Frontend React · API FastAPI</footer>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><App /></React.StrictMode>,
);
