export default function MckDashboard() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Кабинет Председателя МЦК</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginTop: '20px' }}>
        <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
          <h3>📖 Рабочие программы (РПД)</h3>
          <p>Утверждение и проверка рабочих программ дисциплин.</p>
        </div>
        <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
          <h3>📅 Расписание аттестации</h3>
          <p>Утверждение графиков экзаменов и зачетов.</p>
        </div>
        <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
          <h3>📊 Мониторинг качества</h3>
          <p>Аналитика по методическим цикловым комиссиям.</p>
        </div>
      </div>
    </div>
  );
}
