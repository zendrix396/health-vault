import { useState } from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import HomePage from "./components/HomePage";
import MedicalReports from "./components/MedicalReports";
import MedicalRecommendation from './components/MedicalRecommendation';
import PatientCare from './components/PatientCare';
import DoctorPortal from "./components/DoctorPortal"
function App() {
  const [currentPage, setCurrentPage] = useState("home");
  const [isDarkMode, setIsDarkMode] = useState(true);

  const renderPage = () => {
    switch(currentPage) {
      case "Medical Report Analysis":
        return <MedicalReports />;
      case "Medicine Recommendations":
        return <MedicalRecommendation />;
      case "Doctor Portal":
        return <DoctorPortal/>
      case "Patient Care":
        return <PatientCare/>
      case "home":
      default:
        return <HomePage setCurrentPage={setCurrentPage} />;
    }
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'dark' : 'light'}`}>
      <Navbar 
        currentPage={currentPage} 
        setCurrentPage={setCurrentPage}
        isDarkMode={isDarkMode}
        setIsDarkMode={setIsDarkMode}
      />
      <div className="pt-16">
        {renderPage()}
      </div>
    </div>
  );
}

export default App;