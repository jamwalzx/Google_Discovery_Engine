"use client";

import React, { useState, useMemo, useEffect } from 'react';

// Hardcoded defaults for Discovery Map & Query Lab since Phase 4 only generates Funnel, Memory, Opportunity
const CLUSTERS = [
  { id: 1, name: 'Fuzzy Place & Ambience', color: '#8b5cf6', badge: 'bg-purple-500/20 text-purple-300 border-purple-500/40' },
  { id: 2, name: 'Utility & Document Text', color: '#38bdf8', badge: 'bg-sky-500/20 text-sky-300 border-sky-500/40' },
  { id: 3, name: 'Fleeting Serendipity', color: '#ec4899', badge: 'bg-pink-500/20 text-pink-300 border-pink-500/40' },
  { id: 4, name: 'Co-temporal Events', color: '#10b981', badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' },
  { id: 5, name: 'Emotional / Sensory Cues', color: '#f59e0b', badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40' },
];

const generateClusterPoints = () => {
  const points = [];
  const centers = [
    { cx: 32, cy: 38, id: 1, label: 'Fuzzy Place', quote: '"Looked like a rustic wine cellar with arched brick ceiling"' },
    { cx: 72, cy: 28, id: 2, label: 'Utility Docs', quote: '"The serial number sticker behind my dishwasher was illegible"' },
    { cx: 68, cy: 74, id: 3, label: 'Fleeting Cues', quote: '"A dog jumping through a water sprinkler mid-air during sunset"' },
    { cx: 28, cy: 76, id: 4, label: 'Co-temporal', quote: '"Photo taken right after our flight got canceled in Munich"' },
    { cx: 50, cy: 50, id: 5, label: 'Sensory Cues', quote: '"That cozy rainy afternoon with hot matcha mug in hand"' },
  ];

  centers.forEach((center) => {
    for (let i = 0; i < 48; i++) {
      const r = Math.random() * 14;
      const theta = Math.random() * 2 * Math.PI;
      const x = Math.max(5, Math.min(95, center.cx + r * Math.cos(theta) + (Math.random() - 0.5) * 6));
      const y = Math.max(5, Math.min(95, center.cy + r * Math.sin(theta) + (Math.random() - 0.5) * 6));
      points.push({
        id: `${center.id}-${i}`,
        x: parseFloat(x.toFixed(2)),
        y: parseFloat(y.toFixed(2)),
        clusterId: center.id,
        clusterName: center.label,
        quote: center.quote,
        volume: Math.floor(Math.random() * 800) + 120,
        confidence: Math.floor(Math.random() * 30) + 70
      });
    }
  });
  return points;
};
const DISCOVERY_POINTS = generateClusterPoints();

export default function Dashboard() {
  const [currentTab, setCurrentTab] = useState('overview');
  const [aiWeight, setAiWeight] = useState(60);
  const [stratWeight, setStratWeight] = useState(40);
  const [activeClusterFilter, setActiveClusterFilter] = useState('all');
  const [hoveredPoint, setHoveredPoint] = useState<any>(null);

  // Data from backend
  const [funnelData, setFunnelData] = useState<any[]>([]);
  const [opportunityData, setOpportunityData] = useState<any[]>([]);
  const [memoryData, setMemoryData] = useState<any>(null);
  const [selectedFunnelStep, setSelectedFunnelStep] = useState<any>(null);

  // Phase 6 Live Features
  const [chatInput, setChatInput] = useState('');
  const [chatLog, setChatLog] = useState<{role: string, text: string}[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);

  const [liveInput, setLiveInput] = useState('');
  const [liveResult, setLiveResult] = useState<any>(null);
  const [isLiveLoading, setIsLiveLoading] = useState(false);

  useEffect(() => {
    fetch('/api/metrics')
      .then(res => res.json())
      .then(data => {
        if (!data.error) {
          const funnelStages = [
            { id: 'F1', name: 'F1: Express Intent', desc: 'User types initial search term or memory clue', leakCause: 'Initial formulation barrier' },
            { id: 'F2', name: 'F2: Query Understand', desc: 'AI parser extracts spatial, temporal & entity tags', leakCause: 'Semantic & synonym parsing mismatch' },
            { id: 'F3', name: 'F3: Photo Candidate Recall', desc: 'Embedding index returns top-50 candidate photos', leakCause: 'Index misses non-indexed OCR / background details' },
            { id: 'F4', name: 'F4: Visual Recognition', desc: 'User scans grid to recognize target among results', leakCause: 'Thumbnails too small or clutter obfuscates target' },
            { id: 'F5', name: 'F5: Query Refine Loop', desc: 'User reformulates query with fallback filters', leakCause: 'Cognitive fatigue; memory mismatch escalation' },
            { id: 'F6', name: 'F6: Finished & Retrieved', desc: 'Target photo opened, favorited, shared or exported', leakCause: 'Total Leakage across discovery flow' }
          ];
          
          let prevRate = 100;
          const mappedFunnel = funnelStages.map((stage, i) => {
             const val = data.funnel && data.funnel[stage.id] ? data.funnel[stage.id] : (100 - (i*15)); 
             const currentRate = i === 0 ? 100 : val;
             const drop = prevRate - currentRate;
             prevRate = currentRate;
             return {
               ...stage,
               rate: currentRate.toFixed(1),
               dropRate: drop > 0 ? drop.toFixed(1) : 0,
               count: `${Math.floor(1420800 * (currentRate/100)).toLocaleString()}`
             };
          });
          setFunnelData(mappedFunnel);
          setSelectedFunnelStep(mappedFunnel[2]);

          if (data.opportunity && data.opportunity.length > 0) {
            setOpportunityData(data.opportunity.map((o: any, i: number) => ({
              ...o,
              id: i,
              sampleQuery: `Query related to ${o.archetype}`,
              status: o.frequency > 0.1 ? 'High Opportunity' : 'Investigating'
            })));
          } else {
             setOpportunityData([
               { id: 1, archetype: 'Fuzzy Place & Atmospheric Memory', stage: 'F3', frequency: 0.15, severity: 4.2, ai_fit: 90, strat_fit: 80, sampleQuery: '"that candlelit patio near the olive trees"', status: 'High Opportunity' }
             ]);
          }
          setMemoryData(data.memory);
        }
      })
      .catch(console.error);
  }, []);

  const sortedArchetypes = useMemo(() => {
    if (!opportunityData) return [];
    return [...opportunityData].map(item => {
      const normalizedAi = (item.ai_fit * (aiWeight / 50));
      const normalizedStrat = (item.strat_fit * (stratWeight / 50));
      const freqScore = item.frequency * 100;
      const sevScore = item.severity * 20; 
      const totalScore = Math.round((freqScore * 0.25) + (sevScore * 0.25) + (normalizedAi * 0.25) + (normalizedStrat * 0.25));
      return {
        ...item,
        totalScore: Math.min(99, Math.max(10, totalScore)),
        freqScore: Math.round(freqScore),
        sevScore: Math.round(sevScore)
      };
    }).sort((a, b) => b.totalScore - a.totalScore);
  }, [opportunityData, aiWeight, stratWeight]);

  const filteredPoints = useMemo(() => {
    if (activeClusterFilter === 'all') return DISCOVERY_POINTS;
    return DISCOVERY_POINTS.filter(p => p.clusterId === parseInt(activeClusterFilter));
  }, [activeClusterFilter]);

  const handleSendChat = async () => {
    if (!chatInput) return;
    const msg = chatInput;
    setChatLog(prev => [...prev, {role: 'user', text: msg}]);
    setChatInput('');
    setIsChatLoading(true);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      setChatLog(prev => [...prev, {role: 'model', text: data.reply || data.error}]);
    } catch (e) {
      setChatLog(prev => [...prev, {role: 'model', text: 'Error connecting to RAG endpoint'}]);
    }
    setIsChatLoading(false);
  };

  const handleTryLive = async () => {
    if (!liveInput) return;
    setIsLiveLoading(true);
    try {
      const res = await fetch('/api/try-live', {
        method: 'POST',
        body: JSON.stringify({ text: liveInput })
      });
      const data = await res.json();
      setLiveResult(data);
    } catch (e) {
      setLiveResult({ error: 'Failed to process' });
    }
    setIsLiveLoading(false);
  };

  if (!funnelData.length) return <div className="p-10 text-white">Loading Engine Telemetry...</div>;

  return (
    <div className="flex min-h-screen">
      {/* SIDEBAR */}
      <aside className="w-64 border-r border-white/[0.08] bg-[#090a16]/90 backdrop-blur-2xl flex flex-col fixed inset-y-0 z-40">
        <div className="p-5 border-b border-white/[0.08] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500 via-indigo-600 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/25 ring-1 ring-white/20">
              <span className="text-white font-bold text-xs">RS</span>
            </div>
            <div>
              <h1 className="font-bold text-base tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-purple-300">
                RecallScope
              </h1>
              <p className="text-[10px] font-mono tracking-wider text-purple-400 uppercase font-medium">
                Failure Intel v2.4
              </p>
            </div>
          </div>
          <span className="w-2 h-2 rounded-full bg-emerald-400 glow-dot animate-pulse"></span>
        </div>

        <nav className="p-3 space-y-1 flex-1 overflow-y-auto">
          <div className="px-3 py-2 text-[10px] font-mono tracking-wider uppercase text-slate-400 font-semibold">Analytics Core</div>
          
          {[
            { id: 'overview', label: 'Overview Dashboard' },
            { id: 'live_ai', label: 'Ask the Evidence (Live RAG)', badge: 'Phase 6' }
          ].map(tab => {
            const isActive = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setCurrentTab(tab.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all group ${
                  isActive 
                    ? 'bg-gradient-to-r from-purple-600/30 to-indigo-600/10 text-white border border-purple-500/40 shadow-sm shadow-purple-900/30' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className={`text-[9px] px-1.5 py-0.5 rounded-md font-mono ${isActive ? 'bg-purple-500/30 text-purple-200' : 'bg-white/[0.06] text-slate-400'}`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </aside>

      {/* MAIN CONTENT */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <header className="h-16 border-b border-white/[0.08] bg-[#090a16]/75 backdrop-blur-xl sticky top-0 z-30 px-8 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <span className="text-purple-400">Project</span>
            <span>/</span>
            <span className="text-slate-200 font-medium">Visual Search Failures</span>
            <span>/</span>
            <span className="text-purple-300 font-semibold uppercase">{currentTab}</span>
          </div>
        </header>

        <main className="flex-1 p-8 space-y-8 overflow-y-auto max-w-[1600px] w-full mx-auto">
          
          {currentTab === 'overview' && (
            <>
              {/* HERO */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border-white/[0.08] relative overflow-hidden">
                <div className="absolute right-0 top-0 w-96 h-full bg-gradient-to-l from-purple-600/10 via-pink-600/5 to-transparent pointer-events-none"></div>
                <div className="space-y-1 relative z-10">
                  <h2 className="text-2xl font-bold text-white tracking-tight">Photo Retrieval Failure Engine</h2>
                  <p className="text-xs text-slate-400 max-w-2xl">Bridging what humans remember vs what engines index.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
                {/* FUNNEL */}
                <div className="xl:col-span-7 glass-panel p-6 rounded-2xl flex flex-col justify-between">
                  <h3 className="text-base font-bold text-white mb-6">The Funnel Leak Architecture (F1 → F6)</h3>
                  <div className="space-y-3.5">
                    {funnelData.map((step, idx) => {
                      const isSelected = selectedFunnelStep?.id === step.id;
                      return (
                        <div key={step.id} onClick={() => setSelectedFunnelStep(step)} className={`p-3 rounded-xl cursor-pointer transition-all duration-200 border ${isSelected ? 'bg-purple-950/40 border-purple-500/60' : 'bg-white/[0.02] border-white/[0.05]'}`}>
                          <div className="flex justify-between text-xs mb-1.5">
                            <span className="text-slate-200">{step.name}</span>
                            <span className="text-white font-bold">{step.rate}%</span>
                          </div>
                          <div className="w-full bg-white/[0.06] h-3 rounded-full overflow-hidden p-[1px]">
                            <div className="h-full rounded-full transition-all duration-500" style={{ width: `${step.rate}%`, background: 'linear-gradient(90deg, #8b5cf6, #6366f1)' }}></div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* MEMORY LENSES (Mocked for speed here) */}
                <div className="xl:col-span-5 glass-panel p-6 rounded-2xl">
                  <h3 className="text-base font-bold text-white mb-6">Memory Lenses: Cognitive Bias Gap</h3>
                  <div className="space-y-3.5 text-xs text-slate-400">
                      {memoryData ? (
                        <div>
                          <p>Top Remembered Cues: {Object.keys(memoryData.remembered).join(', ')}</p>
                          <p className="mt-2">Top Forgotten Cues: {Object.keys(memoryData.forgotten).join(', ')}</p>
                        </div>
                      ) : <p>Loading memory metrics...</p>}
                  </div>
                </div>
              </div>

              {/* OPPORTUNITY SCORING */}
              <div className="glass-panel p-6 rounded-2xl">
                <div className="flex flex-col lg:flex-row justify-between mb-6">
                  <h3 className="text-base font-bold text-white">Opportunity Scoring Matrix (Dynamic Weight Engine)</h3>
                  <div className="flex gap-6">
                    <div>
                      <span className="text-xs text-slate-300 block mb-1">AI Addressability: {aiWeight}%</span>
                      <input type="range" min="10" max="90" value={aiWeight} onChange={(e) => setAiWeight(Number(e.target.value))} />
                    </div>
                    <div>
                      <span className="text-xs text-slate-300 block mb-1">Strategic Fit: {stratWeight}%</span>
                      <input type="range" min="10" max="90" value={stratWeight} onChange={(e) => setStratWeight(Number(e.target.value))} />
                    </div>
                  </div>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-white/[0.08] text-slate-400 font-mono text-[11px] uppercase">
                        <th className="py-3 px-4">Archetype</th>
                        <th className="py-3 px-3">Leak Stage</th>
                        <th className="py-3 px-3">Freq Score</th>
                        <th className="py-3 px-3">Sev Score</th>
                        <th className="py-3 px-4 text-right">Opportunity Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.05]">
                      {sortedArchetypes.map((arch: any, idx: number) => (
                        <tr key={idx} className="hover:bg-white/[0.03]">
                          <td className="py-3 px-4 font-semibold text-slate-200">{arch.archetype}</td>
                          <td className="py-3 px-3 text-slate-300">{arch.stage}</td>
                          <td className="py-3 px-3 text-slate-300">{arch.freqScore}</td>
                          <td className="py-3 px-3 text-rose-400">{arch.sevScore}</td>
                          <td className="py-3 px-4 text-right text-amber-300 font-bold">{arch.totalScore}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {currentTab === 'live_ai' && (
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
              
              {/* CHAT RAG */}
              <div className="glass-panel p-6 rounded-2xl flex flex-col h-[600px]">
                <div className="mb-4">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-sm bg-purple-500"></span>
                    Ask the Evidence (SQL + RAG)
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">Talk to Gemini 1.5 Flash. It has a tool to query the SQLite Database directly.</p>
                </div>
                
                <div className="flex-1 bg-[#06060c] rounded-xl border border-white/[0.08] p-4 overflow-y-auto space-y-4 mb-4">
                  {chatLog.length === 0 && <p className="text-xs text-slate-500 font-mono text-center mt-10">Send a message to query the SQLite DB.</p>}
                  {chatLog.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`p-3 rounded-xl max-w-[80%] text-sm ${msg.role === 'user' ? 'bg-purple-600 text-white rounded-br-none' : 'bg-white/[0.05] text-slate-200 rounded-bl-none border border-white/[0.1]'}`}>
                        {msg.text}
                      </div>
                    </div>
                  ))}
                  {isChatLoading && <div className="text-xs text-slate-500 font-mono animate-pulse">Gemini is querying the DB...</div>}
                </div>

                <div className="flex gap-2">
                  <input 
                    value={chatInput} onChange={e => setChatInput(e.target.value)} 
                    onKeyDown={e => e.key === 'Enter' && handleSendChat()}
                    placeholder="e.g. What are the top failure archetypes?"
                    className="flex-1 bg-white/[0.05] border border-white/[0.1] rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-purple-500/50"
                  />
                  <button onClick={handleSendChat} disabled={isChatLoading} className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all disabled:opacity-50">
                    Send
                  </button>
                </div>
              </div>

              {/* TRY LIVE */}
              <div className="glass-panel p-6 rounded-2xl flex flex-col h-[600px]">
                <div className="mb-4">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span>
                    Try Live Extraction
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">Simulates Stage A & B of the pipeline on raw feedback using Gemini JSON schema extraction.</p>
                </div>

                <textarea 
                  value={liveInput} onChange={e => setLiveInput(e.target.value)}
                  placeholder="Paste a raw user complaint here... (e.g. 'I couldn't find a photo of my dog wearing a party hat from last summer')"
                  className="w-full h-32 bg-white/[0.05] border border-white/[0.1] rounded-lg p-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 resize-none mb-4"
                ></textarea>
                
                <button onClick={handleTryLive} disabled={isLiveLoading} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all disabled:opacity-50 mb-4">
                  {isLiveLoading ? 'Extracting Dimensions...' : 'Run Extraction Pipeline'}
                </button>

                <div className="flex-1 bg-[#06060c] rounded-xl border border-white/[0.08] p-4 overflow-y-auto">
                  <h4 className="text-[10px] uppercase font-mono text-slate-400 mb-2">Extraction Output (JSON)</h4>
                  {liveResult ? (
                    <pre className="text-xs text-emerald-300 font-mono whitespace-pre-wrap">{JSON.stringify(liveResult, null, 2)}</pre>
                  ) : (
                    <p className="text-xs text-slate-500 font-mono text-center mt-10">Run the pipeline to see structured JSON output.</p>
                  )}
                </div>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
