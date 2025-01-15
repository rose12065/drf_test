import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom"; 

const RegistrationForm = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    date_of_birth: "",
    role: "",
    profile_Picture: null, 
  });

  const [responseMessage, setResponseMessage] = useState(""); 
  const [showModal, setShowModal] = useState(false); 
  const [userId, setUserId] = useState(null); 
  const navigate = useNavigate(); 

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFormData({ ...formData, profilePicture: file });
  };


  const handleSubmit = async (e) => {
    e.preventDefault();


    const convertToBase64 = (file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = (error) => reject(error);
      });
    };

    try {

      const base64Image = formData.profilePicture
        ? await convertToBase64(formData.profilePicture)
        : null;


      const data = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        date_of_birth: formData.dateOfBirth,
        role: formData.role,
        profile_picture: base64Image, 
      };

      const response = await axios.post(
        "http://127.0.0.1:8000/auth/registerclass/",
        data,
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      setResponseMessage(response.data.message); 
      setUserId(response.data.user_id); 
      setShowModal(true); 
    } catch (error) {
      setResponseMessage("Error registering. Please try again."); 
      setShowModal(true); 
    }
  };

  
  const navigateToUserDetails = () => {
    if (userId) {
      navigate(`/user-details/${userId}`); 
    }
  };

  return (
    <div className="container">
      <h2 className="mt-5">Registration Form</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Username:</label>
          <input
            type="text"
            className="form-control"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">Email:</label>
          <input
            type="email"
            className="form-control"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">Password:</label>
          <input
            type="password"
            className="form-control"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">Confirm Password:</label>
          <input
            type="password"
            className="form-control"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">Date of Birth:</label>
          <input
            type="date"
            className="form-control"
            name="dateOfBirth"
            value={formData.dateOfBirth}
            onChange={handleChange}
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">Role:</label>
          <select
            className="form-control"
            name="role"
            value={formData.role}
            onChange={handleChange}
            required
          >
            <option value={1}>customer</option>
            <option value={2}>Seller</option>
            <option value={3}>agent</option>
          </select>
        </div>


        <div className="mb-3">
          <label className="form-label">Upload Image:</label>
          <input
            type="file"
            className="form-control"
            name="profilePicture"
            onChange={handleFileChange}
            required
          />
        </div>

        <button type="submit" className="btn btn-primary">
          Register
        </button>
      </form>

      {/* Modal for response message */}
      {showModal && (
        <div
          className="modal fade show"
          style={{ display: "block" }}
          tabIndex="-1"
          role="dialog"
        >
          <div className="modal-dialog" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Registration Response</h5>
                <button
                  type="button"
                  className="close"
                  data-dismiss="modal"
                  aria-label="Close"
                  onClick={() => setShowModal(false)}
                >
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div className="modal-body">
                <p>{responseMessage}</p>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  data-dismiss="modal"
                  onClick={() => setShowModal(false)}
                >
                  Close
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={navigateToUserDetails}
                >
                  Go to User Details
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RegistrationForm;
