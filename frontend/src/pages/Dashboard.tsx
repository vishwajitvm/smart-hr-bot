import "./css/Dashboard.css";

function Dashboard() {
  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      <div className="dashboard-cards">
        <div className="card">
          <h3>Users</h3>
          <p>120 Active Users</p>
        </div>
        <div className="card">
          <h3>Interviews</h3>
          <p>25 Scheduled</p>
        </div>
        <div className="card">
          <h3>Revenue</h3>
          <p>$12,400</p>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
