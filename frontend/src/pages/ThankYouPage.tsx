import React from "react";
import { Link } from "react-router-dom";
import "./css/thankyou.css";

const ThankYouPage: React.FC = () => {
  return (
    <section className="hero is-fullheight is-primary is-bold">
      <div className="hero-body">
        <div className="container has-text-centered">
          <div className="thankyou-box">
            <h1 className="thankyou-title">🎉 Thank You for Applying!</h1>
            <p className="thankyou-subtitle">
              We’ve received your application and our team will get back to you shortly.
            </p>

            <div className="buttons is-centered mt-5 thankyou-buttons">
              <Link to="/" className="button is-link is-medium">
                Back to Home
              </Link>
              <Link to="/view-job-openings" className="button is-success is-medium">
                View More Job Openings
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ThankYouPage;
