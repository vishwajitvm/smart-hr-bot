import "./css/Home.css";

function Home() {
  return (
    <div className="home">
      {/* Hero Section */}
      <header className="hero">
        <h1>🤖 Smart HR Bot</h1>
        <p className="subtitle has-text-dark">
          Your AI-powered recruitment assistant – streamline hiring with resume
          parsing, candidate evaluation, AI interviews, scheduling, and
          analytics.
        </p>
        <button className="cta-btn">Get Started</button>
      </header>

      {/* Features Section */}
      <section className="features">
        <h2>✨ What Smart HR Bot Does</h2>
        <div className="feature-grid">
          <div className="feature-card">
            <h3>📄 Resume Parsing</h3>
            <p>
              Upload resumes in PDF/DOCX and let AI extract skills, experience,
              and education instantly.
            </p>
          </div>
          <div className="feature-card">
            <h3>⭐ Candidate Evaluation</h3>
            <p>
              AI scoring on skills, ATS compliance, grammar, projects, and
              cultural fit.
            </p>
          </div>
          <div className="feature-card">
            <h3>🎤 AI Interviews</h3>
            <p>
              Simulated interview Q&A with real-time sentiment and confidence
              analysis.
            </p>
          </div>
          <div className="feature-card">
            <h3>📅 Scheduling</h3>
            <p>
              Google Calendar integration – schedule interviews automatically
              and send reminders.
            </p>
          </div>
          <div className="feature-card">
            <h3>📢 Notifications</h3>
            <p>
              Automated email & SMS alerts for candidates and recruiters using
              Twilio/Kaleyra.
            </p>
          </div>
          <div className="feature-card">
            <h3>📊 Analytics Dashboard</h3>
            <p>
              Insights on candidate performance, hiring trends, and recruiter
              efficiency.
            </p>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="about">
        <h2>💡 Why Smart HR Bot?</h2>
        <p>
          Instead of HR teams spending countless hours screening resumes and
          coordinating interviews, Smart HR Bot does the heavy lifting. Recruiters
          get a clean dashboard with only the best-matched candidates and smart
          analytics to make faster, data-driven hiring decisions.
        </p>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>© {new Date().getFullYear()} Bee Logical. All Rights Reserved.</p>
      </footer>

    </div>
  );
}

export default Home;
