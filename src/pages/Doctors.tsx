import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Home, Calendar, Star, MapPin, Clock, Phone, Mail } from "lucide-react";

interface Doctor {
  id: number;
  name: string;
  specialty: string;
  rating: number;
  experience: string;
  location: string;
  availability: string;
  phone: string;
  email: string;
  image: string;
  consultationFee: string;
}

const doctorsData: Doctor[] = [
  {
    id: 1,
    name: "Dr. Sarah Johnson",
    specialty: "General Medicine",
    rating: 4.8,
    experience: "15 years",
    location: "New York, NY",
    availability: "Mon-Fri, 9AM-5PM",
    phone: "+1 (555) 123-4567",
    email: "dr.johnson@intellicare.com",
    image: "/api/placeholder/200/200",
    consultationFee: "$150"
  },
  {
    id: 2,
    name: "Dr. Michael Chen",
    specialty: "Cardiology",
    rating: 4.9,
    experience: "12 years",
    location: "Los Angeles, CA",
    availability: "Tue-Thu, 10AM-6PM",
    phone: "+1 (555) 234-5678",
    email: "dr.chen@intellicare.com",
    image: "/api/placeholder/200/200",
    consultationFee: "$200"
  },
  {
    id: 3,
    name: "Dr. Emily Rodriguez",
    specialty: "Pediatrics",
    rating: 4.7,
    experience: "10 years",
    location: "Houston, TX",
    availability: "Mon-Wed, 8AM-4PM",
    phone: "+1 (555) 345-6789",
    email: "dr.rodriguez@intellicare.com",
    image: "/api/placeholder/200/200",
    consultationFee: "$120"
  },
  {
    id: 4,
    name: "Dr. James Wilson",
    specialty: "Orthopedics",
    rating: 4.6,
    experience: "18 years",
    location: "Chicago, IL",
    availability: "Fri-Sat, 9AM-3PM",
    phone: "+1 (555) 456-7890",
    email: "dr.wilson@intellicare.com",
    image: "/api/placeholder/200/200",
    consultationFee: "$175"
  },
  {
    id: 5,
    name: "Dr. Lisa Anderson",
    specialty: "Dermatology",
    rating: 4.9,
    experience: "8 years",
    location: "Miami, FL",
    availability: "Mon-Thu, 10AM-5PM",
    phone: "+1 (555) 567-8901",
    email: "dr.anderson@intellicare.com",
    image: "/api/placeholder/200/200",
    consultationFee: "$140"
  },
  {
    id: 6,
    name: "Dr. Robert Taylor",
    specialty: "Neurology",
    rating: 4.8,
    experience: "14 years",
    location: "Boston, MA",
    availability: "Wed-Fri, 11AM-6PM",
    phone: "+1 (555) 678-9012",
    email: "dr.taylor@intellicare.com",
    image: "/api/placeholder/200/200",
    consultationFee: "$225"
  }
];

export default function Doctors() {
  const navigate = useNavigate();
  const [selectedSpecialty, setSelectedSpecialty] = useState("all");

  const specialties = ["all", "General Medicine", "Cardiology", "Pediatrics", "Orthopedics", "Dermatology", "Neurology"];

  const filteredDoctors = selectedSpecialty === "all" 
    ? doctorsData 
    : doctorsData.filter(doctor => doctor.specialty === selectedSpecialty);

  const handleBookAppointment = (doctor: Doctor) => {
    // For now, navigate to chat page with doctor info
    // In a real app, this would open a booking modal or booking page
    navigate('/chat');
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-card rounded-2xl shadow-sm border overflow-hidden mb-8">
          <div className="bg-gradient-to-r from-blue-500 to-cyan-600 text-primary-foreground p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-primary-foreground/20 rounded-full flex items-center justify-center">
                  <div className="w-6 h-6 bg-primary-foreground rounded-full"></div>
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Available Doctors</h2>
                  <p className="text-blue-100 text-sm">Book a consultation with our expert physicians</p>
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
        </div>

        {/* Specialty Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            {specialties.map((specialty) => (
              <button
                key={specialty}
                onClick={() => setSelectedSpecialty(specialty)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                  selectedSpecialty === specialty
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                }`}
              >
                {specialty === "all" ? "All Specialties" : specialty}
              </button>
            ))}
          </div>
        </div>

        {/* Doctors Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDoctors.map((doctor) => (
            <div key={doctor.id} className="bg-card rounded-xl shadow-md border overflow-hidden hover:shadow-lg transition-shadow duration-200">
              {/* Doctor Image and Basic Info */}
              <div className="p-6 border-b border-border">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-primary to-primary/60 rounded-full flex items-center justify-center">
                    <span className="text-primary-foreground font-bold text-xl">
                      {doctor.name.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-foreground">{doctor.name}</h3>
                    <p className="text-sm text-muted-foreground">{doctor.specialty}</p>
                    <div className="flex items-center space-x-1 mt-1">
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      <span className="text-sm font-medium">{doctor.rating}</span>
                      <span className="text-sm text-muted-foreground">({doctor.experience})</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Doctor Details */}
              <div className="p-6 space-y-3">
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm">{doctor.location}</span>
                </div>
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm">{doctor.availability}</span>
                </div>
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Phone className="w-4 h-4" />
                  <span className="text-sm">{doctor.phone}</span>
                </div>
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Mail className="w-4 h-4" />
                  <span className="text-sm">{doctor.email}</span>
                </div>
                
                {/* Consultation Fee */}
                <div className="pt-3 border-t border-border">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Consultation Fee:</span>
                    <span className="text-lg font-semibold text-primary">{doctor.consultationFee}</span>
                  </div>
                </div>
              </div>

              {/* Book Appointment Button */}
              <div className="p-6 pt-0">
                <Button 
                  onClick={() => handleBookAppointment(doctor)}
                  className="w-full"
                  variant="hero"
                >
                  <Calendar className="w-4 h-4 mr-2" />
                  Book Consultation
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* No Results Message */}
        {filteredDoctors.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
              <div className="w-8 h-8 bg-muted-foreground/30 rounded-full"></div>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">No doctors found</h3>
            <p className="text-muted-foreground">Try selecting a different specialty</p>
          </div>
        )}
      </div>
    </div>
  );
}
