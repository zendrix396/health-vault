import { useState } from "react";
import { motion } from "framer-motion";
import { FaHeartbeat, FaMedkit, FaExclamationTriangle } from "react-icons/fa";

const MedicalRecommendation = () => {
  const [formData, setFormData] = useState({
    age: "",
    gender: "",
    symptoms: "",
    cause: "",
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
  
    try {
      const response = await fetch('http://localhost:8000/predict-medical', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
  
      const data = await response.json();
      console.log('Raw API Response:', data); // Add this debug log
      
      if (!response.ok) {
        throw new Error(data.detail || 'Prediction failed');
      }
  
      setPrediction(data);
    } catch (err) {
      console.error('Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-lg p-6"
      >
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          <FaHeartbeat className="mr-2 text-red-500" />
          Medical Recommendation System
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-2">Age</label>
            <input
              type="number"
              name="age"
              value={formData.age}
              onChange={handleChange}
              className="w-full p-2 border rounded"
              required
            />
          </div>

          <div>
            <label className="block mb-2">Gender</label>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              className="w-full p-2 border rounded"
              required
            >
              <option value="">Select Gender</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
            </select>
          </div>

          <div>
            <label className="block mb-2">Symptoms</label>
            <input
              type="text"
              name="symptoms"
              value={formData.symptoms}
              onChange={handleChange}
              className="w-full p-2 border rounded"
              placeholder="e.g., Fever, Cough, Headache"
              required
            />
          </div>

          <div>
            <label className="block mb-2">Cause</label>
            <input
              type="text"
              name="cause"
              value={formData.cause}
              onChange={handleChange}
              className="w-full p-2 border rounded"
              placeholder="e.g., Viral Infection"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
            disabled={loading}
          >
            {loading ? "Processing..." : "Get Recommendation"}
          </button>
        </form>
        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded flex items-center">
            <FaExclamationTriangle className="mr-2" />
            {error}
          </div>
        )}
    {prediction && (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    className="mt-6 space-y-4"
  >
    {/* Advanced Prediction Section */}
    <div className="bg-green-50 p-4 rounded-lg">
      <h3 className="font-bold text-lg mb-2 flex items-center">
        <FaMedkit className="mr-2 text-green-500" />
        Advanced Prediction
      </h3>
      <div className="space-y-2">
        {prediction.error ? (
          <p className="text-red-500">Error: {prediction.error}</p>
        ) : (
          <>
            <p>Disease: {prediction.advanced_prediction.disease.name}</p>
            <p>Disease Confidence: {prediction.advanced_prediction.disease.confidence}%</p>
            <p>Recommended Medicine: {prediction.advanced_prediction.medicine.name}</p>
            <p>Medicine Confidence: {prediction.advanced_prediction.medicine.confidence}%</p>
          </>
        )}
      </div>
    </div>

    {/* Basic Prediction Section */}
    <div className="bg-blue-50 p-4 rounded-lg">
      <h3 className="font-bold text-lg mb-2 flex items-center">
        <FaMedkit className="mr-2 text-blue-500" />
        Basic Prediction
      </h3>
      
      {/* Diseases */}
      <div className="mb-4">
        <h4 className="font-semibold">Predicted Diseases:</h4>
        <ul className="list-disc pl-5 space-y-1">
          {prediction.basic_prediction.diseases.map((disease, index) => (
            <li key={index}>
              {disease.name}: {disease.confidence}%
            </li>
          ))}
        </ul>
      </div>

      {/* Medicines */}
      <div className="mb-4">
        <h4 className="font-semibold">Recommended Medicines:</h4>
        <ul className="list-disc pl-5 space-y-1">
          {prediction.basic_prediction.medicines.map((medicine, index) => (
            <li key={index}>
              {medicine.name}: {medicine.confidence}%
            </li>
          ))}
        </ul>
      </div>

      {/* Model Metrics */}
      <div className="mt-4 pt-4 border-t border-blue-200">
        <h4 className="font-semibold">Model Accuracy:</h4>
        <p>Disease Prediction: {prediction.model_metrics.disease_accuracy}%</p>
        <p>Medicine Prediction: {prediction.model_metrics.medicine_accuracy}%</p>
      </div>
    </div>
  </motion.div>
)}
      </motion.div>
    </div>
  );
};

export default MedicalRecommendation;
