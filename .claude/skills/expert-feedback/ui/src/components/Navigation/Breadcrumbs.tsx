import React from 'react'

interface BreadcrumbsProps {
  items: string[]
}

export function Breadcrumbs({ items }: BreadcrumbsProps) {
  return (
    <div className="breadcrumbs">
      {items.map((item, i) => (
        <React.Fragment key={i}>
          {i > 0 && <span className="breadcrumb-separator"> / </span>}
          <span className="breadcrumb-item">{item}</span>
        </React.Fragment>
      ))}
    </div>
  )
}
