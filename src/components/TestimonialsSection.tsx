import { Star } from "lucide-react";

const testimonials = [
  {
    quote: "IntelliCare AI's diagnostics helped detect my condition early. The accuracy and speed of their analysis is remarkable.",
    author: "Jennifer M.",
    role: "Patient",
    rating: 5,
  },
  {
    quote: "As a physician, the AI-assisted tools have enhanced my practice significantly. Highly recommend to colleagues.",
    author: "Dr. Robert K.",
    role: "Cardiologist",
    rating: 5,
  },
  {
    quote: "The platform made connecting with specialists effortless. Got my diagnosis and treatment plan within 48 hours.",
    author: "David L.",
    role: "Patient",
    rating: 5,
  },
];

const TestimonialsSection = () => {
  return (
    <section className="py-24 bg-secondary/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16 space-y-4">
          <p className="text-primary font-medium">Testimonials</p>
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">
            Trusted by Thousands
          </h2>
          <p className="text-muted-foreground max-w-lg mx-auto">
            Hear from patients and healthcare professionals who've experienced the IntelliCare AI difference.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="glass-card rounded-2xl p-8 hover-lift"
            >
              <div className="flex items-center gap-1 mb-6">
                {Array.from({ length: testimonial.rating }).map((_, i) => (
                  <Star key={i} className="w-5 h-5 text-amber-400 fill-amber-400" />
                ))}
              </div>

              <blockquote className="text-foreground text-lg leading-relaxed mb-6">
                "{testimonial.quote}"
              </blockquote>

              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-accent flex items-center justify-center">
                  <span className="text-lg">👤</span>
                </div>
                <div>
                  <p className="font-semibold text-foreground">{testimonial.author}</p>
                  <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;
