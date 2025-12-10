import { useState } from "react";
import FileUpload from "../components/FileUpload";
import api from "../api";
import { Loader2, TerminalSquare, AlertTriangle, ArrowRight } from "lucide-react";

const Reports = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [analysisObj, setAnalysisObj] = useState(null);
  const [language, setLanguage] = useState("english"); // english | hindi | hinglish
  const [error, setError] = useState(null);

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
    setResult(null);
    setError(null);
  };

  const normalizeAnalysis = (payload) => {
    const fallback = {
      summary: [
        "No analysis available. Please try again with a different file or check your API configuration.",
      ],
      findings: [],
      terms: [],
      recommendations: [],
    };

    const candidate = payload?.analysis ?? payload;
    if (!candidate) return fallback;

    if (typeof candidate === "object") {
      const normalized = {
        summary: candidate.summary ?? fallback.summary,
        findings: Array.isArray(candidate.findings) ? candidate.findings : [],
        terms: Array.isArray(candidate.terms) ? candidate.terms : [],
        recommendations: Array.isArray(candidate.recommendations)
          ? candidate.recommendations
          : [],
      };
      if (typeof normalized.summary === "string") {
        normalized.summary = normalized.summary
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean);
      }
      return normalized;
    }

    if (typeof candidate === "string") {
      try {
        const parsed = JSON.parse(candidate);
        const normalized = {
          summary: parsed.summary ?? fallback.summary,
          findings: Array.isArray(parsed.findings) ? parsed.findings : [],
          terms: Array.isArray(parsed.terms) ? parsed.terms : [],
          recommendations: Array.isArray(parsed.recommendations)
            ? parsed.recommendations
            : [],
        };
        if (typeof normalized.summary === "string") {
          normalized.summary = normalized.summary
            .split("\n")
            .map((s) => s.trim())
            .filter(Boolean);
        }
        return normalized;
      } catch (err) {
        return { ...fallback, summary: candidate };
      }
    }

    return fallback;
  };

  const formatRichText = (text) => {
    if (!text) return "";
    // Convert ****bold**** then **italics**
    const boldFirst = text.replace(/\*{4}(.*?)\*{4}/g, "<strong>$1</strong>");
    const italics = boldFirst.replace(/\*{2}(.*?)\*{2}/g, "<em>$1</em>");
    return italics;
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);
    setAnalysisObj(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file_upload", file);
      formData.append("language", language);
      const response = await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const data = response.data;
      const normalized = normalizeAnalysis(data);
      setAnalysisObj(normalized);
      setResult(
        typeof data === "string"
          ? data
          : data?.analysis
          ? JSON.stringify(data.analysis, null, 2)
          : JSON.stringify(data, null, 2)
      );
    } catch (err) {
      setError("An error occurred while analyzing the report.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tint-surface">
      <div className="relative z-10 max-w-5xl mx-auto px-6 py-10">
      <header className="mb-12 border-b border-zinc-800/60 pb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Report Analyzer</h1>
        <p className="text-zinc-500 font-mono text-sm">
          Upload diagnostic imaging or PDF reports for OCR and AI analysis.
        </p>
      </header>

      <div className="grid md:grid-cols-3 gap-12">
        <div className="md:col-span-1 space-y-6">
          <div className="bg-zinc-900/30 border border-zinc-800 p-1 backdrop-blur-sm">
            <FileUpload
              accept=".pdf,image/png,image/jpeg,image/webp,image/gif"
              onFileSelect={handleFileSelect}
              label="Select Source File"
            />
          </div>

            <div className="bg-zinc-900/30 border border-zinc-800 p-4 space-y-2 text-sm text-zinc-200">
              <p className="text-xs font-mono text-zinc-500 uppercase tracking-wide">
                Response Language
              </p>
              <div className="flex flex-col gap-2">
                {[
                  { value: "english", label: "English" },
                  { value: "hindi", label: "Hindi" },
                  { value: "hinglish", label: "Hinglish" },
                ].map((opt) => (
                  <label
                    key={opt.value}
                    className={`flex items-center gap-2 px-3 py-2 border transition-colors cursor-pointer ${
                      language === opt.value
                        ? "border-zinc-600 bg-zinc-900/60 text-white"
                        : "border-zinc-800 bg-zinc-900/20 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200"
                    }`}
                  >
                    <input
                      type="radio"
                      name="language"
                      value={opt.value}
                      checked={language === opt.value}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="accent-white bg-zinc-900 border-zinc-700"
                    />
                    <span>{opt.label}</span>
                  </label>
                ))}
              </div>
            </div>

          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className={`w-full flex items-center justify-center gap-3 px-6 py-3 font-medium text-sm transition-all border ${
              !file || loading
                ? "bg-zinc-900/50 border-zinc-800 text-zinc-600 cursor-not-allowed"
                : "bg-white border-white text-black hover:bg-zinc-200"
            }`}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>PROCESSING...</span>
              </>
            ) : (
              <>
                <span>RUN ANALYSIS</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>

          {error && (
            <div className="text-sm text-red-400 font-mono bg-red-500/10 border border-red-500/40 px-3 py-2">
              {error}
            </div>
          )}
        </div>

        <div className="md:col-span-2">
          {!result && !loading && (
            <div className="h-64 border border-dashed border-zinc-800/60 flex flex-col items-center justify-center text-zinc-600 bg-zinc-900/10 backdrop-blur-sm">
              <TerminalSquare className="w-8 h-8 mb-4 opacity-50" />
              <p className="font-mono text-xs uppercase tracking-widest">
                Waiting for input stream...
              </p>
            </div>
          )}

          {loading && (
            <div className="h-64 border border-zinc-800/60 bg-zinc-900/10 backdrop-blur-sm p-6 font-mono text-sm text-zinc-400">
              <p className="flex items-center gap-2">
                <span className="animate-pulse text-green-500">●</span> Uploading
                file payload...
              </p>
              <p className="flex items-center gap-2 mt-2">
                <span className="animate-pulse text-green-500 delay-75">●</span>{" "}
                Initiating vision model...
              </p>
              <p className="flex items-center gap-2 mt-2">
                <span className="animate-pulse text-green-500 delay-150">●</span>{" "}
                Parsing medical terminology...
              </p>
            </div>
          )}

          {analysisObj && (
            <div className="border border-zinc-800 bg-black/80 backdrop-blur-md animate-in fade-in duration-500">
              <div className="flex items-center justify-between px-4 py-2 border-b border-zinc-800 bg-zinc-900/50">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-zinc-700"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-zinc-700"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-zinc-700"></div>
                </div>
                <div className="text-[10px] font-mono text-zinc-500 uppercase">
                  Output.log
                </div>
              </div>

              <div className="p-6 space-y-6 max-h-[70vh] overflow-auto scroll-styled">
                <div className="space-y-2">
                  <h3 className="text-sm font-mono text-zinc-400 uppercase tracking-wide">
                    Summary
                  </h3>
                  <div className="bg-zinc-900/40 border border-zinc-800 p-4 leading-relaxed text-zinc-200">
                    {Array.isArray(analysisObj.summary) ? (
                      <ul className="list-disc ml-4 space-y-1">
                        {analysisObj.summary.map((item, idx) => (
                          <li
                            key={idx}
                            className="text-zinc-200 text-sm"
                            dangerouslySetInnerHTML={{
                              __html: formatRichText(item),
                            }}
                          />
                        ))}
                      </ul>
                    ) : (
                      <p
                        className="text-zinc-200 text-sm"
                        dangerouslySetInnerHTML={{
                          __html: formatRichText(analysisObj.summary),
                        }}
                      />
                    )}
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="text-sm font-mono text-zinc-400 uppercase tracking-wide">
                    Findings
                  </h3>
                  {analysisObj.findings.length === 0 ? (
                    <p className="text-zinc-600 text-sm">No findings provided.</p>
                  ) : (
                    <div className="grid md:grid-cols-2 gap-3">
                      {analysisObj.findings.map((f, idx) => (
                        <div
                          key={idx}
                          className="flex gap-3 bg-zinc-900/30 border border-zinc-800 p-3 text-zinc-200"
                        >
                          <span className="text-lg">{f.emoji || "•"}</span>
                          <p
                            className="text-sm leading-relaxed"
                            dangerouslySetInnerHTML={{
                              __html: formatRichText(f.text),
                            }}
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="space-y-3">
                  <h3 className="text-sm font-mono text-zinc-400 uppercase tracking-wide">
                    Terms
                  </h3>
                  {analysisObj.terms.length === 0 ? (
                    <p className="text-zinc-600 text-sm">No terms provided.</p>
                  ) : (
                    <div className="grid md:grid-cols-2 gap-3">
                      {analysisObj.terms.map((t, idx) => (
                        <div
                          key={idx}
                          className="bg-zinc-900/30 border border-zinc-800 p-3 text-zinc-200"
                        >
                          <p
                            className="font-semibold text-white"
                            dangerouslySetInnerHTML={{
                              __html: formatRichText(t.term),
                            }}
                          />
                          <p
                            className="text-sm text-zinc-400 leading-relaxed"
                            dangerouslySetInnerHTML={{
                              __html: formatRichText(t.explanation),
                            }}
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="space-y-3">
                  <h3 className="text-sm font-mono text-zinc-400 uppercase tracking-wide">
                    Recommendations
                  </h3>
                  {analysisObj.recommendations.length === 0 ? (
                    <p className="text-zinc-600 text-sm">
                      No recommendations provided.
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {analysisObj.recommendations.map((r, idx) => (
                        <div
                          key={idx}
                          className="flex gap-3 bg-zinc-900/30 border border-zinc-800 p-3 text-zinc-200"
                        >
                          <span className="text-lg">{r.emoji || "•"}</span>
                          <div>
                            <p
                              className="font-semibold text-white"
                              dangerouslySetInnerHTML={{
                                __html: formatRichText(r.title),
                              }}
                            />
                            <p
                              className="text-sm text-zinc-400 leading-relaxed"
                              dangerouslySetInnerHTML={{
                                __html: formatRichText(r.description),
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="pt-2 border-t border-zinc-900 flex gap-2 text-xs text-amber-500/80 items-start">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                  <p>AI Generated Analysis. Not a medical diagnosis.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
    </div>
  );
};

export default Reports;

