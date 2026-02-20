import { useRef, useState, useEffect, useMemo } from 'react';
import Vapi from '@vapi-ai/web';
import { HeroBackground } from './components/HeroBackground';
import { VoicePanel } from './components/VoicePanel';
import { TranscriptPanel } from './components/TranscriptPanel';
import { BookingCalendar } from './components/BookingCalendar';
import { BookingsList } from './components/BookingsList';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, Mic, Shield } from 'lucide-react';

const PUBLIC_KEY = import.meta.env.VITE_VAPI_PUBLIC_KEY;
const ASSISTANT_ID = import.meta.env.VITE_VAPI_ASSISTANT_ID;

interface Message {
  role: 'user' | 'ai';
  text: string;
}

function App() {
  const [view, setView] = useState<'voice' | 'calendar' | 'bookings'>('voice');
  const [connecting, setConnecting] = useState(false);
  const [connected, setConnected] = useState(false);
  const connectedRef = useRef(false);
  const timeoutRef = useRef<any>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const vapi = useMemo(() => new Vapi(PUBLIC_KEY || ''), []);

  useEffect(() => {
    if (!vapi) return;

    vapi.on('call-start', () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      setConnecting(false);
      setConnected(true);
      connectedRef.current = true;
      setError(null);
    });

    vapi.on('call-end', () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      setConnecting(false);
      setConnected(false);
      connectedRef.current = false;
      setIsSpeaking(false);
    });

    vapi.on('speech-start', () => setIsSpeaking(true));
    vapi.on('speech-end', () => setIsSpeaking(false));

    vapi.on('message', (message: any) => {
      if (message.type === 'transcript' && message.transcriptType === 'final') {
        setMessages((prev) => {
          const lastMsg = prev[prev.length - 1];
          const newRole = message.role === 'assistant' ? 'ai' : 'user';
          if (lastMsg && lastMsg.role === newRole && lastMsg.text === message.transcript) {
            return prev;
          }
          return [...prev, { role: newRole, text: message.transcript }];
        });
      }

      if (message.type === 'tool-call-result' && message.toolCallResult?.name === 'create-booking') {
        setRefreshKey(prev => prev + 1);
      }
    });

    vapi.on('error', (e: any) => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      let msg = 'Connection Error';
      if (typeof e === 'string') msg = e;
      else if (e?.message) msg = e.message;
      else if (e?.error?.message) msg = e.error.message;
      else {
        try { msg = JSON.stringify(e); } catch { msg = 'Unspecified Error'; }
      }
      setError(`${String(msg).toUpperCase()}. CHECK MIC/INTERNET.`);
      setConnecting(false);
      setConnected(false);
      connectedRef.current = false;
    });

    return () => {
      vapi.removeAllListeners();
    };
  }, [vapi]);

  const toggleCall = async () => {
    setError(null);
    if (connected) {
      vapi.stop();
    } else {
      if (!PUBLIC_KEY || PUBLIC_KEY.includes('YOUR_PUBLIC_KEY')) {
        setError('Missing Vapi Public Key');
        return;
      }
      if (!ASSISTANT_ID || ASSISTANT_ID.includes('YOUR_ASSISTANT_ID')) {
        setError('Assistant Config Error');
        return;
      }
      setConnecting(true);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        if (!connectedRef.current) {
          vapi.stop();
          setConnecting(false);
          setError('Handshake Timeout. Check internet.');
        }
      }, 30000);
      vapi.start(ASSISTANT_ID).catch((e) => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        const errorMsg = typeof e === 'string' ? e : e?.message || 'Start Failed';
        setError(errorMsg.toUpperCase());
        setConnecting(false);
      });
    }
  };

  const getStatusText = () => {
    if (error) return error;
    if (connecting) return 'Connecting Nova';
    if (connected) return isSpeaking ? 'Nova Speaking' : 'Listening';
    return 'Ready for Command';
  };

  return (
    <div className="relative min-h-screen w-full flex flex-col items-center justify-center p-4 md:p-8">
      <HeroBackground />

      <div className="fixed top-8 z-50 flex items-center gap-1 p-1 bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-full shadow-2xl">
        <button
          onClick={() => setView('voice')}
          className={`flex items-center gap-2 px-6 py-2 rounded-full transition-all text-xs font-bold tracking-widest uppercase ${view === 'voice' ? 'bg-cyan-500 text-slate-900 shadow-lg' : 'text-slate-400 hover:text-white'}`}
        >
          <Mic className="w-3.5 h-3.5" />
          <span>Nova Assist</span>
        </button>
        <button
          onClick={() => setView('calendar')}
          className={`flex items-center gap-2 px-6 py-2 rounded-full transition-all text-xs font-bold tracking-widest uppercase ${view === 'calendar' ? 'bg-cyan-500 text-slate-900 shadow-lg' : 'text-slate-400 hover:text-white'}`}
        >
          <Calendar className="w-3.5 h-3.5" />
          <span>Schedule</span>
        </button>
        <button
          onClick={() => setView('bookings')}
          className={`flex items-center gap-2 px-6 py-2 rounded-full transition-all text-xs font-bold tracking-widest uppercase ${view === 'bookings' ? 'bg-cyan-500 text-slate-900 shadow-lg' : 'text-slate-400 hover:text-white'}`}
        >
          <Shield className="w-3.5 h-3.5" />
          <span>Booked</span>
        </button>
      </div>

      <AnimatePresence mode="wait">
        {view === 'voice' ? (
          <motion.main
            key="voice"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8 lg:gap-12 items-start mt-16 md:mt-24"
          >
            <div className="flex flex-col gap-6">
              <VoicePanel
                connecting={connecting}
                connected={connected}
                isSpeaking={isSpeaking}
                onToggle={toggleCall}
                status={getStatusText()}
                hasError={!!error}
              />
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="px-6 flex items-center gap-4 text-slate-500"
              >
                <div className="h-[1px] flex-1 bg-white/10" />
                <span className="text-[10px] uppercase tracking-[0.4em] font-bold">Renta Car Elite</span>
                <div className="h-[1px] flex-1 bg-white/10" />
              </motion.div>
            </div>
            <TranscriptPanel
              messages={messages}
              onClear={() => setMessages([])}
            />
          </motion.main>
        ) : view === 'calendar' ? (
          <motion.main
            key="calendar"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            className="w-full max-w-5xl mx-auto mt-20"
          >
            <BookingCalendar refreshKey={refreshKey} />
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.4 }}
              transition={{ delay: 0.6 }}
              className="text-center mt-6 text-[10px] uppercase tracking-[0.5em] text-slate-500 font-bold"
            >
              Real-time Fleet Live Schedule
            </motion.p>
          </motion.main>
        ) : (
          <motion.main
            key="bookings"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            className="w-full"
          >
            <BookingsList />
          </motion.main>
        )}
      </AnimatePresence>

      <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-cyan-500/5 blur-[120px] rounded-full -z-10" />
    </div>
  );
}

export default App;
