import { Brain, Eye, Stethoscope } from "lucide-react";

const features = [
  {
    icon: Eye,
    title: "AI-Driven Image Analysis",
    description: "Advanced imaging diagnostics powered by deep learning algorithms for precise detection.",
  },
  {
    icon: Stethoscope,
    title: "Smart Surgical Planning",
    description: "AI-assisted pre-operative planning with 3D visualization and risk assessment.",
  },
  {
    icon: Brain,
    title: "Brain Health Monitoring",
    description: "Continuous cognitive health tracking with early warning indicators.",
  },
];

const FeatureCards = () => {
  return (
    <section className="py-20 bg-background relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-0 left-1/4 w-64 h-64 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-64 h-64 rounded-full bg-primary/5 blur-3xl" />
      </div>

      <div className="container relative z-10 mx-auto px-4">
        <div className="text-center mb-16">
          <p className="text-primary font-medium mb-3">Our Capabilities</p>
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">
            Powered by Cutting-Edge AI
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className={`group glass-card rounded-2xl p-8 hover-lift cursor-pointer animate-fade-up`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="w-14 h-14 rounded-2xl bg-accent flex items-center justify-center mb-6 group-hover:bg-primary transition-colors duration-300">
                <feature.icon className="w-7 h-7 text-accent-foreground group-hover:text-primary-foreground transition-colors duration-300" />
              </div>

              <h3 className="text-xl font-semibold text-foreground mb-3">
                {feature.title}
              </h3>

              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>

              <div className="mt-6 flex items-center gap-2 text-primary font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <span>Learn more</span>
                <span className="group-hover:translate-x-1 transition-transform duration-300">→</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeatureCards;
