import React from 'react'

interface CardProps {
  title: string
  children: React.ReactNode  // содержимое внутри карточки
}

function Card({ title, children }: CardProps) {
  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: '10px',
      padding: '20px',
      margin: '10px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      maxWidth: '400px',
      width: '100%'
    }}>
      <h2 style={{ margin: '0 0 10px 0', color: '#333' }}>{title}</h2>
      <div>{children}</div>
    </div>
  )
}

export default Card