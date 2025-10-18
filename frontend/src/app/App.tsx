import { Navigate, Route, Routes } from 'react-router-dom';
import LandingPage from '../features/landing/LandingPage';
import PreferencesPage from '../features/preferences/PreferencesPage';

const App = () => (
  <Routes>
    <Route path="/" element={<LandingPage />} />
    <Route path="/preferences" element={<PreferencesPage />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

export default App;
