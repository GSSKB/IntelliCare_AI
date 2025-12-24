import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import heroDoctor from "@/assets/hero-doctor.jpg";

const HeroSection = () => {
  return (
    <section className="relative min-h-screen hero-gradient overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute top-1/2 -left-20 w-72 h-72 rounded-full bg-primary/10 blur-3xl" />
      </div>

      <div className="container relative z-10 mx-auto px-4 pt-32 pb-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-8 animate-fade-up">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/60 border border-primary/20">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-sm font-medium text-accent-foreground">AI-Powered Healthcare Platform</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight tracking-tight">
              Health with{" "}
              <span className="gradient-text">Intelligence</span>
            </h1>

            <p className="text-lg text-muted-foreground max-w-lg leading-relaxed">
              Experience the future of healthcare with AI-driven diagnostics, personalized treatment plans, 
              and instant access to world-class medical experts.
            </p>

            {/* Search Bar */}
            <div className="relative max-w-xl animate-fade-up-delay-1">
              <div className="flex items-center gap-3 p-2 pl-6 bg-card rounded-2xl border border-border shadow-card">
                <Search className="w-5 h-5 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search for doctors, treatments, or conditions..."
                  className="flex-1 bg-transparent text-foreground placeholder:text-muted-foreground outline-none text-base"
                />
                <Button variant="hero" size="lg">
                  Search
                </Button>
              </div>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-8 pt-4 animate-fade-up-delay-2">
              <div>
                <p className="text-3xl font-bold text-foreground">500+</p>
                <p className="text-sm text-muted-foreground">Expert Doctors</p>
              </div>
              <div className="w-px h-12 bg-border" />
              <div>
                <p className="text-3xl font-bold text-foreground">50k+</p>
                <p className="text-sm text-muted-foreground">Patients Treated</p>
              </div>
              <div className="w-px h-12 bg-border" />
              <div>
                <p className="text-3xl font-bold text-foreground">99%</p>
                <p className="text-sm text-muted-foreground">Satisfaction Rate</p>
              </div>
            </div>
          </div>

          {/* Right Content - Hero Image */}
          <div className="relative animate-fade-up-delay-1">
            <div className="relative z-10">
              <div className="relative rounded-3xl overflow-hidden shadow-card">
                <img
                  src={heroDoctor}
                  alt="Doctor using advanced VR technology for medical diagnostics"
                  className="w-full h-auto object-cover"
                />
                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-background/20 to-transparent" />
              </div>

              {/* Floating card */}
              <div className="absolute -bottom-6 -left-6 glass-card rounded-2xl p-4 animate-float">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-primary text-xl">🧠</span>
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">AI Analysis</p>
                    <p className="text-sm text-muted-foreground">Real-time diagnostics</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Background glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full rounded-full bg-primary/10 blur-3xl -z-10" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
