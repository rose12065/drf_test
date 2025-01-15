import React, { useState, useEffect } from 'react';  
import axios from 'axios';
import { useParams } from 'react-router-dom';

const UserDetails = () => {
  const { userId } = useParams();  
  const [userDetails, setUserDetails] = useState(null);

  const getRoleName = (role) => {
    switch (role) {
      case 1:
        return "customer";
      case 2:
        return "Seller";
      case 3:
        return "agent";
      default:
        return "Unknown";
    }
  };

  useEffect(() => {
    const fetchUserDetails = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/auth/display/?user_id=${userId}`);
        console.log(response.data);  
        setUserDetails(response.data);  
      } catch (error) {
        console.error('Error fetching user details:', error);
      }
    };

    if (userId) {
      fetchUserDetails();
    }
  }, [userId]);  

  return (
    <div>
      <h1>User Details</h1>
      {userDetails ? (
        <div>
          <p>Name: {userDetails.username || 'N/A'}</p>
          <p>Email: {userDetails.email || 'N/A'}</p>
          <p>Date of Birth: {userDetails.date_of_birth || 'N/A'}</p>
          <p>Role: {getRoleName(userDetails.role) || 'N/A'}</p>  
          {userDetails.profile_picture && (
            <img 
              src={userDetails.profile_picture} 
              alt="Profile" 
              style={{ width: '100px', height: '100px' }} 
            />
          )}
        </div>
      ) : (
        <p>Loading user details...</p>
      )}
    </div>
  );
};

export default UserDetails;
