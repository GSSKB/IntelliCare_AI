import axios from "axios";

// Get API URL from environment variable or use default
const API_URL = import.meta.env.VITE_API_URL || "";

export async function sendMessage(message: string) {
  console.log("API: Sending message to backend:", message);
  try {
    const apiEndpoint = API_URL ? `${API_URL}/chat` : "/api/chat";
    const response = await fetch(apiEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data };
  } catch (error) {
    console.error("Fetch error:", error);
    throw error;
  }
}

export function predictRisk(symptomsVector: number[]) {
  const apiEndpoint = API_URL ? `${API_URL}/predict` : "/api/predict";
  return axios.post(apiEndpoint, { symptoms_vector: symptomsVector }, {
    headers: {
      'Content-Type': 'application/json',
    }
  });
}
