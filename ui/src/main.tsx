import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { App } from './app/App';
import { SystemThemeProvider } from './providers/system-theme/SystemThemeProvider';
import './styles/global.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SystemThemeProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </SystemThemeProvider>
  </StrictMode>,
);
