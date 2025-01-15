import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const navigate = useNavigate(); // Hook for navigation

  const handleLogin = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/auth/login/", { email, password });
      setMessage(response.data.message);
      // Store tokens if needed
      localStorage.setItem("access", response.data.access);
      localStorage.setItem("refresh", response.data.refresh);
    } catch (error) {
      console.log("Full error object: ", error); // Log the full error object to inspect its structure
      setMessage(error.response?.data?.error || "Login failed.");
    }
  };

  const goToResetPassword = () => {
    navigate("/reset-password"); // Navigate to the reset password page
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body">
              <h3 className="text-center">Login</h3>
              {message && <div className="alert alert-info">{message}</div>}
              <form>
                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    className="form-control"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <input
                    type="password"
                    id="password"
                    className="form-control"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>

                <div className="d-flex justify-content-center mt-3">
                  <button
                    type="button"
                    className="btn btn-info btn-block"
                    style={{ maxWidth: "300px" }}
                    onClick={handleLogin}
                  >
                    Login
                  </button>
                </div>
              </form>

              <div className="d-flex justify-content-center mt-3">
                <button
                  type="button"
                  className="btn btn-link"
                  onClick={goToResetPassword}
                >
                  Forgot Password?
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
