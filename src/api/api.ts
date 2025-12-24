import axios from "axios";

export async function sendMessage(message: string) {
  console.log("API: Sending message to backend:", message);
  try {
    const response = await fetch("/api/chat", {
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
  return axios.post("/api/predict", { symptoms_vector: symptomsVector }, {
    headers: {
      'Content-Type': 'application/json',
    }
  });
}
