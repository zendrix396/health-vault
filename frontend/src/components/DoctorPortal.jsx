import { motion } from "framer-motion";
import { FaUserMd, FaLock, FaClock, FaTools, FaMoon } from "react-icons/fa";

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

const FeatureCard = ({ icon, title, description }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-white/90 border-black rounded-none p-6 shadow-lg manga-border manga-fade-in"
  >
    <div className="flex items-center mb-4">
      {icon}
      <h3 className="text-xl font-black ml-3 text-black manga-text transform -rotate-2">{title}</h3>
      <FaMoon className="h-4 w-4 text-black absolute translate-x-32 -translate-y-4" />
    </div>
    <p className="text-black manga-text font-bold">{description}</p>
  </motion.div>
);

const DoctorPortal = () => {
  const features = [
    {
      icon: <FaLock className="text-3xl text-black transform -rotate-12" />,
      title: "Secure Access",
      description: "Protected healthcare professional portal with encrypted data transmission"
    },
    {
      icon: <FaTools className="text-3xl text-black transform -rotate-12" />,
      title: "Advanced Tools",
      description: "Specialized diagnostic and analysis tools for medical professionals"
    },
    {
      icon: <FaClock className="text-3xl text-black transform -rotate-12" />,
      title: "Coming Soon",
      description: "We're working on bringing you more powerful features for patient care"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-100 text-black relative overflow-hidden">
      {/* Background with reduced blur */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-gray-100"></div>
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-purple-500/10 blur-[80px]"
        />
        <motion.div
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [0, -180, -360],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-blue-500/10 blur-[80px]"
        />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <div className="flex items-center justify-center mb-6">
            <FaUserMd className="text-6xl text-black transform -rotate-12 mr-4" />
            <FaMoon className="h-8 w-8 text-black absolute translate-x-8 -translate-y-8" />
            <h1 className="text-4xl font-black text-black manga-text transform -rotate-2">
              Doctor Portal
            </h1>
          </div>
          
          <p className="text-xl text-black max-w-2xl mx-auto manga-text font-bold">
            A specialized platform for healthcare professionals with advanced tools and insights
          </p>
        </motion.div>

        {/* Coming Soon Message */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white/90 border-black rounded-none p-8 shadow-lg max-w-3xl mx-auto mb-16 manga-border manga-fade-in"
        >
          <h2 className="text-2xl font-black mb-4 text-black manga-text transform -rotate-2">
            Portal Access Coming Soon
          </h2>
          <FaMoon className="h-6 w-6 text-black absolute right-8 top-8" />
          <p className="text-black text-lg manga-text font-bold">
            We're currently developing a comprehensive suite of tools for medical professionals. 
            Register your interest to be notified when we launch.
          </p>
        </motion.div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.2 }}
            >
              <FeatureCard {...feature} />
            </motion.div>
          ))}
        </div>

        {/* Registration Interest Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-16 max-w-md mx-auto manga-fade-in"
        >
          <div className="bg-white/90 border-black rounded-none p-8 shadow-lg manga-border">
            <h3 className="text-xl font-black mb-6 text-center text-black manga-text transform -rotate-2">
              Register Your Interest
            </h3>
            <FaMoon className="h-6 w-6 text-black absolute right-8 top-8" />
            <form className="space-y-4">
              <input
                type="email"
                placeholder="Professional Email"
                className="w-full p-3 rounded-none bg-white manga-border text-black placeholder-gray-500 focus:outline-none focus:border-black"
              />
              <select className="w-full p-3 rounded-none bg-white manga-border text-black focus:outline-none focus:border-black manga-text font-bold">
                <option value="">Select Specialization</option>
                <option value="general">General Practice</option>
                <option value="cardiology">Cardiology</option>
                <option value="neurology">Neurology</option>
                <option value="other">Other</option>
              </select>
              <motion.button
                whileHover={{ scale: 1.02, rotate: -2 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-3 rounded-none bg-black text-white font-black manga-border manga-text transition-all duration-300"
              >
                Notify Me
              </motion.button>
            </form>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DoctorPortal;