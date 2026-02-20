import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useRef } from 'react';
import { Trash2, User, Cpu } from 'lucide-react';

interface Message {
    role: 'user' | 'ai';
    text: string;
}

interface TranscriptPanelProps {
    messages: Message[];
    onClear: () => void;
}

export const TranscriptPanel = ({ messages, onClear }: TranscriptPanelProps) => {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-panel p-6 md:p-8 flex flex-col gap-6 w-full h-[500px] md:h-[600px] glow-cyan mx-auto"
        >
            <div className="flex justify-between items-center pb-4 border-b border-white/10">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-cyan-500/10 rounded-lg border border-cyan-500/20">
                        <Cpu size={16} className="text-cyan-400" />
                    </div>
                    <h3 className="text-sm font-bold uppercase tracking-widest text-slate-300">Live Session</h3>
                </div>
                <button
                    onClick={onClear}
                    className="p-2 hover:bg-white/5 rounded-lg transition-colors text-slate-500 hover:text-rose-400"
                    title="Clear Session"
                >
                    <Trash2 size={16} />
                </button>
            </div>

            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto pr-2 flex flex-col gap-6 scroll-smooth"
            >
                <AnimatePresence initial={false}>
                    {messages.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex-1 flex flex-col items-center justify-center text-slate-600 italic gap-3"
                        >
                            <div className="w-12 h-12 rounded-full border border-dashed border-slate-700 flex items-center justify-center">
                                <User size={20} className="opacity-30" />
                            </div>
                            <p className="text-xs uppercase tracking-widest font-medium">Waiting for interaction...</p>
                        </motion.div>
                    ) : (
                        messages.map((m, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                transition={{ duration: 0.3 }}
                                className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border 
                  ${m.role === 'user' ? 'bg-cyan-500/10 border-cyan-500/20' : 'bg-slate-800 border-white/5'}`}
                                >
                                    {m.role === 'user' ? <User size={14} className="text-cyan-400" /> : <Cpu size={14} className="text-slate-400" />}
                                </div>
                                <div className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed
                  ${m.role === 'user'
                                        ? 'bg-cyan-600 text-white rounded-tr-none shadow-lg shadow-cyan-900/20'
                                        : 'bg-white/5 text-slate-200 border border-white/5 rounded-tl-none'}`}
                                >
                                    {m.text}
                                </div>
                            </motion.div>
                        ))
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
};
