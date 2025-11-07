import * as React from "react"

export function Table({ children, className }) {
  return (
    <div className={`relative w-full overflow-auto ${className}`}>
      <table className="w-full caption-bottom text-sm">{children}</table>
    </div>
  )
}

export function TableHeader({ children }) {
  return <thead className="[&_tr]:border-b">{children}</thead>
}

export function TableBody({ children }) {
  return <tbody className="[&_tr:last-child]:border-0">{children}</tbody>
}

export function TableRow({ children }) {
  return (
    <tr className="border-b transition-colors hover:bg-gray-50">
      {children}
    </tr>
  )
}

export function TableHead({ children }) {
  return (
    <th className="h-10 px-2 text-left align-middle font-semibold text-gray-600">
      {children}
    </th>
  )
}

export function TableCell({ children }) {
  return (
    <td className="p-2 align-middle text-gray-700">{children}</td>
  )
}
