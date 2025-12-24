import { Button } from "@/components/ui/button";
import dnaHelix from "@/assets/dna-helix.jpg";
import aiBrain from "@/assets/ai-brain.jpg";

const AboutSection = () => {
  return (
    <section className="py-24 bg-secondary/30 relative overflow-hidden">
      <div className="container mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left - Images Grid */}
          <div className="relative">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div className="rounded-3xl overflow-hidden shadow-card animate-fade-up">
                  <img
                    src={dnaHelix}
                    alt="DNA helix representing genetic analysis"
                    className="w-full h-64 object-cover"
                  />
                </div>
                <div className="rounded-3xl overflow-hidden shadow-card animate-fade-up-delay-1 h-48 bg-accent flex items-center justify-center">
                  <div className="text-center p-6">
                    <p className="text-4xl font-bold text-primary">15+</p>
                    <p className="text-sm text-muted-foreground mt-1">Years of Innovation</p>
                  </div>
                </div>
              </div>
              <div className="space-y-4 pt-8">
                <div className="rounded-3xl overflow-hidden shadow-card animate-fade-up-delay-2 h-48 bg-primary flex items-center justify-center">
                  <div className="text-center p-6">
                    <p className="text-4xl font-bold text-primary-foreground">24/7</p>
                    <p className="text-sm text-primary-foreground/80 mt-1">AI Support Available</p>
                  </div>
                </div>
                <div className="rounded-3xl overflow-hidden shadow-card animate-fade-up-delay-3">
                  <img
                    src={aiBrain}
                    alt="AI brain neural network visualization"
                    className="w-full h-64 object-cover"
                  />
                </div>
              </div>
            </div>

            {/* Decorative element */}
            <div className="absolute -bottom-10 -left-10 w-40 h-40 rounded-full bg-primary/10 blur-3xl" />
          </div>

          {/* Right - Content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <p className="text-primary font-medium">About IntelliCare AI</p>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground leading-tight">
                Healthcare with{" "}
                <span className="gradient-text">AI Precision</span>
              </h2>
            </div>

            <p className="text-lg text-muted-foreground leading-relaxed">
              We're revolutionizing healthcare by combining cutting-edge artificial intelligence 
              with world-class medical expertise. Our platform enables faster, more accurate 
              diagnoses and personalized treatment plans.
            </p>

            <ul className="space-y-4">
              {[
                "AI-powered diagnostic accuracy exceeding 98%",
                "Instant access to verified medical specialists",
                "Personalized treatment recommendations",
                "Secure, HIPAA-compliant data protection",
              ].map((item, index) => (
                <li key={index} className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <span className="text-primary text-sm">✓</span>
                  </span>
                  <span className="text-foreground">{item}</span>
                </li>
              ))}
            </ul>

            <div className="flex flex-wrap gap-4 pt-4">
              <Button variant="hero" size="lg">
                Get Started
              </Button>
              <Button variant="heroOutline" size="lg">
                Learn More
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;
