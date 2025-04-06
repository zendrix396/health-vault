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
  FaFileExcel,
  FaFile,
  FaCheck
} from "react-icons/fa";

// Add manga-style CSS classes
const mangaStyles = `
  .manga-border {
    border: 2px solid black !important;
    box-shadow: 4px 4px 0 rgba(0,0,0,0.9) !important;
  }
  
  .manga-text {
    font-family: 'Comic Sans MS', 'Bangers', sans-serif !important;
    letter-spacing: 0.5px !important;
  }
  
  .manga-text-rotate {
    font-family: 'Comic Sans MS', 'Bangers', sans-serif !important;
    letter-spacing: 0.5px !important;
    transform: rotate(-1deg) !important;
  }
  
  .manga-fade-in {
    animation: fadeIn 0.5s ease-in-out !important;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

// Add styling to head
if (typeof document !== 'undefined') {
  const styleElement = document.createElement('style');
  styleElement.textContent = mangaStyles;
  document.head.appendChild(styleElement);
}

const GlassCard = ({ children, className = "" }) => (
  <div className={`backdrop-blur-lg bg-white/90 rounded-none shadow-lg manga-border ${className}`}>
    {children}
  </div>
);

const InputField = ({ icon, label, ...props }) => (
  <div>
    <label className="block mb-2 text-black font-black manga-text">{label}</label>
    <div className="relative">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        {icon}
      </div>
      <input
        {...props}
        className="w-full pl-10 p-3 rounded-none bg-white border-black manga-border
                 text-black placeholder-gray-500 focus:border-blue-500 
                 focus:ring-2 focus:ring-blue-500/20 outline-none 
                 transition-all duration-300"
      />
    </div>
  </div>
);

const ExcelUploadSection = ({ onExcelUpload, loading, error, uploadedFile }) => (
  <GlassCard className="p-6 mb-6 manga-fade-in">
    <h3 className="text-xl font-black mb-4 flex items-center text-black manga-text">
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
        className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-black rounded-none cursor-pointer
                 hover:border-green-500 transition-colors duration-300 manga-border"
      >
        <FaFileExcel className="text-3xl text-black mb-3" />
        <span className="text-black text-lg mb-2 manga-text font-bold">
          Upload Excel file to update training data
        </span>
        <span className="text-gray-700 text-sm manga-text">Supports .xlsx and .xls files</span>
      </label>
    </div>

    <AnimatePresence>
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="mt-4 p-4 bg-red-100 manga-border flex items-center text-red-600 manga-text font-bold"
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
          className="mt-4 p-4 bg-blue-100 manga-border flex items-center justify-center text-black manga-text font-bold"
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
          className="mt-4 p-4 bg-green-100 manga-border flex items-center text-black manga-text font-bold"
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
    <div className="min-h-screen bg-gray-100 text-black p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-center mb-8">
          <FaHeartbeat className="h-16 w-16 text-black" />
        </div>
        <h2 className="manga-text-rotate text-3xl font-black text-center text-black mb-8 transform -rotate-2">
          Medical Recommendation System
        </h2>
        
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
          <GlassCard className="p-6 manga-fade-in">
            <h2 className="text-2xl font-black mb-6 flex items-center text-black manga-text">
              <FaHeartbeat className="mr-2" />
              Enter Patient Details
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InputField
                  icon={<FaUserAlt className="text-black" />}
                  label="Age"
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  placeholder="Enter age"
                  required
                />

                <div>
                  <label className="block mb-2 text-black font-black manga-text">Gender</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FaUserAlt className="text-black" />
                    </div>
                    <select
                      name="gender"
                      value={formData.gender}
                      onChange={handleChange}
                      className="w-full pl-10 p-3 rounded-none bg-white manga-border border-black 
                               text-black focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 
                               outline-none transition-all duration-300 manga-text font-bold"
                      required
                    >
                      <option value="" className="bg-white">Select Gender</option>
                      <option value="M" className="bg-white">Male</option>
                      <option value="F" className="bg-white">Female</option>
                    </select>
                  </div>
                </div>
              </div>

              <InputField
                icon={<FaThermometerHalf className="text-black" />}
                label="Symptoms"
                type="text"
                name="symptoms"
                value={formData.symptoms}
                onChange={handleChange}
                placeholder="e.g., Fever, Cough, Headache"
                required
              />

              <InputField
                icon={<FaStethoscope className="text-black" />}
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
                className="w-full bg-black hover:bg-gray-800 text-white py-3 rounded-none
                         flex items-center justify-center space-x-2 manga-border manga-text font-black
                         disabled:bg-gray-400 disabled:cursor-not-allowed
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
                className="p-4 bg-red-100 manga-border flex items-center text-red-600 manga-text font-bold"
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
              <GlassCard className="p-6 manga-fade-in">
                <h3 className="text-xl font-black mb-4 flex items-center text-black manga-text">
                  <FaMicroscope className="mr-2" />
                  Basic Prediction Analysis
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {prediction.error ? (
                    <div className="col-span-2 text-red-600 flex items-center manga-text font-bold">
                      <FaExclamationTriangle className="mr-2" />
                      Error: {prediction.error}
                    </div>
                  ) : (
                    <>
                      {/* Disease Prediction */}
                      <div className="bg-blue-100 rounded-none p-4 manga-border">
                        <h4 className="text-lg font-black mb-3 text-black manga-text flex items-center">
                          <FaHeartbeat className="mr-2" />
                          Disease Prediction
                        </h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-black manga-text font-bold">Diagnosis:</span>
                            <span className="text-black manga-text font-black">
                              {prediction.advanced_prediction.disease.name}
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-black manga-text font-bold">Confidence:</span>
                            <div className="flex items-center text-black manga-text font-black">
                              <FaPercentage className="mr-1" />
                              <span>{prediction.advanced_prediction.disease.confidence.toFixed(1)}%</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Medicine Recommendation */}
                      <div className="bg-purple-100 rounded-none p-4 manga-border">
                        <h4 className="text-lg font-black mb-3 text-black manga-text flex items-center">
                          <FaPills className="mr-2" />
                          Medicine Recommendation
                        </h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-black manga-text font-bold">Medicine:</span>
                            <span className="text-black manga-text font-black">
                              {prediction.advanced_prediction.medicine.name}
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-black manga-text font-bold">Confidence:</span>
                            <div className="flex items-center text-black manga-text font-black">
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
              <GlassCard className="p-6 manga-fade-in">
                <h3 className="text-xl font-black mb-4 flex items-center text-black manga-text">
                  <FaChartLine className="mr-2" />
                  Advanced Prediction Analysis
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Diseases List */}
                  <div className="bg-green-100 rounded-none p-4 manga-border">
                    <h4 className="text-lg font-black mb-3 text-black manga-text flex items-center">
                      <FaHeartbeat className="mr-2" />
                      Predicted Diseases
                    </h4>
                    <div className="space-y-2">
                      {prediction.basic_prediction.diseases.map((disease, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-black manga-text font-bold">{disease.name}</span>
                          <div className="flex items-center text-black manga-text font-black">
                            <FaPercentage className="mr-1" />
                            <span>{disease.confidence.toFixed(1)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Medicines List */}
                  <div className="bg-green-100 rounded-none p-4 manga-border">
                    <h4 className="text-lg font-black mb-3 text-black manga-text flex items-center">
                      <FaPills className="mr-2" />
                      Recommended Medicines
                    </h4>
                    <div className="space-y-2">
                      {prediction.basic_prediction.medicines.map((medicine, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-black manga-text font-bold">{medicine.name}</span>
                          <div className="flex items-center text-black manga-text font-black">
                            <FaPercentage className="mr-1" />
                            <span>{medicine.confidence.toFixed(1)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Model Metrics */}
                <div className="mt-6 pt-6 border-t border-black">
                  <h4 className="text-lg font-black mb-3 text-black manga-text flex items-center">
                    <FaChartLine className="mr-2" />
                    Model Performance Metrics
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex justify-between items-center bg-blue-100 p-3 manga-border">
                      <span className="text-black manga-text font-bold">Disease Prediction Accuracy:</span>
                      <div className="flex items-center text-black manga-text font-black">
                        <FaPercentage className="mr-1" />
                        <span>{prediction.model_metrics.disease_accuracy.toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center bg-blue-100 p-3 manga-border">
                      <span className="text-black manga-text font-bold">Medicine Prediction Accuracy:</span>
                      <div className="flex items-center text-black manga-text font-black">
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
