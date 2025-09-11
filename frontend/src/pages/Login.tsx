import "./css/Login.css";

function Login() {
  const handleMicrosoftLogin = () => {
    // Redirect to Microsoft OAuth login (placeholder)
    window.location.href = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize";
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Login</h2>
        <button className="ms-login-btn" onClick={handleMicrosoftLogin}>
          🔑 Login with Microsoft
        </button>
      </div>
    </div>
  );
}

export default Login;
