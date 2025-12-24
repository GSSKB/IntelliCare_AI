import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const CTASection = () => {
  return (
    <section className="py-24 bg-background relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 rounded-full bg-primary/5 blur-3xl" />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground leading-tight">
            Ready to Experience the Future of{" "}
            <span className="gradient-text">Healthcare?</span>
          </h2>

          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Join thousands of patients and healthcare professionals who trust IntelliCare AI 
            for AI-powered medical solutions. Get started today.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/doctors">
              <Button variant="hero" size="xl" className="w-full sm:w-auto">
                Book Consultation
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
            <Link to="/risk">
              <Button variant="heroOutline" size="xl" className="w-full sm:w-auto">
                Check Risk Assessment
              </Button>
            </Link>
          </div>

          <p className="text-sm text-muted-foreground">
            No credit card required • HIPAA compliant • 24/7 support
          </p>
        </div>
      </div>
    </section>
  );
};

export default CTASection;
