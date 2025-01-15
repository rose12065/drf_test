import React, { useState, useEffect } from "react";
import axios from "axios";

const AlertTable = () => {
  const [users, setUsers] = useState([]);
  const [modalContent, setModalContent] = useState("");
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/auth/users-list/").then((response) => {
      setUsers(response.data);
    });
  }, []);

  const sendAlert = (userId, sendEmail, sendSMS) => {
    axios
      .post("http://127.0.0.1:8000/auth/alert/", {
        user_id: userId,
        send_email: sendEmail,
        send_sms: sendSMS,
      })
      .then((response) => {
        const message = response.data.email || "Alert sent successfully!";
        setModalContent(message);
        setShowModal(true);
      })
      .catch(() => {
        setModalContent("Error sending alert");
        setShowModal(true);
      });
  };

  return (
    <div className="container mt-4">
      <h3 className="mb-3">Alert Users</h3>
      <table className="table table-striped table-hover">
        <thead className="thead-dark">
          <tr>
            <th>User</th>
            <th>Email</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td>
                <div className="btn-group" role="group">
                  <button
                    className="btn btn-outline-success btn-sm me-2"
                    onClick={() => sendAlert(user.id, true, false)}
                  >
                    Send Email
                  </button>
                  <button
                    className="btn btn-outline-success btn-sm me-2"
                    onClick={() => sendAlert(user.id, false, true)}
                  >
                    Send SMS
                  </button>
                  <button
                    className="btn btn-outline-success btn-sm me-2"
                    onClick={() => sendAlert(user.id, true, true)}
                  >
                    Send Both
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Modal */}
      {showModal && (
        <div
          className="modal fade show"
          tabIndex="-1"
          role="dialog"
          style={{ display: "block", backgroundColor: "rgba(0, 0, 0, 0.5)" }}
        >
          <div className="modal-dialog" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Alert</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <p>{modalContent}</p>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertTable;
