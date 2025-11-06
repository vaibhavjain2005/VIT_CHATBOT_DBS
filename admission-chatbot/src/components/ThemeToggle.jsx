import { Switch } from "@heroui/react";
import { MoonIcon, SunIcon } from "@heroicons/react/24/solid";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(
    () => localStorage.getItem("theme") === "dark"
  );

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      root.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDark]);

  return (
    <div className="absolute top-4 right-4">
        
      <Switch
        size="lg"
        color="primary"
        isSelected={isDark}
        onValueChange={setIsDark}
        startContent={<SunIcon className="w-4 h-4 text-yellow-400" />}
        endContent={<MoonIcon className="w-4 h-4 text-indigo-400" />}
        aria-label="Toggle dark mode"
        />
    </div>
  );
}
