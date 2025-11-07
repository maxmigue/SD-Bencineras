import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef(({ className, type, ...props }, ref) => {
  return (
    <input
      type={type}
      className={cn(
        // 🔸 Cambiado el color de focus y border a naranjo (#F26E22)
        "flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 " +
        "focus:outline-none focus:ring-2 focus:ring-[#F26E22] focus:ring-offset-1 focus:border-[#F26E22] " +
        "disabled:opacity-50 disabled:cursor-not-allowed transition-colors",
        className
      )}
      ref={ref}
      {...props}
    />
  );
});
Input.displayName = "Input";
