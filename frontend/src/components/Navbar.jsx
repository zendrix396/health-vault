import { motion } from "framer-motion";
import { AnimatePresence } from "framer-motion";
import { 
  FaStethoscope, 
  FaSun, 
  FaMoon, 
  FaUserCircle,
  FaHome,
  FaFileMedical,
  FaPills,
  FaUserMd,
  FaTimes,
} from "react-icons/fa";
import { useState } from "react";

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
if (typeof document !== 'undefined') {
  const styleElement = document.createElement('style');
  styleElement.textContent = mangaStyles;
  document.head.appendChild(styleElement);
}

const GlassCard = ({ children, className = "" }) => (
  <div className={`bg-white/90 border-b border-black manga-border shadow-lg ${className}`}>
    {children}
  </div>
);

const NavLink = ({ icon, text, isActive, onClick }) => (
  <motion.button
    whileHover={{ scale: 1.05, rotate: -2 }}
    whileTap={{ scale: 0.95 }}
    onClick={onClick}
    className={`flex items-center px-4 py-2 rounded-none transition-all duration-300 manga-text font-bold
                ${isActive 
                  ? 'bg-blue-100 text-black manga-border' 
                  : 'hover:bg-white text-black hover:manga-border'}`}
  >
    {icon}
    <span className="ml-2">{text}</span>
  </motion.button>
);

const LoginModal = ({ isOpen, onClose }) => (
  <AnimatePresence>
    {isOpen && (
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
          className="relative w-full max-w-md manga-fade-in"
        >
          <GlassCard className="p-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-black text-black manga-text">Login to MediAI</h2>
              <motion.button
                whileHover={{ scale: 1.1, rotate: 10 }}
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
                className="text-black hover:text-red-600"
              >
                <FaTimes className="text-xl transform -rotate-6" />
              </motion.button>
            </div>

            <form className="space-y-4">
              <div>
                <label className="block text-black mb-2 manga-text font-bold">Email</label>
                <input
                  type="email"
                  className="w-full p-3 rounded-none bg-white manga-border
                           text-black placeholder-gray-500 focus:border-blue-500 
                           focus:ring-2 focus:ring-blue-500/20 outline-none"
                  placeholder="Enter your email"
                />
              </div>

              <div>
                <label className="block text-black mb-2 manga-text font-bold">Password</label>
                <input
                  type="password"
                  className="w-full p-3 rounded-none bg-white manga-border
                           text-black placeholder-gray-500 focus:border-blue-500 
                           focus:ring-2 focus:ring-blue-500/20 outline-none"
                  placeholder="Enter your password"
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded-none border-black bg-white
                             text-blue-500 focus:ring-blue-500/20"
                  />
                  <span className="ml-2 text-black manga-text font-bold">Remember me</span>
                </label>
                <a href="#" className="text-blue-600 hover:text-blue-800 manga-text font-bold">
                  Forgot password?
                </a>
              </div>

              <motion.button
                whileHover={{ scale: 1.02, rotate: -1 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-3 bg-black hover:bg-gray-800 
                         text-white rounded-none font-black transition-colors manga-border manga-text"
              >
                Login
              </motion.button>

              <div className="text-center text-black manga-text font-bold">
                Don't have an account?{" "}
                <a href="#" className="text-blue-600 hover:text-blue-800">
                  Sign up
                </a>
              </div>
            </form>
          </GlassCard>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

const Navbar = ({ currentPage, setCurrentPage, isDarkMode, setIsDarkMode }) => {
  const [showLogin, setShowLogin] = useState(false);

  const navItems = [
    { id: 'home', text: 'Home', icon: <FaHome /> },
    { id: 'Medical Report Analysis', text: 'Medical Reports', icon: <FaFileMedical /> },
    { id: 'Medicine Recommendations', text: 'Recommendations', icon: <FaPills /> },
  ];

  return (
    <>
      <GlassCard className="fixed top-0 w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <motion.div 
              className="flex items-center cursor-pointer"
              whileHover={{ scale: 1.05, rotate: -2 }}
              onClick={() => setCurrentPage('home')}
            >
              <FaStethoscope className="text-black text-3xl transform -rotate-12" />
              <span className="ml-2 text-xl font-black text-black manga-text">MediAI</span>
            </motion.div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-2">
              {navItems.map((item) => (
                <NavLink
                  key={item.id}
                  icon={item.icon}
                  text={item.text}
                  isActive={currentPage === item.id}
                  onClick={() => setCurrentPage(item.id)}
                />
              ))}
            </div>

            {/* Right Side Controls */}
            <div className="flex items-center space-x-4">
              <motion.button
                whileHover={{ scale: 1.1, rotate: 10 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="p-2 rounded-none hover:bg-white/5 manga-border"
              >
                {isDarkMode ? 
                  <FaSun className="text-black transform -rotate-6" /> : 
                  <FaMoon className="text-black transform -rotate-6" />
                }
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.1, rotate: -2 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowLogin(true)}
                className="flex items-center px-4 py-2 rounded-none bg-black hover:bg-gray-800 text-white manga-text font-black manga-border"
              >
                <FaUserCircle className="mr-2 transform -rotate-6" />
                Login
              </motion.button>
            </div>
          </div>
        </div>
      </GlassCard>
      <LoginModal 
        isOpen={showLogin} 
        onClose={() => setShowLogin(false)} 
      />
    </>
  );
};

export default Navbar;