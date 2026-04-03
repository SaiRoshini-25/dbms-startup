import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./components/AppShell";
import FundingPage from "./pages/FundingPage";
import LoginPage from "./pages/LoginPage";
import MyStartupsPage from "./pages/MyStartupsPage";
import NotificationsPage from "./pages/NotificationsPage";
import OverviewPage from "./pages/OverviewPage";
import MyInterestsPage from "./pages/MyInterestsPage";
import PortfolioPage from "./pages/PortfolioPage";
import RegisterPage from "./pages/RegisterPage";
import StartupsPage from "./pages/StartupsPage";
import { AuthProvider, useAuth } from "./auth";

function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

function RoleRoute({ allowedRoles, children }) {
  const { user } = useAuth();
  return allowedRoles.includes(user?.role) ? children : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <AppShell />
            </PrivateRoute>
          }
        >
          <Route index element={<OverviewPage />} />
          <Route path="startups" element={<StartupsPage />} />
          <Route
            path="my-startups"
            element={
              <RoleRoute allowedRoles={["STARTUP_REP"]}>
                <MyStartupsPage />
              </RoleRoute>
            }
          />
          <Route
            path="funding"
            element={
              <RoleRoute allowedRoles={["ADMIN"]}>
                <FundingPage />
              </RoleRoute>
            }
          />
          <Route
            path="interests"
            element={
              <RoleRoute allowedRoles={["INVESTOR"]}>
                <MyInterestsPage />
              </RoleRoute>
            }
          />
          <Route
            path="portfolio"
            element={
              <RoleRoute allowedRoles={["INVESTOR"]}>
                <PortfolioPage />
              </RoleRoute>
            }
          />
          <Route path="notifications" element={<NotificationsPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
