import { motion, AnimatePresence } from 'framer-motion';
import { Play, Square, Loader2, Gauge, ShieldCheck, Zap } from 'lucide-react';

interface VoicePanelProps {
    connecting: boolean;
    connected: boolean;
    isSpeaking: boolean;
    onToggle: () => void;
    status: string;
    hasError?: boolean;
}

export const VoicePanel = ({ connecting, connected, isSpeaking, onToggle, status, hasError }: VoicePanelProps) => {
    return (
        <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-panel p-6 sm:p-8 md:p-12 flex flex-col gap-6 md:gap-8 w-full max-w-md glow-cyan mx-auto"
        >
            <div className="flex justify-between items-start">
                <div>
                    <motion.h2
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-3xl md:text-4xl font-extrabold tracking-tighter bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent"
                    >
                        NOVA
                    </motion.h2>
                    <p className="text-cyan-400/80 font-medium tracking-widest text-xs mt-1 uppercase">Luxury Voice Assist</p>
                </div>
                <div className="p-2 bg-white/5 rounded-full border border-white/10">
                    <Gauge size={20} className="text-slate-400" />
                </div>
            </div>

            <div className="flex flex-col items-center gap-6 py-6">
                <div className="relative">
                    {/* Pulse Rings for Listening State */}
                    <AnimatePresence>
                        {connected && !isSpeaking && (
                            <>
                                <motion.div
                                    initial={{ scale: 0.8, opacity: 0 }}
                                    animate={{ scale: 1.5, opacity: 0 }}
                                    exit={{ opacity: 0 }}
                                    transition={{ duration: 2, repeat: Infinity }}
                                    className="absolute inset-0 rounded-full border-2 border-cyan-500/30"
                                />
                                <motion.div
                                    initial={{ scale: 0.8, opacity: 0 }}
                                    animate={{ scale: 1.3, opacity: 0 }}
                                    exit={{ opacity: 0 }}
                                    transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                                    className="absolute inset-0 rounded-full border-2 border-cyan-500/20"
                                />
                            </>
                        )}
                    </AnimatePresence>

                    <button
                        onClick={onToggle}
                        disabled={connecting}
                        className={`relative z-10 w-28 h-28 rounded-full flex justify-center items-center transition-all duration-500 shadow-2xl
              ${connected ? 'bg-rose-500' : 'bg-cyan-500'} 
              ${connecting ? 'opacity-80' : 'hover:scale-105 active:scale-95 group'}
            `}
                    >
                        {connecting ? (
                            <Loader2 className="animate-spin text-white" size={48} />
                        ) : connected ? (
                            <Square size={40} className="text-white fill-white" />
                        ) : (
                            <Play size={40} className="text-white fill-white ml-2 transition-transform group-hover:scale-110" />
                        )}
                    </button>
                </div>

                <div className="flex flex-col items-center gap-2">
                    <div className={`flex items-center gap-2 px-4 py-1.5 bg-white/5 border border-white/10 rounded-full ${hasError ? 'border-rose-500/50 bg-rose-500/5' : ''}`}>
                        <div className={`w-2 h-2 rounded-full ${hasError ? 'bg-rose-500' :
                            connected ? 'bg-emerald-400 animate-pulse' :
                                connecting ? 'bg-cyan-400 animate-bounce' : 'bg-slate-500'
                            }`} />
                        <span className={`text-sm font-semibold tracking-wide uppercase ${hasError ? 'text-rose-400' : 'text-slate-300'}`}>
                            {status}
                        </span>
                    </div>

                    {isSpeaking && (
                        <div className="flex gap-1 h-5 items-center">
                            {[...Array(5)].map((_, i) => (
                                <div key={i} className="voice-wave" />
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-4">
                <QuickAction text="SUV Availablity" icon={<Zap size={14} />} onClick={() => { }} />
                <QuickAction text="Luxury Sedan" icon={<ShieldCheck size={14} />} onClick={() => { }} />
            </div>

            <p className="text-center text-[10px] text-slate-500 uppercase tracking-[0.2em] font-medium">
                Microphone Access Required For Assist
            </p>
        </motion.div>
    );
};

const QuickAction = ({ text, icon, onClick }: { text: string; icon: any; onClick: () => void }) => (
    <button
        onClick={onClick}
        className="flex items-center gap-2 px-3 py-2 bg-white/5 border border-white/5 rounded-xl text-[11px] text-slate-400 hover:bg-white/10 hover:border-white/20 transition-all uppercase tracking-wider font-bold"
    >
        {icon}
        {text}
    </button>
);
