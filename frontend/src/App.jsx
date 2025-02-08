import "./App.css";
import MedicalReports from "./components/MedicalReports";
import MedicalRecommendation from './components/MedicalRecommendation';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">AI Chat Interface</h1>
        <MedicalReports />
        <MedicalRecommendation />
      </div>
    </div>
  );
}

export default App;