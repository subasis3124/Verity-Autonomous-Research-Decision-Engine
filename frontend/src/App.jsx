import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import SubmitQuery from './pages/SubmitQuery';
import QueryDetail from './pages/QueryDetail';
import ReportView from './pages/ReportView';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/submit"
            element={
              <ProtectedRoute>
                <SubmitQuery />
              </ProtectedRoute>
            }
          />
          <Route
            path="/queries/:id"
            element={
              <ProtectedRoute>
                <QueryDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports/:queryId"
            element={
              <ProtectedRoute>
                <ReportView />
              </ProtectedRoute>
            }
          />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
