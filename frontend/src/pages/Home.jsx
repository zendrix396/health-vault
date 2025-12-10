import { ArrowRight, FileText, Activity, Terminal, Lock } from "lucide-react";

const Home = ({ onNavigate }) => {
  return (
    <div className="w-full tint-surface">
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-20 lg:py-32">
        <div className="mb-24 relative">
          <div className="absolute -top-20 -left-20 w-[300px] h-[300px] bg-blue-500/10 rounded-full blur-[100px] pointer-events-none"></div>

          <div className="relative">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-zinc-900/80 border border-zinc-800 text-zinc-400 text-xs font-mono mb-8 backdrop-blur-sm">
              <span className="w-2 h-2 bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"></span>
              SYSTEM OPERATIONAL
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-8 max-w-4xl leading-[1.1]">
              Healthcare Intelligence <br />
              <span className="inline-block italic text-zinc-300 font-semibold">
                Infrastructure
              </span>
            </h1>

            <p className="text-xl text-zinc-400 max-w-2xl mb-12 font-light leading-relaxed">
              Deploy AI-powered analysis for medical diagnostics. Process reports and generate treatment protocols with zero latency.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => onNavigate("reports")}
                className="group flex items-center justify-center gap-4 px-8 py-4 bg-white text-black font-semibold hover:bg-zinc-200 transition-all active:translate-y-0.5"
              >
                Start Analysis
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={() => onNavigate("recommendations")}
                className="flex items-center justify-center gap-4 px-8 py-4 bg-zinc-900/50 text-white border border-zinc-800 font-semibold hover:bg-zinc-900 transition-all backdrop-blur-sm"
              >
                Run Protocol
              </button>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-px bg-zinc-800/50 border border-zinc-800 overflow-hidden">
          <div
            onClick={() => onNavigate("reports")}
            className="group relative cursor-pointer bg-zinc-950/40 p-10 hover:bg-zinc-900/60 transition-colors backdrop-blur-sm"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

            <div className="relative z-10">
              <div className="w-10 h-10 bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-6 text-white group-hover:border-zinc-600 transition-colors">
                <FileText className="w-5 h-5" />
              </div>

              <h2 className="text-xl font-bold text-white mb-2">Diagnostic Report Parsing</h2>
              <p className="text-zinc-500 mb-8 leading-relaxed text-sm group-hover:text-zinc-400 transition-colors">
                Ingest PDF and image data. Extract key biomarkers and flag anomalies against standard ranges.
              </p>

              <div className="flex items-center text-white text-sm font-mono opacity-0 group-hover:opacity-100 transition-opacity transform translate-y-2 group-hover:translate-y-0">
                <span className="mr-2 text-zinc-400">INITIALIZE</span>
                <ArrowRight className="w-3 h-3 text-white" />
              </div>
            </div>
          </div>

          <div
            onClick={() => onNavigate("recommendations")}
            className="group relative cursor-pointer bg-zinc-950/40 p-10 hover:bg-zinc-900/60 transition-colors backdrop-blur-sm"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

            <div className="relative z-10">
              <div className="w-10 h-10 bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-6 text-white group-hover:border-zinc-600 transition-colors">
                <Activity className="w-5 h-5" />
              </div>

              <h2 className="text-xl font-bold text-white mb-2">Recommendation Engine</h2>
              <p className="text-zinc-500 mb-8 leading-relaxed text-sm group-hover:text-zinc-400 transition-colors">
                Match symptoms to pharmaceutical databases. Custom training data ingestion supported via Excel.
              </p>

              <div className="flex items-center text-white text-sm font-mono opacity-0 group-hover:opacity-100 transition-opacity transform translate-y-2 group-hover:translate-y-0">
                <span className="mr-2 text-zinc-400">EXECUTE</span>
                <ArrowRight className="w-3 h-3 text-white" />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8 border-t border-zinc-800/50 pt-10">
          <div>
            <p className="text-zinc-600 text-xs font-mono uppercase mb-2">Uptime</p>
            <p className="text-white font-mono bg-green-500/10 inline-block px-2 py-0.5 rounded text-green-400 text-sm">
              99.99%
            </p>
          </div>
          <div>
            <p className="text-zinc-600 text-xs font-mono uppercase mb-2">Security</p>
            <div className="flex items-center gap-2 text-zinc-300 font-mono text-sm">
              <Lock className="w-3 h-3 text-zinc-500" /> HIPAA
            </div>
          </div>
          <div>
            <p className="text-zinc-600 text-xs font-mono uppercase mb-2">Engine</p>
            <div className="flex items-center gap-2 text-zinc-300 font-mono text-sm">
              <Terminal className="w-3 h-3 text-zinc-500" /> Gemini 2.5
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;

