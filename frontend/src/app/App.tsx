import { Navigate, Route, Routes } from 'react-router-dom';

import AuthPage from '../features/auth/AuthPage';
import LandingPage from '../features/landing/LandingPage';
import PreferencesPage from '../features/preferences/PreferencesPage';
import { RequireAuth } from './RequireAuth';

const App = () => (
  <Routes>
    <Route path="/" element={<LandingPage />} />
    <Route path="/auth" element={<AuthPage />} />
    <Route
      path="/preferences"
      element={
        <RequireAuth>
          <PreferencesPage />
        </RequireAuth>
      }
    />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

export default App;
