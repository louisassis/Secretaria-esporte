
// Frontend (React + Tailwind + Recharts)
// App.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
  const [eventos, setEventos] = useState([]);
  const [form, setForm] = useState({ nome: '', data: '', local: '', tipo: '', publico_estimado: '', custo: '', descricao: '', regiao: '' });
  const [token, setToken] = useState('');

  useEffect(() => {
    axios.get('http://localhost:8000/eventos').then(res => setEventos(res.data));
  }, []);

  const custoPorTipo = eventos.reduce((acc, ev) => {
    acc[ev.tipo] = (acc[ev.tipo] || 0) + ev.custo;
    return acc;
  }, {});

  const eventosPorRegiao = eventos.reduce((acc, ev) => {
    acc[ev.regiao] = (acc[ev.regiao] || 0) + 1;
    return acc;
  }, {});

  const dadosCusto = Object.entries(custoPorTipo).map(([tipo, custo]) => ({ tipo, custo }));
  const dadosRegiao = Object.entries(eventosPorRegiao).map(([regiao, total]) => ({ regiao, total }));

  const login = async () => {
    const res = await axios.post('http://localhost:8000/login', new URLSearchParams({ username: 'admin', password: 'admin' }));
    setToken(res.data.access_token);
  };

  const cadastrarEvento = async () => {
    await axios.post('http://localhost:8000/eventos', form, { headers: { Authorization: `Bearer ${token}` } });
    const res = await axios.get('http://localhost:8000/eventos');
    setEventos(res.data);
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Eventos Esportivos - DF</h1>

      <button className="mb-4 bg-blue-500 text-white px-4 py-2 rounded" onClick={login}>Login</button>

      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Cadastrar Novo Evento</h2>
        <div className="grid grid-cols-2 gap-2">
          {Object.keys(form).map(field => (
            <input
              key={field}
              className="border p-2 rounded"
              placeholder={field}
              value={form[field]}
              onChange={e => setForm({ ...form, [field]: e.target.value })}
            />
          ))}
        </div>
        <button className="mt-2 bg-green-500 text-white px-4 py-2 rounded" onClick={cadastrarEvento}>Cadastrar</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white shadow p-4 rounded-2xl">
          <h2 className="text-xl font-semibold mb-2">Eventos Registrados</h2>
          <ul className="max-h-64 overflow-y-auto">
            {eventos.map(ev => (
              <li key={ev._id} className="border-b py-2">
                <strong>{ev.nome}</strong> - {ev.local} ({new Date(ev.data).toLocaleDateString()})
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white shadow p-4 rounded-2xl">
          <h2 className="text-xl font-semibold mb-2">Custo por Tipo</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={dadosCusto}>
              <XAxis dataKey="tipo" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="custo" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white shadow p-4 rounded-2xl">
          <h2 className="text-xl font-semibold mb-2">Eventos por Região</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={dadosRegiao}>
              <XAxis dataKey="regiao" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="total" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default App;
