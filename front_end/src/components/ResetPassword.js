import React, { useState } from "react";
import axios from "axios";

const ResetPassword = () => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleResetPassword = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/auth/reset-password/", { email });
      setMessage(response.data.message || "Password reset link sent to your email.");
    } catch (error) {
      setMessage(error.response?.data?.error || "Error sending password reset link.");
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body">
              <h3 className="text-center">Reset Password</h3>
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

                <div className="d-flex justify-content-center mt-3">
                  <button
                    type="button"
                    className="btn btn-primary btn-block"
                    style={{ maxWidth: "300px" }}
                    onClick={handleResetPassword}
                  >
                    Send Reset Link
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;
