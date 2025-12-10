import { useEffect, useState } from "react";
import FileUpload from "../components/FileUpload";
import api from "../api";
import { Loader2, Database, Search, Terminal, AlertCircle } from "lucide-react";

const DUMMY_DATA_CONTEXT =
  "Condition: Headache. Medicine: Paracetamol. Dosage: 500mg every 4-6 hours.";

const formatRecommendation = (data) => {
  if (typeof data === "string") return data;
  if (!data) return "";

  if (data.advanced_prediction || data.basic_prediction) {
    const lines = [];
    if (data.advanced_prediction?.disease) {
      lines.push(
        `# Condition`,
        `- ${data.advanced_prediction.disease.name} (${data.advanced_prediction.disease.confidence?.toFixed?.(
          1
        )}% confidence)`
      );
    }
    if (data.advanced_prediction?.medicine) {
      lines.push(
        `# Recommendation`,
        `- ${data.advanced_prediction.medicine.name} (${data.advanced_prediction.medicine.confidence?.toFixed?.(
          1
        )}% confidence)`
      );
    }
    if (data.model_metrics) {
      lines.push(
        `## Model Metrics`,
        `- Disease Accuracy: ${data.model_metrics.disease_accuracy}%`,
        `- Medicine Accuracy: ${data.model_metrics.medicine_accuracy}%`
      );
    }
    return lines.join("\n");
  }

  return JSON.stringify(data, null, 2);
};

const Recommendations = () => {
  const [dataMode, setDataMode] = useState("upload");
  const [trainingFile, setTrainingFile] = useState(null);
  const [isDataReady, setIsDataReady] = useState(false);

  const [age, setAge] = useState("");
  const [gender, setGender] = useState("M");
  const [symptomInput, setSymptomInput] = useState("");
  const [causeInput, setCauseInput] = useState("");
  const [symptomList, setSymptomList] = useState([]);
  const [causeList, setCauseList] = useState([]);

  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(false);
  const [recommendationText, setRecommendationText] = useState(null);
  const [recommendationData, setRecommendationData] = useState(null);
  const [availableSymptoms, setAvailableSymptoms] = useState([]);
  const [availableCauses, setAvailableCauses] = useState([]);
  const [multiAllowed, setMultiAllowed] = useState({ symptoms: true, causes: true });

  useEffect(() => {
    const fetchTerms = async () => {
      try {
        const response = await api.get("/available-terms");
        const data = response.data || {};
        setAvailableSymptoms(data.symptoms || []);
        setAvailableCauses(data.causes || []);
        setMultiAllowed(data.multi_allowed || { symptoms: true, causes: true });
      } catch (err) {
        // fall back to a small static list if backend is unreachable
        setAvailableSymptoms([
          "Headache",
          "Fever",
          "Nausea",
          "Back Pain",
          "Cough",
          "Sore Throat",
          "Acid Reflux",
        ]);
        setAvailableCauses(["Viral Infection", "Stress", "Allergy"]);
      }
    };
    if (isDataReady) {
      fetchTerms();
    }
  }, [isDataReady]);

  const handleDataFileSelect = (file) => {
    setTrainingFile(file);
    setDataLoading(true);
    setTimeout(() => {
      setIsDataReady(true);
      setDataLoading(false);
    }, 800);
  };

  const useDummyData = async () => {
    setDataMode("dummy");
    setDataLoading(true);
    try {
      const resp = await api.get("/dummy-excel", { responseType: "blob" });
      const blob = resp.data;
      const file = new File(
        [blob],
        "data.xlsx",
        { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }
      );
      const fd = new FormData();
      fd.append("file", file);
      const uploadResp = await api.post("/upload-excel", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (uploadResp.status === 200) {
        setTrainingFile({ name: "data.xlsx" });
        setIsDataReady(true);
        // Pull fresh terms after the dummy data is loaded
        const termsResp = await api.get("/available-terms");
        const data = termsResp.data || {};
        setAvailableSymptoms(data.symptoms || []);
        setAvailableCauses(data.causes || []);
        setMultiAllowed(data.multi_allowed || { symptoms: true, causes: true });
      }
    } catch (err) {
      console.error("Failed to init dummy data", err);
    } finally {
      setDataLoading(false);
    }
  };

  const handleGetRecommendation = async () => {
    const hasSymptoms = symptomList.length || symptomInput.trim();
    const hasCauses = causeList.length || causeInput.trim();
    if (!age || !hasSymptoms || !hasCauses) return;
    setLoading(true);
    setRecommendationText(null);
    setRecommendationData(null);
    const ensureLists = () => {
      const finalize = (input, listSetter, listVal) => {
        const parts = (input || "")
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean);
        if (parts.length) {
          listSetter([...new Set([...listVal, ...parts])]);
          return [...new Set([...listVal, ...parts])];
        }
        return listVal;
      };
      const finalSymptoms = finalize(symptomInput, setSymptomList, symptomList);
      const finalCauses = finalize(causeInput, setCauseList, causeList);
      setSymptomInput("");
      setCauseInput("");
      return { finalSymptoms, finalCauses };
    };

    const { finalSymptoms, finalCauses } = ensureLists();

    const payload = {
      age,
      gender: (gender || "").toUpperCase().charAt(0),
      symptoms: finalSymptoms.join(", "),
      cause: finalCauses.join(", "),
    };

    try {
      const response = await api.post("/predict-medical", payload);
      setRecommendationText(formatRecommendation(response.data));
      setRecommendationData(response.data);
    } catch (err) {
      const context =
        dataMode === "dummy"
          ? DUMMY_DATA_CONTEXT
          : "User has uploaded a specific training data file.";
      setRecommendationText(
        `# Unable to reach backend\n- Using local context\n- ${context}`
      );
      setRecommendationData(null);
    } finally {
      setLoading(false);
    }
  };

  const openDataFile = () => {
    if (dataMode === "dummy") {
      window.open(`${api.defaults.baseURL}/dummy-excel`, "_blank");
      return;
    }
    if (trainingFile) {
      const url = URL.createObjectURL(trainingFile);
      window.open(url, "_blank");
    }
  };

  const filterMatches = (value, list) => {
    if (!value) return [];
    const lower = value.toLowerCase();
    return list
      .filter((item) => item.toLowerCase().includes(lower))
      .slice(0, 6);
  };

  return (
    <div className="tint-surface">
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-10">
        <header className="mb-12 border-b border-zinc-800/60 pb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Recommendation Engine
        </h1>
        <p className="text-zinc-500 font-mono text-sm">
          Query training data for treatment protocols based on patient
          variables.
        </p>
      </header>

      <div className="grid lg:grid-cols-12 gap-12 items-start">
        <div className="lg:col-span-4 space-y-8">
          <div className="border border-zinc-800 bg-zinc-900/20 backdrop-blur-sm">
            <div className="px-4 py-3 bg-zinc-900/40 border-b border-zinc-800 flex items-center gap-2">
              <Database className="w-4 h-4 text-zinc-400" />
              <span className="text-xs font-mono uppercase text-zinc-400">
                Context Data
              </span>
            </div>

            <div className="p-6">
              {!isDataReady ? (
                <div className="space-y-4">
                  <FileUpload
                    accept=".xlsx, .xls"
                    onFileSelect={handleDataFileSelect}
                    label="Load Knowledge Base"
                    subLabel=".xlsx, .xls"
                  />
                  <div className="text-center text-xs text-zinc-600 font-mono">
                    - OR -
                  </div>
                  <button
                    onClick={useDummyData}
                    className="w-full py-2 px-4 text-sm font-medium text-zinc-300 bg-zinc-900/50 border border-zinc-800 hover:bg-zinc-800 hover:text-white transition-colors disabled:opacity-60"
                    disabled={dataLoading}
                  >
                    {dataLoading ? "Loading dataset..." : "Initialize Demo Data"}
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-between bg-zinc-900/50 border border-zinc-800 p-3 gap-3">
                  <div className="flex flex-col">
                    <span className="text-xs font-mono text-green-500">
                      ● DATA MOUNTED
                    </span>
                    <span className="text-sm text-white truncate max-w-[150px]">
                      {dataMode === "dummy"
                        ? "data.xlsx"
                        : trainingFile?.name}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={openDataFile}
                      className="text-xs text-zinc-300 hover:text-white border border-zinc-700 px-2 py-1"
                    >
                      VIEW
                    </button>
                    <button
                      onClick={() => {
                        setIsDataReady(false);
                        setDataMode("upload");
                        setTrainingFile(null);
                        setRecommendationText(null);
                        setRecommendationData(null);
                      }}
                      className="text-xs text-zinc-500 hover:text-white underline"
                    >
                      UNMOUNT
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div
            className={`border border-zinc-800 bg-zinc-900/20 backdrop-blur-sm transition-all ${
              !isDataReady ? "opacity-50 pointer-events-none" : ""
            }`}
          >
            <div className="px-4 py-3 bg-zinc-900/40 border-b border-zinc-800 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-zinc-400" />
              <span className="text-xs font-mono uppercase text-zinc-400">
                Patient Parameters
              </span>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-mono text-zinc-500 mb-1">
                    AGE
                  </label>
                  <input
                    type="number"
                    value={age}
                    onChange={(event) => setAge(event.target.value)}
                    className="w-full bg-black/50 border border-zinc-800 px-3 py-2 text-white text-sm focus:border-white outline-none placeholder:text-zinc-700"
                    placeholder="00"
                  />
                </div>
                <div>
                  <label className="block text-xs font-mono text-zinc-500 mb-1">
                    SEX
                  </label>
                  <select
                    value={gender}
                    onChange={(event) => setGender(event.target.value)}
                    className="w-full bg-black/50 border border-zinc-800 px-3 py-2 text-white text-sm focus:border-white outline-none appearance-none"
                  >
                    <option value="M">M</option>
                    <option value="F">F</option>
                    <option value="X">X</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono text-zinc-500 mb-1">
                  SYMPTOM KEYWORD
                </label>
                <input
                  type="text"
                  value={symptomInput}
                  onChange={(event) => setSymptomInput(event.target.value)}
                  placeholder="Query..."
                  className="w-full bg-black/50 border border-zinc-800 px-3 py-2 text-white text-sm focus:border-white outline-none placeholder:text-zinc-700"
                  list="symptoms-list"
                />
                <datalist id="symptoms-list">
                  {availableSymptoms.map((term) => (
                    <option key={term} value={term} />
                  ))}
                </datalist>
                {symptomInput && (
                  <div className="mt-2 border border-zinc-800 bg-zinc-950/80 text-xs text-zinc-400 p-2 space-y-1">
                    {filterMatches(symptomInput, availableSymptoms).map((item) => (
                      <button
                        key={item}
                        onClick={() => {
                          setSymptomList((prev) => [...new Set([...prev, item])]);
                          setSymptomInput("");
                        }}
                        className="block w-full text-left hover:text-white"
                        type="button"
                      >
                        {item}
                      </button>
                    ))}
                  </div>
                )}
                {multiAllowed.symptoms && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        const parts = symptomInput
                          .split(",")
                          .map((t) => t.trim())
                          .filter(Boolean);
                        if (parts.length) {
                          setSymptomList((prev) => [...new Set([...prev, ...parts])]);
                          setSymptomInput("");
                        }
                      }}
                      className="text-xs px-3 py-1 border border-zinc-700 text-zinc-300 hover:text-white hover:border-white"
                    >
                      Add symptom
                    </button>
                    {symptomList.map((item) => (
                      <span
                        key={item}
                        className="flex items-center gap-1 text-xs px-2 py-1 bg-zinc-800 border border-zinc-700 text-white"
                      >
                        {item}
                        <button
                          type="button"
                          onClick={() =>
                            setSymptomList((prev) => prev.filter((s) => s !== item))
                          }
                          className="text-zinc-400 hover:text-white"
                        >
                          ✕
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-xs font-mono text-zinc-500 mb-1">
                  PROBABLE REASON
                </label>
                <input
                  type="text"
                  value={causeInput}
                  onChange={(event) => setCauseInput(event.target.value)}
                  placeholder="Reason / cause"
                  className="w-full bg-black/50 border border-zinc-800 px-3 py-2 text-white text-sm focus:border-white outline-none placeholder:text-zinc-700"
                  list="cause-list"
                />
                <datalist id="cause-list">
                  {availableCauses.map((term) => (
                    <option key={term} value={term} />
                  ))}
                </datalist>
                {causeInput && (
                  <div className="mt-2 border border-zinc-800 bg-zinc-950/80 text-xs text-zinc-400 p-2 space-y-1">
                    {filterMatches(causeInput, availableCauses).map((item) => (
                      <button
                        key={item}
                        onClick={() => {
                          setCauseList((prev) => [...new Set([...prev, item])]);
                          setCauseInput("");
                        }}
                        className="block w-full text-left hover:text-white"
                        type="button"
                      >
                        {item}
                      </button>
                    ))}
                  </div>
                )}
                {multiAllowed.causes && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        const parts = causeInput
                          .split(",")
                          .map((t) => t.trim())
                          .filter(Boolean);
                        if (parts.length) {
                          setCauseList((prev) => [...new Set([...prev, ...parts])]);
                          setCauseInput("");
                        }
                      }}
                      className="text-xs px-3 py-1 border border-zinc-700 text-zinc-300 hover:text-white hover:border-white"
                    >
                      Add cause
                    </button>
                    {causeList.map((item) => (
                      <span
                        key={item}
                        className="flex items-center gap-1 text-xs px-2 py-1 bg-zinc-800 border border-zinc-700 text-white"
                      >
                        {item}
                        <button
                          type="button"
                          onClick={() =>
                            setCauseList((prev) => prev.filter((s) => s !== item))
                          }
                          className="text-zinc-400 hover:text-white"
                        >
                          ✕
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <button
                onClick={handleGetRecommendation}
                disabled={
                  !age ||
                  (!symptomList.length && !symptomInput) ||
                  (!causeList.length && !causeInput) ||
                  loading
                }
                className={`w-full mt-4 flex items-center justify-center gap-2 px-6 py-3 font-semibold text-sm transition-all border ${
                  !age ||
                  (!symptomList.length && !symptomInput) ||
                  (!causeList.length && !causeInput) ||
                  loading
                    ? "bg-zinc-900/50 text-zinc-600 border-zinc-800 cursor-not-allowed"
                    : "bg-white text-black border-white hover:bg-zinc-200"
                }`}
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
                QUERY
              </button>
            </div>
          </div>
        </div>

        <div className="lg:col-span-8 h-full min-h-[500px] border border-zinc-800 bg-black/60 backdrop-blur-md relative">
          <div className="absolute top-0 left-0 right-0 h-10 border-b border-zinc-800 bg-zinc-900/30 flex items-center px-4 justify-between">
            <span className="text-xs font-mono text-zinc-500">
              RESULT_BUFFER
            </span>
            {recommendationText && <span className="w-2 h-2 rounded-full bg-green-500"></span>}
          </div>

          <div className="p-8 pt-16 h-full overflow-auto font-mono text-sm text-zinc-300 space-y-6">
            {!recommendationText && !loading && (
              <div className="flex flex-col items-center justify-center h-full text-zinc-700 space-y-4">
                <Terminal className="w-12 h-12 opacity-20" />
                <p className="uppercase tracking-widest text-xs">
                  Awaiting Query Execution
                </p>
              </div>
            )}

            {loading && (
              <div className="space-y-2">
                <p className="text-zinc-500">{">"} Loading training dataset and models...</p>
                <p className="text-zinc-500">
                  {">"} Preparing request...
                </p>
                <p className="text-white animate-pulse">
                  {">"} Generating metrics...
                </p>
              </div>
            )}

            {recommendationData && (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="border border-emerald-800 bg-emerald-900/20 p-4">
                    <div className="text-xs text-emerald-300 mb-2 font-semibold">
                      ADVANCED DISEASE
                    </div>
                    {recommendationData.advanced_prediction?.error ? (
                      <p className="text-amber-300">
                        {recommendationData.advanced_prediction.error}
                      </p>
                    ) : (
                      <p className="text-white text-lg font-bold">
                        {recommendationData.advanced_prediction?.disease?.name || "N/A"}
                      </p>
                    )}
                  </div>
                  <div className="border border-blue-800 bg-blue-900/20 p-4">
                    <div className="text-xs text-blue-300 mb-2 font-semibold">
                      ADVANCED MEDICINE
                    </div>
                    {recommendationData.advanced_prediction?.error ? (
                      <p className="text-amber-300">
                        {recommendationData.advanced_prediction.error}
                      </p>
                    ) : (
                      <p className="text-white text-lg font-bold">
                        {recommendationData.advanced_prediction?.medicine?.name || "N/A"}
                      </p>
                    )}
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="border border-zinc-800 bg-zinc-900/40 p-4">
                    <div className="text-xs text-zinc-400 mb-2 uppercase tracking-wide">
                      Top Diseases (basic model)
                    </div>
                    {(recommendationData.basic_prediction?.diseases || []).length === 0 ? (
                      <p className="text-zinc-500 text-sm">No diseases returned.</p>
                    ) : (
                      <ul className="space-y-1">
                        {recommendationData.basic_prediction.diseases.map((d) => (
                          <li key={d.name} className="flex justify-between text-sm">
                            <span className="text-white">{d.name}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div className="border border-zinc-800 bg-zinc-900/40 p-4">
                    <div className="text-xs text-zinc-400 mb-2 uppercase tracking-wide">
                      Top Medicines (basic model)
                    </div>
                    {(recommendationData.basic_prediction?.medicines || []).length === 0 ? (
                      <p className="text-zinc-500 text-sm">No medicines returned.</p>
                    ) : (
                      <ul className="space-y-1">
                        {recommendationData.basic_prediction.medicines.map((m) => (
                          <li key={m.name} className="flex justify-between text-sm">
                            <span className="text-white">{m.name}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                <div className="border border-zinc-800 bg-zinc-900/50 p-4">
                  <div className="flex items-center justify-between text-xs uppercase text-zinc-400 mb-2">
                    <span>Model Metrics</span>
                    <span className="text-[10px] text-zinc-500">
                      Advanced + Basic predictors
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="text-white">
                      Disease Accuracy
                      <div className="text-zinc-300">
                        {recommendationData.model_metrics?.disease_accuracy?.toFixed
                          ? recommendationData.model_metrics.disease_accuracy.toFixed(1)
                          : recommendationData.model_metrics?.disease_accuracy || 0}
                        %
                      </div>
                    </div>
                    <div className="text-white">
                      Medicine Accuracy
                      <div className="text-zinc-300">
                        {recommendationData.model_metrics?.medicine_accuracy?.toFixed
                          ? recommendationData.model_metrics.medicine_accuracy.toFixed(1)
                          : recommendationData.model_metrics?.medicine_accuracy || 0}
                        %
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 text-xs text-zinc-500">
                    Accuracy is calculated from the training data you provided; real-world performance may vary. Always review with a licensed clinician.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default Recommendations;

