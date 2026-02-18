import { useState, useEffect } from 'react';
import Vapi from '@vapi-ai/web';
import { HeroBackground } from './components/HeroBackground';
import { VoicePanel } from './components/VoicePanel';
import { TranscriptPanel } from './components/TranscriptPanel';
import { motion } from 'framer-motion';

const PUBLIC_KEY = import.meta.env.VITE_VAPI_PUBLIC_KEY;
const ASSISTANT_ID = import.meta.env.VITE_VAPI_ASSISTANT_ID;

const vapi = new Vapi(PUBLIC_KEY || '');

interface Message {
  role: 'user' | 'ai';
  text: string;
}

function App() {
  const [connecting, setConnecting] = useState(false);
  const [connected, setConnected] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    vapi.on('call-start', () => {
      console.log('Call started');
      setConnecting(false);
      setConnected(true);
      setError(null);
    });

    vapi.on('call-end', () => {
      console.log('Call ended');
      setConnecting(false);
      setConnected(false);
      setIsSpeaking(false);
    });

    vapi.on('speech-start', () => {
      setIsSpeaking(true);
    });

    vapi.on('speech-end', () => {
      setIsSpeaking(false);
    });

    vapi.on('message', (message) => {
      if (message.type === 'transcript' && message.transcriptType === 'final') {
        const newMessage: Message = {
          role: message.role === 'assistant' ? 'ai' : 'user',
          text: message.transcript,
        };
        setMessages((prev) => [...prev, newMessage]);
      }
    });

    vapi.on('error', (e) => {
      console.error('Vapi error:', e);
      setError('Connection Error. Check your microphone and keys.');
      setConnecting(false);
      setConnected(false);
    });

    return () => {
      vapi.removeAllListeners();
    };
  }, []);

  const toggleCall = () => {
    setError(null);
    if (connected) {
      vapi.stop();
    } else {
      if (!PUBLIC_KEY || PUBLIC_KEY.includes('YOUR_PUBLIC_KEY')) {
        setError('Missing Vapi Public Key');
        return;
      }
      if (!ASSISTANT_ID || ASSISTANT_ID.includes('YOUR_ASSISTANT_ID')) {
        setError('Missing Assistant ID');
        return;
      }

      setConnecting(true);

      // Safety timeout: if not connected in 10s, reset state
      const timeout = setTimeout(() => {
        if (!connected) {
          setConnecting(false);
          setError('Connection Timeout. Refresh and try again.');
        }
      }, 10000);

      vapi.start(ASSISTANT_ID).catch((e) => {
        clearTimeout(timeout);
        console.error('Start call error:', e);
        setError('Failed to start voice assist.');
        setConnecting(false);
      });
    }
  };

  const getStatusText = () => {
    if (error) return 'System Error';
    if (connecting) return 'Connecting Nova';
    if (connected) return isSpeaking ? 'Nova Speaking' : 'Listening';
    return 'Ready for Command';
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center p-4 md:p-8">
      <HeroBackground />

      <motion.main
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-start"
      >
        <div className="flex flex-col gap-6">
          <VoicePanel
            connecting={connecting}
            connected={connected}
            isSpeaking={isSpeaking}
            onToggle={toggleCall}
            status={getStatusText()}
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

      {/* Background Ambient Glow */}
      <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-cyan-500/5 blur-[120px] rounded-full -z-10" />
    </div>
  );
}

export default App;
