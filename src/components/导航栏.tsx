import { Button } from "./ui/button";
import { Sparkles, Moon, Sun } from "lucide-react";
import { useTheme } from "./theme-provider";
import logoImage from "../assets/logo.png";

interface 导航栏Props {}

export function 导航栏({}: 导航栏Props) {
  const { theme, setTheme } = useTheme();

  const handleGetCourse = () => {
    window.open("https://appze9inzwc2314.h5.xiaoeknow.com/", "_blank");
  };
  
  return (
    <nav className="h-16 bg-background/95 backdrop-blur-lg border-b border-border flex items-center justify-between px-6 relative z-50">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-gray-700 to-gray-800 dark:from-gray-200 dark:to-gray-300 rounded-lg flex items-center justify-center shadow-lg overflow-hidden">
          <img src={logoImage} alt="Logo" className="w-full h-full object-cover rounded-lg" />
        </div>
        <div>
          <h1 className="text-lg font-medium text-foreground">
            赋范空间公开体验课
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Button
          variant="outline"
          size="icon"
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          className="w-9 h-9"
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        </Button>
        
        <Button 
          onClick={handleGetCourse}
          className="shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden group"
        >
          <span className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 -skew-x-12 transform -translate-x-full group-hover:translate-x-full transition-transform duration-700"></span>
          <Sparkles className="w-4 h-4 mr-2" />
          点击获取课程优惠
        </Button>
      </div>
    </nav>
  );
}
