export default function AdminDashboard() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Панель администратора</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginTop: '20px' }}>
        <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
          <h3>👥 Управление пользователями</h3>
          <p>Создание, редактирование, сброс паролей.</p>
        </div>
        <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
          <h3>📚 Справочники</h3>
          <p>Группы, специальности, дисциплины, организации.</p>
        </div>
        <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
          <h3>📥 Импорт / Экспорт</h3>
          <p>Массовая загрузка данных из Excel/CSV.</p>
        </div>
        <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
          <h3>⚙️ Django Admin</h3>
          <a href="/django-admin/" target="_blank" rel="noopener noreferrer" style={{ color: '#1976d2' }}>Перейти в стандартную админку →</a>
        </div>
      </div>
    </div>
  );
}
