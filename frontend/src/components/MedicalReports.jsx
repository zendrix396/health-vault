import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FaHeartbeat,
  FaClipboardList,
  FaBookMedical,
  FaCheckCircle,
  FaFileUpload,
  FaSpinner,
  FaTimesCircle,
  FaFileAlt,
  FaArrowRight
} from "react-icons/fa";

const GlassCard = ({ children, className = "" }) => (
  <div className={`backdrop-blur-lg bg-black/40 rounded-xl shadow-lg ${className}`}>
    {children}
  </div>
);

const BlurryBackground = () => (
  <div className="fixed inset-0 -z-10 overflow-hidden">
    <div className="absolute inset-0 bg-gradient-to-br from-gray-950 via-gray-900 to-black"></div>
    <motion.div
      animate={{
        scale: [1, 1.2, 1],
        rotate: [0, 180, 360],
        x: [0, 100, 0],
        y: [0, -50, 0],
      }}
      transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
      className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-blue-500/10 blur-[100px]"
    />
    <motion.div
      animate={{
        scale: [1.2, 1, 1.2],
        rotate: [0, -180, -360],
        x: [0, -100, 0],
        y: [0, 50, 0],
      }}
      transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
      className="absolute top-1/3 right-1/4 w-96 h-96 rounded-full bg-purple-500/10 blur-[100px]"
    />
  </div>
);

const ReportSection = ({ title, icon, children }) => (
  <motion.div
    className="min-h-screen snap-start p-8"
    initial={{ opacity: 0, y: 50 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
  >
    <GlassCard className="p-6">
      <div className="flex items-center mb-6">
        {icon}
        <h2 className="text-2xl font-bold ml-4 text-white">{title}</h2>
      </div>
      {children}
    </GlassCard>
  </motion.div>
);

const FileUploadSection = ({ onFileUpload, loading, error, uploadedFile }) => (
  <GlassCard className="p-6 mb-8">
    <div className="relative">
      <input
        type="file"
        accept=".pdf"
        onChange={onFileUpload}
        className="hidden"
        id="file-upload"
      />
      <label
        htmlFor="file-upload"
        className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-600 rounded-lg cursor-pointer
                 hover:border-blue-500 transition-colors duration-300"
      >
        <FaFileUpload className="text-4xl text-blue-400 mb-4" />
        <span className="text-gray-300 text-lg mb-2">
          Drop your medical report here or click to browse
        </span>
        <span className="text-gray-500 text-sm">Supports PDF files only</span>
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
          <FaTimesCircle className="mr-2" />
          {error}
        </motion.div>
      )}

      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="mt-4 p-4 bg-blue-500/20 border border-blue-500/50 rounded-lg flex items-center justify-center text-blue-400"
        >
          <FaSpinner className="animate-spin mr-2" />
          Processing your document...
        </motion.div>
      )}

      {uploadedFile && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="mt-4 p-4 bg-green-500/20 border border-green-500/50 rounded-lg flex items-center text-green-400"
        >
          <FaFileAlt className="mr-2" />
          Successfully uploaded: {uploadedFile}
        </motion.div>
      )}
    </AnimatePresence>
  </GlassCard>
);
const MedicalReport = ({ analysis }) => {
  const analysisData = typeof analysis === 'string' ? JSON.parse(analysis) : analysis;

  return (
    <div className="snap-y snap-mandatory h-screen overflow-y-scroll">
      <ReportSection
        title="Summary"
        icon={<FaClipboardList className="text-3xl text-blue-400" />}
      >
        <motion.div
          className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <p className="text-lg leading-relaxed text-gray-300">
            {analysisData.summary}
          </p>
        </motion.div>
      </ReportSection>

      <ReportSection
        title="Key Findings"
        icon={<FaHeartbeat className="text-3xl text-red-400" />}
      >
        <div className="space-y-4">
          {analysisData.findings.map((finding, index) => (
            <motion.div
              key={index}
              className="flex items-start p-4 bg-red-500/10 border border-red-500/20 rounded-lg"
              initial={{ x: -50, opacity: 0 }}
              whileInView={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <span className="text-2xl mr-4">{finding.emoji}</span>
              <p className="text-gray-300">{finding.text}</p>
            </motion.div>
          ))}
        </div>
      </ReportSection>

      <ReportSection
        title="Medical Terms"
        icon={<FaBookMedical className="text-3xl text-green-400" />}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {analysisData.terms.map((term, index) => (
            <motion.div
              key={index}
              className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg"
              initial={{ scale: 0.9, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              <h3 className="font-bold text-lg text-green-400 mb-2">{term.term}</h3>
              <p className="text-gray-300">{term.explanation}</p>
            </motion.div>
          ))}
        </div>
      </ReportSection>

      <ReportSection
        title="Recommendations"
        icon={<FaCheckCircle className="text-3xl text-purple-400" />}
      >
        <div className="space-y-4">
          {analysisData.recommendations.map((rec, index) => (
            <motion.div
              key={index}
              className="flex items-start p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg"
              initial={{ y: 50, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex-shrink-0 w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mr-4">
                <span className="text-2xl">{rec.emoji}</span>
              </div>
              <div>
                <h4 className="font-bold text-purple-400 mb-1">{rec.title}</h4>
                <p className="text-gray-300">{rec.description}</p>
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
    <div className="min-h-screen text-white relative snap-y snap-mandatory h-screen overflow-y-scroll scroll-styled">
      <BlurryBackground />
      
      <div className="max-w-4xl mx-auto p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <FileUploadSection
            onFileUpload={handleFileUpload}
            loading={loading}
            error={error}
            uploadedFile={uploadedFile}
          />

          <AnimatePresence>
            {pdfText && analysis && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <MedicalReport analysis={analysis} />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
};

export default MedicalReports;