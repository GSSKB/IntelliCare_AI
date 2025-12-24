import { Button } from "@/components/ui/button";
import { Mail } from "lucide-react";

const Footer = () => {
  const footerLinks = {
    Product: ["Features", "Pricing", "Integrations", "FAQ"],
    Company: ["About Us", "Careers", "Press", "Contact"],
    Resources: ["Blog", "Documentation", "API", "Support"],
    Legal: ["Privacy Policy", "Terms of Service", "HIPAA Compliance", "Security"],
  };

  return (
    <footer className="bg-foreground text-background py-16">
      <div className="container mx-auto px-4">
        {/* Newsletter */}
        <div className="glass-card bg-primary/10 border-primary/20 rounded-2xl p-8 mb-16">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <h3 className="text-2xl font-bold text-background mb-2">
                Stay Updated with Healthcare Innovation
              </h3>
              <p className="text-background/70">
                Get the latest AI healthcare insights delivered to your inbox.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-4 py-3 bg-background/10 rounded-xl border border-background/20">
                <Mail className="w-5 h-5 text-background/70" />
                <input
                  type="email"
                  placeholder="Enter your email"
                  className="bg-transparent text-background placeholder:text-background/50 outline-none w-48"
                />
              </div>
              <Button className="bg-background text-foreground hover:bg-background/90">
                Subscribe
              </Button>
            </div>
          </div>
        </div>

        {/* Links Grid */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <a href="#" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-xl">I</span>
              </div>
              <span className="text-2xl font-bold text-background">IntelliCare AI</span>
            </a>
            <p className="text-background/60 text-sm leading-relaxed">
              Transforming healthcare with artificial intelligence for better outcomes.
            </p>
          </div>

          {/* Link Columns */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="font-semibold text-background mb-4">{category}</h4>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-background/60 hover:text-background transition-colors text-sm"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 pt-8 border-t border-background/10">
          <p className="text-background/50 text-sm">
            © 2024 IntelliCare AI. All rights reserved.
          </p>
          <div className="flex items-center gap-6">
            <a href="#" className="text-background/50 hover:text-background transition-colors text-sm">
              Privacy
            </a>
            <a href="#" className="text-background/50 hover:text-background transition-colors text-sm">
              Terms
            </a>
            <a href="#" className="text-background/50 hover:text-background transition-colors text-sm">
              Cookies
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
