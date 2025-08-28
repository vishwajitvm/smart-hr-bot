import { Link } from "react-router-dom";
import "./css/Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <h1 className="logo">Smart HR Bot</h1>
      <ul className="nav-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/login">Login</Link></li>
        <li><Link to="/dashboard">Dashboard</Link></li>
      </ul>
    </nav>
  );
}

export default Navbar;
