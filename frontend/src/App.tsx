import { useMemo, useState, type ReactNode } from 'react'
import { Bell, ClipboardList, FilePlus2, Filter, LayoutDashboard, Search, Settings, ShieldCheck, Users, Video, X } from 'lucide-react'

type Status = 'Em análise' | 'Aguardando assinaturas' | 'Pronta para extração' | 'Finalizada' | 'Recusada'
type Request = { id: string; employee: string; location: string; date: string; status: Status; requester: string; reason: string }

const demoRequests: Request[] = [
  { id: 'CV-2026-0042', employee: 'Mariana Costa', location: 'Portaria / Câmera 02', date: '28/10/2026 · 14:30', status: 'Em análise', requester: 'Carlos Mendes', reason: 'Apuração de ocorrência na entrada principal.' },
  { id: 'CV-2026-0041', employee: 'Rafael Lima', location: 'Expedição / Câmera 07', date: '27/10/2026 · 08:10', status: 'Aguardando assinaturas', requester: 'Ana Souza', reason: 'Formalização de incidente operacional.' },
  { id: 'CV-2026-0038', employee: 'Juliana Alves', location: 'Estacionamento / Câmera 11', date: '24/10/2026 · 18:45', status: 'Pronta para extração', requester: 'Paulo Reis', reason: 'Verificação de evento reportado ao RH.' },
  { id: 'CV-2026-0032', employee: 'Diego Rocha', location: 'Recepção / Câmera 01', date: '19/10/2026 · 09:05', status: 'Finalizada', requester: 'Carlos Mendes', reason: 'Solicitação concluída e arquivada.' },
  { id: 'CV-2026-0029', employee: 'Fernanda Dias', location: 'Docas / Câmera 05', date: '17/10/2026 · 22:20', status: 'Recusada', requester: 'Ana Souza', reason: 'Período informado não corresponde à ocorrência.' },
]

const navItems = [
  ['dashboard', 'Dashboard', LayoutDashboard], ['requests', 'Solicitações', ClipboardList], ['new', 'Nova solicitação', FilePlus2], ['approvals', 'Aprovações', ShieldCheck], ['people', 'Perfis e permissões', Users],
] as const

function StatusPill({ status }: { status: Status }) {
  const key = status.toLowerCase().replace(/ /g, '-')
  return <span className={`status status-${key}`}>{status}</span>
}

export default function App() {
  const [active, setActive] = useState('dashboard')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState<Request | null>(null)
  const filtered = useMemo(() => demoRequests.filter(r => `${r.id} ${r.employee} ${r.location} ${r.status}`.toLowerCase().includes(query.toLowerCase())), [query])

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-logo-wrap"><img className="brand-logo" src="/brand/logo-cipolatti.png" alt="Cipolatti" /></div><div><strong>CIPO VISION</strong><small>Gestão de ocorrências</small></div></div>
      <nav>{navItems.map(([key, label, Icon]) => <button className={active === key ? 'nav-item active' : 'nav-item'} onClick={() => setActive(key)} key={key}><Icon size={18}/><span>{label}</span>{key === 'approvals' && <b className="nav-count">3</b>}</button>)}</nav>
      <div className="sidebar-bottom"><button className="nav-item" onClick={() => setActive('settings')}><Settings size={18}/><span>Configurações</span></button><div className="user-card"><div className="avatar">CM</div><div><strong>Carlos Mendes</strong><small>Encarregado</small></div><span className="online"/></div></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div><p className="eyebrow">Visão geral</p><h1>{active === 'new' ? 'Nova solicitação' : active === 'approvals' ? 'Fila de aprovações' : 'Olá, Carlos'}</h1></div><div className="top-actions"><span className="demo-badge">AMBIENTE DEMONSTRATIVO</span><button className="icon-button" aria-label="Notificações"><Bell size={19}/><i/></button><div className="avatar avatar-small">CM</div></div></header>
      {active === 'new' ? <NewRequest onCancel={() => setActive('dashboard')} /> : <>
        <section className="hero-card"><div><span className="hero-kicker">Acompanhe o fluxo</span><h2>Solicitações com rastreabilidade<br/>do início ao arquivamento.</h2><p>Centralize aprovações, assinaturas e extrações autorizadas em um único lugar.</p><button className="primary" onClick={() => setActive('new')}><FilePlus2 size={17}/> Nova solicitação</button></div><div className="hero-illustration"><div className="ring ring-one"/><div className="ring ring-two"/><Video size={52}/></div></section>
        <div className="stats-grid"><Stat label="Total de solicitações" value="42" trend="+8% este mês" icon={<ClipboardList/>}/><Stat label="Aguardando sua análise" value="03" trend="Prioridade alta" icon={<ShieldCheck/>} accent/><Stat label="Em formalização" value="07" trend="2 novas hoje" icon={<Users/>}/><Stat label="Finalizadas no mês" value="18" trend="+12% vs. anterior" icon={<Video/>}/></div>
        <section className="section-heading"><div><p className="eyebrow">Acompanhamento</p><h2>Solicitações recentes</h2></div><button className="text-button" onClick={() => setActive('requests')}>Ver todas <span>→</span></button></section>
        <section className="table-card"><div className="table-toolbar"><div className="search-box"><Search size={17}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Buscar por protocolo, colaborador..."/></div><button className="filter-button"><Filter size={16}/> Filtros</button></div><div className="table-wrap"><table><thead><tr><th>Protocolo</th><th>Colaborador</th><th>Local / câmera</th><th>Data e horário</th><th>Status</th><th/></tr></thead><tbody>{filtered.map(r => <tr key={r.id} onClick={() => setSelected(r)}><td><strong>{r.id}</strong></td><td>{r.employee}<small>{r.requester}</small></td><td>{r.location}</td><td>{r.date}</td><td><StatusPill status={r.status}/></td><td><button className="row-action" aria-label={`Abrir ${r.id}`}>→</button></td></tr>)}</tbody></table>{filtered.length === 0 && <div className="empty">Nenhuma solicitação encontrada.</div>}</div></section>
      </>}
    </main>
    {selected && <div className="modal-backdrop" onClick={() => setSelected(null)}><article className="detail-modal" onClick={e => e.stopPropagation()}><button className="close" onClick={() => setSelected(null)}><X size={18}/></button><p className="eyebrow">Detalhe da solicitação</p><h2>{selected.id}</h2><StatusPill status={selected.status}/><div className="detail-grid"><div><small>Colaborador</small><strong>{selected.employee}</strong></div><div><small>Local / câmera</small><strong>{selected.location}</strong></div><div><small>Data e horário</small><strong>{selected.date}</strong></div><div><small>Solicitante</small><strong>{selected.requester}</strong></div></div><div className="reason"><small>Motivo informado</small><p>{selected.reason}</p></div><div className="timeline"><b>Histórico demonstrativo</b><span>Solicitação registrada · 28/10/2026 15:02</span><span>Em análise · aguardando decisão</span></div></article></div>}
  </div>
}

function Stat({ label, value, trend, icon, accent = false }: { label: string; value: string; trend: string; icon: ReactNode; accent?: boolean }) { return <div className={`stat-card ${accent ? 'accent' : ''}`}><div className="stat-icon">{icon}</div><span>{label}</span><strong>{value}</strong><small>{trend}</small></div> }
function NewRequest({ onCancel }: { onCancel: () => void }) { return <section className="form-card"><div className="section-heading"><div><p className="eyebrow">Fluxo de solicitação</p><h2>Registrar ocorrência</h2><p className="muted">Os campos abaixo são demonstrativos e ainda não enviam dados para uma API.</p></div><button className="text-button" onClick={onCancel}>Voltar</button></div><div className="stepper"><span className="step active"><b>1</b> Dados da ocorrência</span><span className="step"><b>2</b> Participantes</span><span className="step"><b>3</b> Revisão e envio</span></div><div className="form-grid"><label>Colaborador envolvido<input placeholder="Nome do colaborador"/></label><label>Categoria<select><option>Selecione uma categoria</option><option>Incidente operacional</option><option>Ocorrência patrimonial</option></select></label><label>Data<input type="date"/></label><label>Horário aproximado<input type="time"/></label><label>Local / câmera<input placeholder="Ex.: Portaria / Câmera 02"/></label><label>Motivo<textarea placeholder="Descreva o motivo da solicitação"/></label></div><div className="form-actions"><button className="secondary" onClick={onCancel}>Cancelar</button><button className="primary">Continuar <span>→</span></button></div></section> }
