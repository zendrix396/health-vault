import { useState, useRef, useEffect } from "react";
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

  FaArrowRight,
  FaImage
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
    transform: rotate(-1deg) !important;
  }
  
  .manga-fade-in {
    animation: fadeIn 0.5s ease-in-out !important;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  @media (max-width: 768px) {
    .manga-text {
      font-size: 0.95em !important;
    }
    
    .report-section-title {
      font-size: 1.5rem !important;
    }
    
    .report-section {
      padding-left: 0.5rem !important;
      padding-right: 0.5rem !important;
    }
    
    /* Disable smooth scrolling on mobile */
    .mobile-scroll {
      scroll-behavior: auto !important;
    }
    
    /* Non-sticky section headers on mobile */
    .section-header {
      position: relative !important;
      top: auto !important;
      margin-top: 0 !important;
      margin-bottom: 1.5rem !important;
      padding-top: 1rem !important;
      padding-bottom: 1rem !important;
    }
  }
  
  /* For smoother scrolling on desktop only */
  @media (min-width: 769px) {
    .desktop-scroll {
      scroll-behavior: smooth;
      scroll-padding-top: 6rem;
    }
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

const BlurryBackground = () => (
  <div className="fixed inset-0 -z-10 overflow-hidden">
    <div className="absolute inset-0 bg-gray-100"></div>
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

const ReportSection = ({ title, icon, children, id }) => {
  // Track if this section has been seen
  const [hasAnimated, setHasAnimated] = useState(false);
  const sectionRef = useRef(null);
  const isMobile = typeof window !== 'undefined' ? window.innerWidth <= 768 : false;

  return (
    <motion.div
      id={id}
      ref={sectionRef}
      className={`min-h-screen p-4 md:p-8 report-section mt-8 md:mt-16 ${isMobile ? "snap-start" : ""}`}
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      onAnimationComplete={() => setHasAnimated(true)}
    >
      <GlassCard className="p-4 md:p-6 manga-fade-in">
        <div className="md:sticky section-header bg-white/90 z-10 py-4 px-4 flex items-center mb-6 manga-border border-t-0 border-x-0 md:-mt-4 md:-mx-4">
          {icon}
          <h2 className="text-xl md:text-2xl font-black ml-4 text-black manga-text transform -rotate-2 report-section-title">{title}</h2>
        </div>
        <div className="mt-4 md:mt-8">
          {children}
        </div>
      </GlassCard>
    </motion.div>
  );
};

const FileUploadSection = ({ onFileUpload, loading, error, uploadedFile }) => (
  <GlassCard className="p-4 md:p-6 mb-8 manga-fade-in">
    <div className="relative">
      <input
        type="file"
        accept=".pdf,.jpg,.jpeg,.png,.gif,.bmp,.webp"
        onChange={onFileUpload}
        className="hidden"
        id="file-upload"
      />
      <label
        htmlFor="file-upload"
        className="flex flex-col items-center justify-center p-4 md:p-8 border-2 border-dashed border-black rounded-none cursor-pointer
                 hover:border-blue-500 transition-colors duration-300 manga-border"
      >
        <div className="flex flex-row items-center justify-center mb-4 space-x-4">

          <FaFileUpload className="text-3xl md:text-4xl text-black transform -rotate-6" />
          <FaImage className="text-3xl md:text-4xl text-black transform rotate-6" />
        </div>
        <span className="text-black text-base md:text-lg mb-2 manga-text font-bold text-center">
          Drop your medical report here or click to browse
        </span>
        <span className="text-gray-700 text-xs md:text-sm manga-text text-center">Supports PDF and image files (JPEG, PNG, GIF, BMP, WebP)</span>

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
          <FaTimesCircle className="mr-2 flex-shrink-0" />
          <span className="text-sm md:text-base">{error}</span>
        </motion.div>
      )}

      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="mt-4 p-4 bg-blue-100 manga-border flex items-center justify-center text-black manga-text font-bold"
        >
          <FaSpinner className="animate-spin mr-2 flex-shrink-0" />
          <span className="text-sm md:text-base">Processing your document...</span>
        </motion.div>
      )}

      {uploadedFile && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="mt-4 p-4 bg-green-100 manga-border flex items-center text-black manga-text font-bold"
        >
          <FaFileAlt className="mr-2 flex-shrink-0" />
          <span className="text-sm md:text-base truncate">Successfully uploaded: {uploadedFile}</span>
        </motion.div>
      )}
    </AnimatePresence>
  </GlassCard>
);

const MedicalReport = ({ analysis }) => {
  let analysisData;
  try {
    analysisData = typeof analysis === 'string' ? JSON.parse(analysis) : analysis;
  } catch (error) {
    console.error("Error parsing analysis JSON:", error);
    console.error("Raw analysis data:", analysis);
    // Return a fallback component for invalid JSON
    return (
      <div className="mt-4 p-4 bg-red-100 manga-border text-red-600 manga-text font-bold">
        <h3 className="text-lg font-bold mb-2">Analysis Error</h3>
        <p className="text-sm">Unable to parse the analysis data. Raw response:</p>
        <pre className="mt-2 text-xs bg-white p-2 rounded overflow-auto max-h-40">
          {typeof analysis === 'string' ? analysis : JSON.stringify(analysis, null, 2)}
        </pre>
      </div>
    );
  }
  const [animatedSections, setAnimatedSections] = useState({
    findings: false,
    terms: false,
    recommendations: false
  });
  const isMobile = typeof window !== 'undefined' ? window.innerWidth <= 768 : false;

  return (
    <div className={`h-screen overflow-y-scroll ${isMobile ? "mobile-scroll" : "desktop-scroll md:snap-y md:snap-mandatory"}`}>
      <ReportSection
        id="summary-section"
        title="Summary"
        icon={<FaClipboardList className="text-2xl md:text-3xl text-black transform -rotate-12" />}
      >
        <motion.div
          className="bg-blue-100 manga-border p-4 md:p-6 w-full"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <p className="text-base md:text-lg leading-relaxed text-black manga-text font-bold">
            {analysisData.summary}
          </p>
        </motion.div>
      </ReportSection>

      <ReportSection
        id="findings-section"
        title="Key Findings"
        icon={<FaHeartbeat className="text-2xl md:text-3xl text-black transform -rotate-12" />}
      >
        <div className="space-y-3 md:space-y-4">
          {analysisData.findings.map((finding, index) => (
            <motion.div
              key={index}
              className="flex items-start p-3 md:p-4 bg-red-100 manga-border"
              initial={{ x: -50, opacity: 0 }}
              whileInView={{ x: 0, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
            >
              <span className="text-xl md:text-2xl mr-3 md:mr-4 transform -rotate-6 flex-shrink-0">{finding.emoji}</span>
              <p className="text-black manga-text font-bold text-sm md:text-base">
                {finding.text}
              </p>
            </motion.div>
          ))}
        </div>
      </ReportSection>

      <ReportSection
        id="terms-section"
        title="Medical Terms"
        icon={<FaBookMedical className="text-2xl md:text-3xl text-black transform -rotate-12" />}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
          {analysisData.terms.map((term, index) => (
            <motion.div
              key={index}
              className="p-3 md:p-4 bg-green-100 manga-border"
              initial={{ scale: 0.9, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02, rotate: -1 }}
            >
              <h3 className="font-black text-base md:text-lg text-black mb-1 md:mb-2 manga-text transform -rotate-2">
                {term.term}
              </h3>
              <p className="text-black manga-text font-bold text-sm md:text-base">
                {term.explanation}
              </p>
            </motion.div>
          ))}
        </div>
      </ReportSection>

      <ReportSection
        id="recommendations-section"
        title="Recommendations"
        icon={<FaCheckCircle className="text-2xl md:text-3xl text-black transform -rotate-12" />}
      >
        <div className="space-y-3 md:space-y-4">
          {analysisData.recommendations.map((rec, index) => (
            <motion.div
              key={index}
              className="flex items-start p-3 md:p-4 bg-purple-100 manga-border"
              initial={{ y: 50, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.01, rotate: -1 }}
            >
              <div className="flex-shrink-0 w-10 h-10 md:w-12 md:h-12 manga-border rounded-none flex items-center justify-center mr-3 md:mr-4 bg-white">
                <span className="text-xl md:text-2xl transform -rotate-6">{rec.emoji}</span>
              </div>
              <div>
                <h4 className="font-black text-base md:text-lg text-black mb-1 manga-text transform -rotate-2">
                  {rec.title}
                </h4>
                <p className="text-black manga-text font-bold text-sm md:text-base">
                  {rec.description}
                </p>
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
  const scrollContainerRef = useRef(null);
  const summaryRef = useRef(null);

  // Handle auto-scrolling when analysis is complete
  useEffect(() => {
    if (analysis && !loading) {
      setTimeout(() => {
        const summarySection = document.getElementById('summary-section');
        if (summarySection) {
          const isMobile = window.innerWidth <= 768;
          // Use different scrolling methods based on device
          if (isMobile) {
            // Simple scrolling for mobile
            summarySection.scrollIntoView();
          } else {
            // Smooth scrolling for desktop
            summarySection.scrollIntoView({ behavior: 'smooth' });
          }
        }
      }, 500); // Short delay to allow rendering
    }
  }, [analysis, loading]);

  const handleFileUpload = async (event) => {
    console.log("File upload handler called");
    const file = event.target.files[0];
    if (!file) {
      console.log("No file selected");
      return;
    }

    console.log("File selected:", {
      name: file.name,
      type: file.type,
      size: file.size,
      lastModified: file.lastModified
    });

    // Check if file is a PDF or supported image type
    const validImageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
    const isPdf = file.type === 'application/pdf';
    const isImage = validImageTypes.includes(file.type);

    console.log("File validation:", {
      isPdf,
      isImage,
      fileType: file.type,
      validImageTypes
    });

    if (!isPdf && !isImage) {
      console.error("Invalid file type:", file.type);
      setError("Please upload a PDF or supported image file (JPEG, PNG, GIF, BMP, WebP)");
      return;
    }

    console.log("File validation passed, creating FormData");
    const formData = new FormData();
    formData.append("file_upload", file);
    console.log("FormData created, file appended");

    console.log("Setting loading state to true");
    setLoading(true);
    setError(null);

    try {
      console.log("Starting file upload to:", "http://localhost:8000/upload");
      console.log("File details:", {
        name: file.name,
        type: file.type,
        size: file.size
      });
      
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      
      console.log("Upload response status:", response.status);
      console.log("Upload response ok:", response.ok);

      const data = await response.json();
      console.log("Upload response data:", data);

      if (!response.ok) {
        console.error("Upload failed with status:", response.status);
        console.error("Error data:", data);
        throw new Error(data.detail || "Upload failed");
      }

      console.log("Upload successful! Setting state...");
      setUploadedFile(data.filename);
      setPdfText(data.text_content);
      setAnalysis(data.analysis);
      setError(null);
      console.log("State updated successfully");
    } catch (error) {
      console.error("Error uploading file:", error);
      console.error("Error details:", {
        message: error.message,
        stack: error.stack,
        name: error.name
      });
      setError(error.message || "Failed to upload file");
      setUploadedFile(null);
      setPdfText("");
      setAnalysis(null);
    } finally {
      console.log("Upload process completed, setting loading to false");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen text-black relative h-screen overflow-y-scroll bg-gray-100" ref={scrollContainerRef}>
      <BlurryBackground />
      
      <div className="w-full max-w-4xl mx-auto p-3 md:p-6 pt-16 md:pt-16">
        <div className="flex items-center justify-center mb-6 md:mb-8">
          <FaBookMedical className="h-12 w-12 md:h-16 md:w-16 text-black transform -rotate-12" />
        </div>
        <h2 className="manga-text text-2xl md:text-3xl font-black text-center text-black mb-6 md:mb-8 transform -rotate-2">
          Medical Report Analyzer
        </h2>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4 md:space-y-6"
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
                className="manga-fade-in"
                ref={summaryRef}
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
