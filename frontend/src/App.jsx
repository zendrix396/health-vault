import { useState } from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Reports from "./pages/Reports";
import Recommendations from "./pages/Recommendations";

function App() {
  const [currentPage, setCurrentPage] = useState("home");

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return <Home onNavigate={setCurrentPage} />;
      case "reports":
        return <Reports />;
      case "recommendations":
        return <Recommendations />;
      case "login":
        return (
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-zinc-500 animate-in fade-in duration-500">
            <div className="w-16 h-16 border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm flex items-center justify-center mb-6">
              <span className="text-2xl">🔒</span>
            </div>
            <h2 className="text-xl font-medium text-white mb-2">
              Access Restricted
            </h2>
            <p className="text-zinc-500 font-mono text-sm">
              Demo environment. Login unavailable.
            </p>
            <button
              onClick={() => setCurrentPage("home")}
              className="mt-6 text-sm text-white border-b border-transparent hover:border-white transition-all"
            >
              Return Home
            </button>
          </div>
        );
      default:
        return <Home onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white selection:bg-white selection:text-black font-sans relative">
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-grid-white opacity-[0.15]"></div>
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[600px] bg-[radial-gradient(circle_at_center,rgba(56,189,248,0.08),transparent_70%)]"></div>
        <div className="absolute top-[20%] right-0 w-[500px] h-[500px] bg-[radial-gradient(circle_at_center,rgba(139,92,246,0.05),transparent_70%)]"></div>
      </div>

      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar currentPage={currentPage} onNavigate={setCurrentPage} />
        <main className="flex-grow pt-0 pb-16">{renderPage()}</main>

        <footer className="border-t border-zinc-900 bg-black/50 backdrop-blur-md py-8">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center text-xs text-zinc-600 uppercase tracking-widest font-mono">
            <div className="flex items-center gap-4">
              <div className="w-2 h-2 bg-green-900 rounded-full border border-green-700 animate-pulse"></div>
              <span>MediAI System v2.0.0</span>
            </div>
            <p className="mt-4 md:mt-0">
              &copy; {new Date().getFullYear()} MediAI Inc.
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;