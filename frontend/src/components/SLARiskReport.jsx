import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle, CheckCircle, Loader } from 'lucide-react';

const SLARiskReport = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/analytics/sla-risk')
      .then(res => res.json())
      .then(data => {
        setTickets(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load SLA report", err);
        setLoading(false);
      });
  }, []);

  if (loading) return (
    <div className="flex justify-center items-center h-32">
        <div className="flex items-center gap-2 text-slate-400">
            <Loader className="animate-spin" /> Analyzing Ticket Risk...
        </div>
    </div>
  );

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-orange-500/10 rounded-lg flex-shrink-0">
            <Clock className="text-orange-400" size={20} />
        </div>
        <div className="flex-1">
          <h4 className="text-base font-bold text-white">AI SLA Breach Prediction</h4>
          <p className="text-slate-400 text-xs">
             Analyzing {tickets.length} open tickets for potential delays.
          </p>
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-slate-700">
        <table className="w-full border-collapse table-fixed">
          <thead className="bg-slate-900/50">
            <tr className="text-slate-400 text-xs uppercase">
              <th className="p-4 font-semibold text-left" style={{width: '40%'}}>Ticket Issue</th>
              <th className="p-4 font-semibold text-left" style={{width: '15%'}}>Priority</th>
              <th className="p-4 font-semibold text-left" style={{width: '20%'}}>AI Prediction</th>
              <th className="p-4 font-semibold text-left" style={{width: '25%'}}>Risk Status</th>
            </tr>
          </thead>
          <tbody className="text-sm text-slate-200 divide-y divide-slate-700">
            {tickets.length === 0 ? (
                <tr>
                    <td colSpan="4" className="p-8 text-center text-slate-400">
                        <div className="flex flex-col items-center gap-2">
                            <CheckCircle className="text-slate-500" size={32} />
                            <p className="text-base">No open tickets found to analyze.</p>
                        </div>
                    </td>
                </tr>
            ) : (
                tickets.map(t => {
                const isRisk = t.predicted_hours > t.sla_limit;
                return (
                    <tr key={t.id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="p-4 font-medium text-left align-top" style={{width: '40%'}}>
                        <div className="text-white break-words">{t.title}</div>
                        <div className="text-xs text-slate-500 mt-1">ID: #{t.id}</div>
                    </td>
                    <td className="p-4 text-left align-top" style={{width: '15%'}}>
                        <span className={`inline-block text-xs font-bold uppercase px-3 py-1.5 rounded whitespace-nowrap ${
                            t.priority === 'high' ? 'bg-red-500/20 text-red-400' : 
                            t.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' : 
                            'bg-blue-500/20 text-blue-400'
                        }`}>
                            {t.priority}
                        </span>
                    </td>
                    <td className="p-4 text-left align-top" style={{width: '20%'}}>
                        <div className="font-mono text-slate-300">
                            <div className="font-bold text-base">{t.predicted_hours}h</div>
                            <div className="text-xs text-slate-500 mt-1">
                                Limit: {t.sla_limit}h
                            </div>
                        </div>
                    </td>
                    <td className="p-4 text-left align-top" style={{width: '25%'}}>
                        {isRisk ? (
                        <div className="flex items-center gap-2 text-red-400 font-bold bg-red-950/30 px-3 py-1.5 rounded-full w-fit border border-red-500/20 whitespace-nowrap">
                            <AlertTriangle size={14} /> 
                            <span>High Risk</span>
                        </div>
                        ) : (
                        <div className="flex items-center gap-2 text-green-400 font-bold bg-green-950/30 px-3 py-1.5 rounded-full w-fit border border-green-500/20 whitespace-nowrap">
                            <CheckCircle size={14} /> 
                            <span>On Track</span>
                        </div>
                        )}
                    </td>
                    </tr>
                );
                })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SLARiskReport;
