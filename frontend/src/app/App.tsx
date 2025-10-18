import { Navigate, Route, Routes } from 'react-router-dom';

import AuthPage from '../features/auth/AuthPage';
import LandingPage from '../features/landing/LandingPage';
import PreferencesPage from '../features/preferences/PreferencesPage';
import TodayPage from '../features/plans/TodayPage';
import ProfilePage from '../features/profile/ProfilePage';
import MainLayout from './MainLayout';
import { RequireAuth } from './RequireAuth';

const App = () => (
  <Routes>
    <Route path="/auth" element={<AuthPage />} />
    <Route element={<MainLayout />}>
      <Route path="/" element={<LandingPage />} />
      <Route
        path="/preferences"
        element={
          <RequireAuth>
            <PreferencesPage />
          </RequireAuth>
        }
      />
      <Route
        path="/plan/today"
        element={
          <RequireAuth>
            <TodayPage />
          </RequireAuth>
        }
      />
      <Route
        path="/profile"
        element={
          <RequireAuth>
            <ProfilePage />
          </RequireAuth>
        }
      />
    </Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

export default App;
