import { useState } from "react";
import { motion } from "framer-motion";
import {
  FaHeartbeat,
  FaClipboardList,
  FaBookMedical,
  FaCheckCircle,
} from "react-icons/fa";

const ReportSection = ({ title, icon, children, color }) => (
  <motion.div
    className={`min-h-screen snap-start p-8 ${color}`}
    initial={{ opacity: 0, y: 50 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
  >
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center mb-6">
        {icon}
        <h2 className="text-3xl font-bold ml-4">{title}</h2>
      </div>
      {children}
    </div>
  </motion.div>
);

const MedicalReport = ({ analysis }) => {
  const analysisData = typeof analysis === 'string' ? JSON.parse(analysis) : analysis;

  return (
    <div className="snap-y snap-mandatory h-screen overflow-y-scroll">
      <ReportSection
        title="Summary"
        icon={<FaClipboardList className="text-4xl text-blue-500" />}
        color="bg-blue-50"
      >
        <motion.p
          className="text-xl leading-relaxed"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {analysisData.summary}
        </motion.p>
      </ReportSection>

      <ReportSection
        title="Key Findings"
        icon={<FaHeartbeat className="text-4xl text-red-500" />}
        color="bg-red-50"
      >
        <div className="space-y-4">
          {analysisData.findings.map((finding, index) => (
            <motion.div
              key={index}
              className="flex items-start p-4 bg-white rounded-lg shadow"
              initial={{ x: -50, opacity: 0 }}
              whileInView={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <span className="text-2xl mr-4">{finding.emoji}</span>
              <p className="text-lg">{finding.text}</p>
            </motion.div>
          ))}
        </div>
      </ReportSection>

      <ReportSection
        title="Medical Terms"
        icon={<FaBookMedical className="text-4xl text-green-500" />}
        color="bg-green-50"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {analysisData.terms.map((term, index) => (
            <motion.div
              key={index}
              className="p-4 bg-white rounded-lg shadow"
              initial={{ scale: 0.9, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <h3 className="font-bold text-lg">{term.term}</h3>
              <p className="text-gray-600">{term.explanation}</p>
            </motion.div>
          ))}
        </div>
      </ReportSection>

      <ReportSection
        title="Recommendations"
        icon={<FaCheckCircle className="text-4xl text-purple-500" />}
        color="bg-purple-50"
      >
        <div className="space-y-4">
          {analysisData.recommendations.map((rec, index) => (
            <motion.div
              key={index}
              className="flex items-center p-4 bg-white rounded-lg shadow"
              initial={{ y: 50, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="flex-shrink-0 w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mr-4">
                <span className="text-2xl">{rec.emoji}</span>
              </div>
              <div>
                <h4 className="font-bold">{rec.title}</h4>
                <p className="text-gray-600">{rec.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </ReportSection>
    </div>
  );
};

const MedicalReports = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [pdfText, setPdfText] = useState("");
  const [analysis, setAnalysis] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.includes("pdf")) {
      setError("Please upload a PDF file");
      return;
    }

    const formData = new FormData();
    formData.append("file_upload", file);

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setUploadedFile(data.filename);
      setPdfText(data.text_content);
      setAnalysis(data.analysis);
      setError(null);
    } catch (error) {
      console.error("Error uploading file:", error);
      setError(error.message || "Failed to upload file");
      setUploadedFile(null);
      setPdfText("");
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="mb-8">
        <label className="block mb-2">
          <span className="text-gray-700">Upload Medical Report (PDF)</span>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            className="mt-1 block w-full p-2 border rounded"
          />
        </label>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {loading && (
        <div className="text-center py-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
        </div>
      )}

      {uploadedFile && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4">
          <span className="block sm:inline">Successfully uploaded: {uploadedFile}</span>
        </div>
      )}

      {pdfText && analysis && <MedicalReport analysis={analysis} />}
    </div>
  );
};

export default MedicalReports;