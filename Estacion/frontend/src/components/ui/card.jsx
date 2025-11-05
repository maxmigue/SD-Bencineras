export const Card = ({ className, children }) => (
    <div className={`rounded-xl border bg-white ${className}`}>{children}</div>
  );
  
  export const CardHeader = ({ children }) => (
    <div className="p-4 border-b">{children}</div>
  );
  
  export const CardTitle = ({ children }) => (
    <h3 className="text-lg font-semibold text-gray-800">{children}</h3>
  );
  
  export const CardContent = ({ children }) => (
    <div className="p-4">{children}</div>
  );
  