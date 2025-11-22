import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import SubmitRequest from './pages/SubmitRequest';
import CategoryManagement from './pages/CategoryManagement';
import Balances from './pages/Balances';
import './index.css';

function Layout({ children }) {
  const location = useLocation();
  
  return (
    <div>
      <header className="header">
        <div className="container">
          <h1>Benefit Reimbursement System</h1>
          <nav className="nav">
            <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
              Submit Request
            </Link>
            <Link to="/categories" className={location.pathname === '/categories' ? 'active' : ''}>
              Categories
            </Link>
            <Link to="/balances" className={location.pathname === '/balances' ? 'active' : ''}>
              Balances
            </Link>
          </nav>
        </div>
      </header>
      <main className="container">
        {children}
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<SubmitRequest />} />
          <Route path="/categories" element={<CategoryManagement />} />
          <Route path="/balances" element={<Balances />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;

