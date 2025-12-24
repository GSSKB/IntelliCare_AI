import { Star } from "lucide-react";
import { Button } from "@/components/ui/button";

const doctors = [
  {
    name: "Dr. Sarah Chen",
    specialty: "Neurologist",
    rating: 4.9,
    reviews: 127,
    available: true,
  },
  {
    name: "Dr. Michael Roberts",
    specialty: "Cardiologist",
    rating: 4.8,
    reviews: 203,
    available: true,
  },
  {
    name: "Dr. Emily Watson",
    specialty: "Oncologist",
    rating: 4.9,
    reviews: 156,
    available: false,
  },
];

const DoctorsSection = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-12">
          <div className="space-y-4">
            <p className="text-primary font-medium">Expert Network</p>
            <h2 className="text-3xl md:text-4xl font-bold text-foreground">
              Meet Our Verified Specialists
            </h2>
            <p className="text-muted-foreground max-w-lg">
              Connect with board-certified physicians using AI-enhanced diagnostic tools.
            </p>
          </div>
          <Button variant="heroOutline" size="lg">
            View All Doctors
          </Button>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {doctors.map((doctor, index) => (
            <div
              key={doctor.name}
              className="glass-card rounded-2xl p-6 hover-lift group"
            >
              {/* Avatar placeholder */}
              <div className="w-20 h-20 rounded-2xl bg-accent mb-4 flex items-center justify-center">
                <span className="text-3xl">👨‍⚕️</span>
              </div>

              <div className="flex items-center gap-2 mb-2">
                {doctor.available ? (
                  <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                    Available Now
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-muted text-muted-foreground text-xs font-medium">
                    Next Available: Tomorrow
                  </span>
                )}
              </div>

              <h3 className="text-xl font-semibold text-foreground mb-1">
                {doctor.name}
              </h3>
              <p className="text-muted-foreground mb-4">{doctor.specialty}</p>

              <div className="flex items-center gap-2 mb-6">
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                  <span className="font-medium text-foreground">{doctor.rating}</span>
                </div>
                <span className="text-muted-foreground text-sm">({doctor.reviews} reviews)</span>
              </div>

              <Button variant="hero" className="w-full">
                Book Consultation
              </Button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default DoctorsSection;
