import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import RegistrationForm from './components/RegistrationForm';
import UserDetails from './components/UserDetails';
import AlertTable from './components/AlertMechanism';
import Login from './components/LoginPage';
import ResetPassword from './components/ResetPassword';
import ResetPasswordToken from './components/ResetPasswordToken';


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RegistrationForm />} />
        <Route path="/user-details/:userId" element={<UserDetails />} />
        <Route path="/alert-mechanism" element={< AlertTable />} />
        <Route path='/login' element={<Login/>}/>
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path='/reset-password-token/:uid/:token' element={<ResetPasswordToken/>} />
      </Routes>
    </Router>
  );
}

export default App;
