

interface ButtonProps {
  text: string          // текст на кнопке
  onClick: () => void   // функция, которая вызывается при клике
  variant?: 'primary' | 'secondary'  // опциональный параметр
}

function Button({ text, onClick, variant = 'primary' }: ButtonProps) {
  const styles = {
    primary: {
      backgroundColor: '#4CAF50',
      color: 'white'
    },
    secondary: {
      backgroundColor: '#f44336',
      color: 'white'
    }
  }

  return (
    <button 
      onClick={onClick}
      style={{
        padding: '10px 20px',
        fontSize: '16px',
        cursor: 'pointer',
        border: 'none',
        borderRadius: '5px',
        margin: '5px',
        ...styles[variant]
      }}
    >
      {text}
    </button>
  )
}

export default Button