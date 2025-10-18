import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { BrowserRouter } from 'react-router-dom';
import App from './app/App';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#b44c3b'
    },
    secondary: {
      main: '#f0a202'
    },
    background: {
      default: '#fff9f4',
      paper: '#ffffff'
    },
    text: {
      primary: '#2f1b16',
      secondary: '#5a4038'
    }
  },
  typography: {
    fontFamily: '"Inter", "Helvetica", "Arial", sans-serif'
  },
  shape: {
    borderRadius: 16
  }
});
const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  </React.StrictMode>
);
