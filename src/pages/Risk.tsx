import { useState, useEffect, useRef } from "react";
import { predictRisk, sendMessage } from "../api/api";
import { RotateCcw, Home, Search, Heart, Brain } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

interface Symptoms {
  fever: boolean;
  cough: boolean;
  fatigue: boolean;
  headache: boolean;
  nausea: boolean;
  chestPain: boolean;
  breathingDifficulty: boolean;
  jointPain: boolean;
}

interface PatientInfo {
  age: string;
  gender: string;
  bloodPressure: string;
  cholesterolLevel: string;
}

export default function Risk() {
  const [risk, setRisk] = useState("");
  const [symptomInfo, setSymptomInfo] = useState<{ [key: string]: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const riskResultRef = useRef<HTMLDivElement>(null);

  const scrollToRiskResult = () => {
    riskResultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  useEffect(() => {
    if (risk) {
      scrollToRiskResult();
    }
  }, [risk]);
  const [symptoms, setSymptoms] = useState<Symptoms>({
    fever: false,
    cough: false,
    fatigue: false,
    headache: false,
    nausea: false,
    chestPain: false,
    breathingDifficulty: false,
    jointPain: false
  });

  const [patientInfo, setPatientInfo] = useState<PatientInfo>({
    age: "",
    gender: "",
    bloodPressure: "",
    cholesterolLevel: ""
  });

  const handleSymptomChange = (symptom: keyof Symptoms) => {
    setSymptoms(prev => ({
      ...prev,
      [symptom]: !prev[symptom]
    }));
  };

  const handleClearAll = () => {
    setSymptoms({
      fever: false,
      cough: false,
      fatigue: false,
      headache: false,
      nausea: false,
      chestPain: false,
      breathingDifficulty: false,
      jointPain: false
    });
    setPatientInfo({
      age: "",
      gender: "",
      bloodPressure: "",
      cholesterolLevel: ""
    });
    setRisk("");
    setSymptomInfo({});
  };

  const handlePatientInfoChange = (field: keyof PatientInfo, value: string) => {
    setPatientInfo(prev => ({
      ...prev,
      [field]: value
    }));
  };

  async function predict() {
    setIsLoading(true);
    try {
      // Get ChatGPT information for all selected symptoms
      const selectedSymptoms = Object.entries(symptoms)
        .filter(([_, isSelected]) => isSelected)
        .map(([symptom]) => symptom);

      if (selectedSymptoms.length === 0) {
        setRisk("Please select at least one symptom to assess risk");
        setIsLoading(false);
        return;
      }

      // Get information for each selected symptom using ChatGPT
      const symptomPromises = selectedSymptoms.map(async (symptom) => {
        try {
          const symptomName = symptom.replace(/([A-Z])/g, ' $1').trim();
          const prompt = `Tell me about ${symptomName} - what causes it, common symptoms, when to see a doctor, basic home remedies, and potential complications. Keep it informative but concise.`;
          const response = await sendMessage(prompt);
          return { symptom, info: response.data.response };
        } catch (error) {
          const fallbackInfo = getFallbackInfo(symptom);
          return { symptom, info: fallbackInfo };
        }
      });

      const symptomResponses = await Promise.all(symptomPromises);
      const newSymptomInfo: { [key: string]: string } = {};
      symptomResponses.forEach(({ symptom, info }) => {
        newSymptomInfo[symptom] = info;
      });
      setSymptomInfo(newSymptomInfo);

      // Build patient information text
      const patientInfoText = [];
      if (patientInfo.age) patientInfoText.push(`Age: ${patientInfo.age}`);
      if (patientInfo.gender) patientInfoText.push(`Gender: ${patientInfo.gender}`);
      if (patientInfo.bloodPressure) patientInfoText.push(`Blood Pressure: ${patientInfo.bloodPressure}`);
      if (patientInfo.cholesterolLevel) patientInfoText.push(`Cholesterol Level: ${patientInfo.cholesterolLevel}`);
      
      const patientInfoString = patientInfoText.length > 0 
        ? `\nPatient Information: ${patientInfoText.join(', ')}` 
        : '';

      // Use ChatGPT for real-time risk assessment
      const symptomsText = selectedSymptoms.map(s => s.replace(/([A-Z])/g, ' $1').trim()).join(', ');
      const riskPrompt = `Analyze these symptoms: ${symptomsText}${patientInfoString}

Provide ONLY a risk assessment response starting with one of these exact formats:
HIGH RISK - [brief explanation]
MEDIUM RISK - [brief explanation]  
LOW RISK - [brief explanation]

Do not include this prompt in your response. Just provide the assessment.`;

      try {
        const riskResponse = await sendMessage(riskPrompt);
        setRisk(riskResponse.data.response);
      } catch (error) {
        // Fallback risk assessment based on symptom count and severity
        const highRiskSymptoms = ['chestPain', 'breathingDifficulty'];
        const mediumRiskSymptoms = ['fever', 'nausea'];
        
        if (selectedSymptoms.some(s => highRiskSymptoms.includes(s))) {
          setRisk("HIGH RISK - Some symptoms require immediate medical attention. Please consult a healthcare provider promptly.");
        } else if (selectedSymptoms.some(s => mediumRiskSymptoms.includes(s)) || selectedSymptoms.length >= 3) {
          setRisk("MEDIUM RISK - Multiple symptoms detected. Monitor closely and consider medical consultation if symptoms persist or worsen.");
        } else {
          setRisk("LOW RISK - Mild symptoms detected. Monitor your condition and seek medical attention if symptoms worsen or persist for more than a few days.");
        }
      }
    } catch (error) {
      setRisk("Error: Unable to assess risk at this time");
    } finally {
      setIsLoading(false);
    }
  }

  function getFallbackInfo(symptom: string): string {
    const fallbacks: { [key: string]: string } = {
      fever: "Fever is a common symptom indicating your body is fighting infection. Monitor temperature and seek medical attention if exceeds 103°F or lasts more than 3 days.",
      cough: "Cough is your body's way of clearing airways. Most coughs resolve within 2-3 weeks. Seek medical care for persistent coughs or breathing difficulties.",
      fatigue: "Fatigue can result from many factors including lack of sleep, stress, or medical conditions. Consult a doctor if persistent despite adequate rest.",
      headache: "Most headaches are not serious but can indicate underlying conditions. Seek immediate care for sudden severe headaches or those with fever/stiff neck.",
      nausea: "Nausea has many causes from mild to serious. Stay hydrated and seek medical attention if accompanied by severe symptoms or persists.",
      chestPain: "Chest pain can be a medical emergency. Seek immediate medical attention, especially if accompanied by shortness of breath, sweating, or jaw pain.",
      breathingDifficulty: "Difficulty breathing requires immediate medical attention. Call emergency services if breathing becomes severely restricted.",
      jointPain: "Joint pain can result from injury, overuse, or medical conditions. Rest and gentle movement may help, but seek care for severe or persistent pain."
    };
    return fallbacks[symptom] || "Information about this symptom is not available. Please consult a healthcare professional.";
  }

  const getRiskLevel = (riskValue: string) => {
    if (riskValue.toLowerCase().includes('low')) return { color: 'green', level: 'Low Risk' };
    if (riskValue.toLowerCase().includes('medium')) return { color: 'yellow', level: 'Medium Risk' };
    if (riskValue.toLowerCase().includes('high')) return { color: 'red', level: 'High Risk' };
    return { color: 'gray', level: 'Unknown' };
  };

  const riskInfo = getRiskLevel(risk);

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="bg-card rounded-2xl shadow-sm border overflow-hidden">
          {/* Risk Header */}
          <div className="bg-gradient-to-r from-purple-500 to-pink-600 text-primary-foreground p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="relative w-12 h-12 bg-primary-foreground/20 rounded-xl flex items-center justify-center shadow-lg">
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-primary-foreground/30 to-transparent" />
                  <div className="relative flex items-center justify-center">
                    <Heart className="w-6 h-6 text-primary-foreground fill-primary-foreground" />
                    <Brain className="w-4 h-4 text-primary-foreground absolute -top-0.5 -right-0.5" />
                  </div>
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Disease Risk Assessment</h2>
                  <p className="text-purple-100 text-sm">Powered by IntelliCare AI</p>
                </div>
              </div>
              
              {/* Home Button */}
              <button
                onClick={() => navigate('/')}
                className="flex items-center space-x-2 px-4 py-2 bg-primary-foreground/20 hover:bg-primary-foreground/30 rounded-lg transition-colors duration-200"
              >
                <Home className="w-4 h-4" />
                <span className="text-sm font-medium">Home</span>
              </button>
            </div>
          </div>

          {/* Risk Content */}
          <div className="h-[700px] overflow-y-auto bg-secondary/30 p-6">
            <div className="max-w-2xl mx-auto">
              {/* Symptoms Selection */}
              <div className="bg-card rounded-xl shadow-md p-6 mb-6 border">
                <h3 className="text-lg font-semibold text-foreground mb-4">Select Your Symptoms</h3>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(symptoms).map(([symptom, checked]) => (
                    <label key={symptom} className="flex items-center space-x-3 p-3 border border-border rounded-lg hover:bg-secondary/50 cursor-pointer transition-colors">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => handleSymptomChange(symptom as keyof Symptoms)}
                        className="w-4 h-4 text-purple-600 border-border rounded focus:ring-purple-500"
                      />
                      <span className="text-foreground capitalize">
                        {symptom.replace(/([A-Z])/g, ' $1').trim()}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Patient Information */}
              <div className="bg-card rounded-xl shadow-md p-6 mb-6 border">
                <h3 className="text-lg font-semibold text-foreground mb-4">Patient Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Age */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Age
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="120"
                      value={patientInfo.age}
                      onChange={(e) => handlePatientInfoChange('age', e.target.value)}
                      placeholder="Enter your age"
                      className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-background text-foreground"
                    />
                  </div>

                  {/* Gender */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Gender
                    </label>
                    <select
                      value={patientInfo.gender}
                      onChange={(e) => handlePatientInfoChange('gender', e.target.value)}
                      className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-background text-foreground"
                    >
                      <option value="">Select Gender</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  {/* Blood Pressure */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Blood Pressure
                    </label>
                    <select
                      value={patientInfo.bloodPressure}
                      onChange={(e) => handlePatientInfoChange('bloodPressure', e.target.value)}
                      className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-background text-foreground"
                    >
                      <option value="">Select Blood Pressure</option>
                      <option value="Low">Low</option>
                      <option value="Normal">Normal</option>
                      <option value="High">High</option>
                    </select>
                  </div>

                  {/* Cholesterol Level */}
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Cholesterol Level
                    </label>
                    <select
                      value={patientInfo.cholesterolLevel}
                      onChange={(e) => handlePatientInfoChange('cholesterolLevel', e.target.value)}
                      className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-background text-foreground"
                    >
                      <option value="">Select Cholesterol Level</option>
                      <option value="Low">Low</option>
                      <option value="Normal">Normal</option>
                      <option value="High">High</option>
                    </select>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-3">
                  * This information helps provide a more accurate risk assessment based on similar cases in our database.
                </p>
              </div>

              {/* Predict and Clear Buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
                <button
                  onClick={predict}
                  disabled={isLoading || Object.values(symptoms).every(v => !v)}
                  className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-primary-foreground rounded-lg font-medium hover:from-purple-600 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                >
                  <div className="flex items-center space-x-2">
                    {isLoading ? (
                      <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    )}
                    <span>{isLoading ? "Analyzing..." : "Assess Risk"}</span>
                  </div>
                </button>
                
                <button
                  onClick={handleClearAll}
                  disabled={isLoading || Object.values(symptoms).every(v => !v)}
                  className="px-8 py-3 bg-gradient-to-r from-gray-500 to-gray-600 text-primary-foreground rounded-lg font-medium hover:from-gray-600 hover:to-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                >
                  <div className="flex items-center space-x-2">
                    <RotateCcw className="w-4 h-4" />
                    <span>Clear All</span>
                  </div>
                </button>
              </div>

              {/* Risk Result */}
              {risk && (
                <div ref={riskResultRef} className="bg-card rounded-xl shadow-md overflow-hidden border">
                  <div className={`p-6 ${riskInfo.color === 'green' ? 'bg-green-50 border-l-4 border-green-500' : riskInfo.color === 'yellow' ? 'bg-yellow-50 border-l-4 border-yellow-500' : riskInfo.color === 'red' ? 'bg-red-50 border-l-4 border-red-500' : 'bg-gray-50 border-l-4 border-gray-500'}`}>
                    <div>
                      <h3 className="text-lg font-semibold text-foreground mb-2">Risk Assessment Result</h3>
                      <p className={`text-2xl font-bold mb-4 ${riskInfo.color === 'green' ? 'text-green-600' : riskInfo.color === 'yellow' ? 'text-yellow-600' : riskInfo.color === 'red' ? 'text-red-600' : 'text-gray-600'}`}>{riskInfo.level}</p>
                      <div className="text-foreground whitespace-pre-line">
                        {risk.split('\n').map((line, index) => {
                          // Format bullet points
                          if (line.trim().startsWith('•')) {
                            return (
                              <p key={index} className="ml-4 mb-1 text-sm">
                                {line}
                              </p>
                            );
                          }
                          // Format section headers (Similar Cases, Disclaimer)
                          else if (line.trim() && !line.trim().startsWith('•') && line.trim() !== line.trim().toLowerCase() && !line.includes('—')) {
                            return (
                              <p key={index} className="font-semibold mt-4 mb-2 text-base">
                                {line.trim()}
                              </p>
                            );
                          }
                          // Format numbered or regular lines
                          else if (line.trim()) {
                            return (
                              <p key={index} className="mb-1 text-sm">
                                {line}
                              </p>
                            );
                          }
                          return null;
                        })}
                      </div>
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
}
