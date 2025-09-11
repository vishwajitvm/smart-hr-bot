import "bulma/css/bulma.min.css";
import "./css/Dashboard.css";


function Dashboard() {
  return (
    <div className="dashboard section">
      <div className="container">
        <h2 className="title has-text-centered has-text-dark">Smart HR Bot Dashboard</h2>

        <div className="columns is-multiline is-variable is-4">
          <div className="column is-one-quarter">
            <div className="card has-text-centered">
              <div className="card-content">
                <p className="title is-4"> Candidates</p>
                <p className="subtitle is-6">340 Profiles Parsed</p>
              </div>
            </div>
          </div>

          <div className="column is-one-quarter">
            <div className="card has-text-centered">
              <div className="card-content">
                <p className="title is-4"> Interviews</p>
                <p className="subtitle is-6">42 Scheduled</p>
              </div>
            </div>
          </div>

          <div className="column is-one-quarter">
            <div className="card has-text-centered">
              <div className="card-content">
                <p className="title is-4"> Hires</p>
                <p className="subtitle is-6">18 Successful</p>
              </div>
            </div>
          </div>

          <div className="column is-one-quarter">
            <div className="card has-text-centered">
              <div className="card-content">
                <p className="title is-4"> Revenue</p>
                <p className="subtitle is-6">$15,200</p>
              </div>
            </div>
          </div>

          <div className="column is-one-quarter">
            <div className="card has-text-centered">
              <div className="card-content">
                <p className="title is-4"> AI Insights</p>
                <p className="subtitle is-6">120 Recommendations</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
