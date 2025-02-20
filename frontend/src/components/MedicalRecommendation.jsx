import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  FaHeartbeat, 
  FaMedkit, 
  FaExclamationTriangle,
  FaUserAlt,
  FaThermometerHalf,
  FaStethoscope,
  FaSpinner,
  FaChevronRight,
  FaMicroscope,
  FaPercentage,
  FaPills,
  FaChartLine,
  FaFileExcel,  // Add this import
  FaFile,       // Optional: for fallback icon
  FaCheck      
} from "react-icons/fa";

const GlassCard = ({ children, className = "" }) => (
  <div className={`backdrop-blur-lg bg-black/40 rounded-xl shadow-lg ${className}`}>
    {children}
  </div>
);

const InputField = ({ icon, label, ...props }) => (
  <div>
    <label className="block mb-2 text-gray-300 font-medium">{label}</label>
    <div className="relative">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        {icon}
      </div>
      <input
        {...props}
        className="w-full pl-10 p-3 rounded-lg bg-black/30 border border-gray-700 focus:border-blue-500 
                 text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500/20 outline-none 
                 transition-all duration-300"
      />
    </div>
  </div>
);

const ExcelUploadSection = ({ onExcelUpload, loading, error, uploadedFile }) => (
  <GlassCard className="p-6 mb-6">
    <h3 className="text-xl font-bold mb-4 flex items-center text-green-400">
      <FaFileExcel className="mr-2" />
      Update Training Data
    </h3>
    
    <div className="relative">
      <input
        type="file"
        accept=".xlsx,.xls"
        onChange={onExcelUpload}
        className="hidden"
        id="excel-upload"
      />
      <label
        htmlFor="excel-upload"
        className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-600 rounded-lg cursor-pointer
                 hover:border-green-500 transition-colors duration-300"
      >
        <FaFileExcel className="text-3xl text-green-400 mb-3" />
        <span className="text-gray-300 text-lg mb-2">
          Upload Excel file to update training data
        </span>
        <span className="text-gray-500 text-sm">Supports .xlsx and .xls files</span>
      </label>
    </div>

    <AnimatePresence>
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center text-red-400"
        >
          <FaExclamationTriangle className="mr-2" />
          {error}
        </motion.div>
      )}

      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="mt-4 p-4 bg-green-500/20 border border-green-500/50 rounded-lg flex items-center justify-center text-green-400"
        >
          <FaSpinner className="animate-spin mr-2" />
          Processing Excel file...
        </motion.div>
      )}

      {uploadedFile && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="mt-4 p-4 bg-green-500/20 border border-green-500/50 rounded-lg flex items-center text-green-400"
        >
          <FaFileExcel className="mr-2" />
          Successfully processed: {uploadedFile}
        </motion.div>
      )}
    </AnimatePresence>
  </GlassCard>
);


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
  const [excelLoading, setExcelLoading] = useState(false);
  const [excelError, setExcelError] = useState(null);
  const [uploadedExcel, setUploadedExcel] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('https://health-vault-3lre.onrender.com/predict-medical', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
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
  const handleExcelUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.match(/\.(xlsx|xls)$/)) {
      setExcelError("Please upload an Excel file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setExcelLoading(true);
    setExcelError(null);

    try {
      const response = await fetch("https://health-vault-3lre.onrender.com/upload-excel", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setUploadedExcel(data.filename);
      // Optional: Show success message with number of records added
      alert(`Successfully added ${data.records_added} records to the training data`);
    } catch (error) {
      console.error("Error uploading Excel file:", error);
      setExcelError(error.message || "Failed to upload Excel file");
      setUploadedExcel(null);
    } finally {
      setExcelLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-white p-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Add Excel Upload Section */}
          <ExcelUploadSection
            onExcelUpload={handleExcelUpload}
            loading={excelLoading}
            error={excelError}
            uploadedFile={uploadedExcel}
          />
          <GlassCard className="p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center text-blue-400">
              <FaHeartbeat className="mr-2" />
              Medical Recommendation System
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InputField
                  icon={<FaUserAlt className="text-gray-500" />}
                  label="Age"
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  placeholder="Enter age"
                  required
                />

                <div>
                  <label className="block mb-2 text-gray-300 font-medium">Gender</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FaUserAlt className="text-gray-500" />
                    </div>
                    <select
                      name="gender"
                      value={formData.gender}
                      onChange={handleChange}
                      className="w-full pl-10 p-3 rounded-lg bg-black/30 border border-gray-700 
                               text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 
                               outline-none transition-all duration-300"
                      required
                    >
                      <option value="" className="bg-gray-900">Select Gender</option>
                      <option value="M" className="bg-gray-900">Male</option>
                      <option value="F" className="bg-gray-900">Female</option>
                    </select>
                  </div>
                </div>
              </div>

              <InputField
                icon={<FaThermometerHalf className="text-gray-500" />}
                label="Symptoms"
                type="text"
                name="symptoms"
                value={formData.symptoms}
                onChange={handleChange}
                placeholder="e.g., Fever, Cough, Headache"
                required
              />

              <InputField
                icon={<FaStethoscope className="text-gray-500" />}
                label="Cause"
                type="text"
                name="cause"
                value={formData.cause}
                onChange={handleChange}
                placeholder="e.g., Viral Infection"
                required
              />

              <motion.button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600/80 hover:bg-blue-500/80 text-white py-3 rounded-lg
                         flex items-center justify-center space-x-2 backdrop-blur-sm
                         disabled:bg-gray-700 disabled:cursor-not-allowed
                         transition-all duration-300"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {loading ? (
                  <>
                    <FaSpinner className="animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <FaChevronRight />
                    <span>Get Recommendation</span>
                  </>
                )}
              </motion.button>
            </form>
          </GlassCard>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center text-red-400"
              >
                <FaExclamationTriangle className="mr-2" />
                {error}
              </motion.div>
            )}
          </AnimatePresence>
          {/* Prediction Results Section */}
          {prediction && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Advanced Prediction Card */}
              <GlassCard className="p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center text-blue-400">
                  <FaMicroscope className="mr-2" />
                  Basic Prediction Analysis
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {prediction.error ? (
                    <div className="col-span-2 text-red-400 flex items-center">
                      <FaExclamationTriangle className="mr-2" />
                      Error: {prediction.error}
                    </div>
                  ) : (
                    <>
                      {/* Disease Prediction */}
                      <div className="bg-blue-500/10 rounded-lg p-4 border border-blue-500/20">
                        <h4 className="text-lg font-semibold mb-3 text-blue-400 flex items-center">
                          <FaHeartbeat className="mr-2" />
                          Disease Prediction
                        </h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-gray-300">Diagnosis:</span>
                            <span className="text-white font-medium">
                              {prediction.advanced_prediction.disease.name}
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-gray-300">Confidence:</span>
                            <div className="flex items-center text-green-400">
                              <FaPercentage className="mr-1" />
                              <span>{prediction.advanced_prediction.disease.confidence.toFixed(1)}%</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Medicine Recommendation */}
                      <div className="bg-purple-500/10 rounded-lg p-4 border border-purple-500/20">
                        <h4 className="text-lg font-semibold mb-3 text-purple-400 flex items-center">
                          <FaPills className="mr-2" />
                          Medicine Recommendation
                        </h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-gray-300">Medicine:</span>
                            <span className="text-white font-medium">
                              {prediction.advanced_prediction.medicine.name}
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-gray-300">Confidence:</span>
                            <div className="flex items-center text-green-400">
                              <FaPercentage className="mr-1" />
                              <span>{prediction.advanced_prediction.medicine.confidence.toFixed(1)}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </GlassCard>

              {/* Basic Prediction Card */}
              <GlassCard className="p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center text-green-400">
                  <FaChartLine className="mr-2" />
                  Advanced Prediction Analysis
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Diseases List */}
                  <div className="bg-green-500/10 rounded-lg p-4 border border-green-500/20">
                    <h4 className="text-lg font-semibold mb-3 text-green-400 flex items-center">
                      <FaHeartbeat className="mr-2" />
                      Predicted Diseases
                    </h4>
                    <div className="space-y-2">
                      {prediction.basic_prediction.diseases.map((disease, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-gray-300">{disease.name}</span>
                          <div className="flex items-center text-green-400">
                            <FaPercentage className="mr-1" />
                            <span>{disease.confidence.toFixed(1)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Medicines List */}
                  <div className="bg-green-500/10 rounded-lg p-4 border border-green-500/20">
                    <h4 className="text-lg font-semibold mb-3 text-green-400 flex items-center">
                      <FaPills className="mr-2" />
                      Recommended Medicines
                    </h4>
                    <div className="space-y-2">
                      {prediction.basic_prediction.medicines.map((medicine, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-gray-300">{medicine.name}</span>
                          <div className="flex items-center text-green-400">
                            <FaPercentage className="mr-1" />
                            <span>{medicine.confidence.toFixed(1)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Model Metrics */}
                <div className="mt-6 pt-6 border-t border-gray-700">
                  <h4 className="text-lg font-semibold mb-3 text-blue-400 flex items-center">
                    <FaChartLine className="mr-2" />
                    Model Performance Metrics
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex justify-between items-center bg-blue-500/10 p-3 rounded-lg">
                      <span className="text-gray-300">Disease Prediction Accuracy:</span>
                      <div className="flex items-center text-blue-400">
                        <FaPercentage className="mr-1" />
                        <span>{prediction.model_metrics.disease_accuracy.toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center bg-blue-500/10 p-3 rounded-lg">
                      <span className="text-gray-300">Medicine Prediction Accuracy:</span>
                      <div className="flex items-center text-blue-400">
                        <FaPercentage className="mr-1" />
                        <span>{prediction.model_metrics.medicine_accuracy.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default MedicalRecommendation;
