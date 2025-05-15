import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import {
  FaStethoscope,
  FaFileMedical,
  FaPills,
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
`;

// Add styling to head
if (typeof document !== "undefined") {
  const styleElement = document.createElement("style");
  styleElement.textContent = mangaStyles;
  document.head.appendChild(styleElement);
}

// Update the BlurryBackground component
const BlurryBackground = () => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Light background instead of dark */}
      <div className="absolute inset-0 bg-gray-100"></div>

      {/* Animated blurry shapes with reduced blur */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360],
          x: [0, 100, 0],
          y: [0, -50, 0],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-blue-500/10 blur-[80px]"
      />
      <motion.div
        animate={{
          scale: [1.2, 1, 1.2],
          rotate: [0, -180, -360],
          x: [0, -100, 0],
          y: [0, 50, 0],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute top-1/3 right-1/4 w-96 h-96 rounded-full bg-purple-500/10 blur-[80px]"
      />
      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          rotate: [0, 90, 360],
          x: [0, 50, 0],
          y: [0, 100, 0],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute bottom-1/4 left-1/3 w-96 h-96 rounded-full bg-green-500/10 blur-[80px]"
      />
    </div>
  );
};

const GlassCard = ({ children, className = "" }) => (
  <div
    className={`bg-white/90 border-black rounded-none manga-border shadow-lg ${className}`}
  >
    {children}
  </div>
);

const HomePage = ({ setCurrentPage }) => {
  const [isDark, setIsDark] = useState(true);
  const [showLogin, setShowLogin] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const features = [
    {
      icon: (
        <FaFileMedical className="text-4xl text-black transform -rotate-12" />
      ),
      title: "Medical Report Analysis",
      description:
        "Upload and analyze medical reports with AI-powered insights",
    },
    {
      icon: <FaPills className="text-4xl text-black transform -rotate-12" />,
      title: "Medicine Recommendations",
      description: "Get personalized medicine suggestions based on symptoms",
    },
  ];

  return (
    <div className="min-h-screen text-black relative overflow-hidden">
      <BlurryBackground />

      {/* Hero Section */}
      <div className="pt-24 pb-20">
        <motion.div
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div className="flex items-center justify-center mb-6">
            <FaStethoscope className="h-16 w-16 text-black transform -rotate-12" />
          </motion.div>
          <motion.h1 className="text-6xl font-black text-center mb-6 text-black manga-text transform -rotate-2">
            Welcome to MedMosaic
          </motion.h1>
          <motion.p className="text-xl text-center mb-12 text-black manga-text font-bold">
            Your AI-powered medical assistant for smarter healthcare decisions
          </motion.p>

          {/* Features Grid */}
          <div className="grid grid-rows-1 md:grid-rows-2 gap-8 mt-12 sm:mt-16 lg:mt-23">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05, rotate: -1 }}
                className="cursor-pointer manga-fade-in"
                onClick={() => setCurrentPage(feature.title)}
              >
                <GlassCard className="p-4 md:p-6 h-full transition-all duration-300 hover:bg-blue-50 max-w-xl mx-auto w-full">
                  <div className="flex items-center mb-4 justify-center">
                    {feature.icon}
                    <h3 className="text-lg md:text-xl font-black ml-4 manga-text transform -rotate-2 text-center">
                      {feature.title}
                    </h3>
                  </div>
                  <p className="text-black manga-text font-bold text-center">
                    {feature.description}
                  </p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Login Modal */}
      <AnimatePresence>
        {showLogin && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, rotate: 0 }}
              animate={{ scale: 1, opacity: 1, rotate: -1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="relative manga-fade-in"
            >
              <GlassCard className="p-8 max-w-md w-full">
                <h2 className="text-2xl font-black mb-6 manga-text transform -rotate-2">
                  Login to MedMosaic
                </h2>
                <input
                  type="email"
                  placeholder="Email"
                  className="w-full p-3 rounded-none mb-4 bg-white manga-border text-black focus:border-blue-400 outline-none"
                />
                <input
                  type="password"
                  placeholder="Password"
                  className="w-full p-3 rounded-none mb-6 bg-white manga-border text-black focus:border-blue-400 outline-none"
                />
                <div className="flex justify-between">
                  <motion.button
                    whileHover={{ scale: 1.05, rotate: -2 }}
                    whileTap={{ scale: 0.95 }}
                    className="bg-black text-white px-6 py-2 rounded-none manga-border manga-text font-black"
                  >
                    Login
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05, rotate: 2 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setShowLogin(false)}
                    className="bg-white px-6 py-2 rounded-none manga-border manga-text font-black text-black"
                  >
                    Cancel
                  </motion.button>
                </div>
              </GlassCard>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HomePage;
