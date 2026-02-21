import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Phone, MapPin, Car, Shield, Lock, Search, Filter, ChevronDown, Loader2 } from 'lucide-react';

interface Booking {
    id: number;
    customerName: string;
    customerPhone: string;
    pickupDateTime: string;
    returnDateTime: string;
    duration: string;
    pickupLocation: string;
    dropoffLocation: string;
    carCategory: string;
    status: string;
}

const ADMIN_KEY = import.meta.env.VITE_ADMIN_KEY || 'RENTACAR_ELITE_2026';

export const BookingsList = ({ refreshKey = 0 }: { refreshKey?: number }) => {
    const [isAdmin, setIsAdmin] = useState(false);
    const [pin, setPin] = useState('');
    const [error, setError] = useState('');
    const [bookings, setBookings] = useState<Booking[]>([]);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(0);
    const [total, setTotal] = useState(0);
    const [categoryFilter, setCategoryFilter] = useState('');
    const [hasMore, setHasMore] = useState(true);

    const fetchBookings = useCallback(async (reset = false) => {
        setLoading(true);
        const offset = reset ? 0 : page * 10;
        try {
            const resp = await fetch(`/api/get-all-bookings?limit=10&offset=${offset}${categoryFilter ? `&carCategory=${categoryFilter}` : ''}&status=booked`, {
                headers: {
                    'X-Admin-Key': ADMIN_KEY,
                    'Cache-Control': 'no-cache'
                }
            });
            const data = await resp.json();
            if (data.success) {
                setBookings(prev => reset ? data.bookings : [...prev, ...data.bookings]);
                setTotal(data.total);
                setHasMore(data.bookings.length === 10);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    }, [page, categoryFilter]);

    useEffect(() => {
        if (isAdmin) {
            fetchBookings(true);
            setPage(1);
        }
    }, [isAdmin, fetchBookings]);

    // Refetch when a new booking is created (e.g. via voice) so Booked Ride list updates immediately
    useEffect(() => {
        if (isAdmin && refreshKey > 0) {
            fetchBookings(true);
            setPage(1);
        }
    }, [refreshKey, isAdmin, fetchBookings]);

    const handlePinSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Changed dashboard pin to 123 as per user request
        if (pin === '123') {
            setIsAdmin(true);
            setError('');
        } else {
            setError('Invalid Access PIN');
            setPin('');
        }
    };

    const loadMore = () => {
        fetchBookings();
        setPage(prev => prev + 1);
    };

    if (!isAdmin) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px] p-6">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="w-full max-w-md p-8 bg-slate-900/60 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-2xl relative overflow-hidden"
                >
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500 to-transparent" />
                    <div className="flex flex-col items-center gap-6">
                        <div className="w-16 h-16 bg-cyan-500/10 rounded-full flex items-center justify-center border border-cyan-500/20">
                            <Lock className="w-8 h-8 text-cyan-500" />
                        </div>
                        <div className="text-center">
                            <h2 className="text-2xl font-bold text-white mb-2 tracking-tight">Elite Access</h2>
                            <p className="text-slate-400 text-sm">Enter the administrator PIN to view booked rides.</p>
                        </div>
                        <form onSubmit={handlePinSubmit} className="w-full flex flex-col gap-4">
                            <input
                                type="password"
                                value={pin}
                                onChange={(e) => setPin(e.target.value)}
                                placeholder="Enter PIN"
                                className="w-full bg-slate-800/50 border border-white/10 rounded-2xl py-4 text-center text-2xl tracking-[0.5em] text-cyan-500 focus:outline-none focus:border-cyan-500/50 transition-all placeholder:text-slate-600 placeholder:tracking-normal"
                                autoFocus
                            />
                            {error && <p className="text-red-400 text-xs text-center font-medium">{error}</p>}
                            <button
                                type="submit"
                                className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-4 rounded-2xl transition-all shadow-lg active:scale-95"
                            >
                                Unlock Dashboard
                            </button>
                        </form>
                    </div>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="w-full max-w-7xl mx-auto p-4 md:p-8 space-y-8 mt-16 lg:mt-24">
            {/* Header & Filters */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <h1 className="text-3xl md:text-4xl font-black text-white tracking-tighter uppercase italic flex items-center gap-3">
                        <Shield className="w-8 h-8 text-cyan-500" />
                        Booked <span className="text-cyan-500">Rides</span>
                    </h1>
                    <p className="text-slate-500 text-sm mt-2 font-medium tracking-widest uppercase">Elite Fleet Management Dashboard</p>
                </div>

                <div className="flex items-center gap-4">
                    <div className="relative group">
                        <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-cyan-500 transition-colors" />
                        <select
                            value={categoryFilter}
                            onChange={(e) => setCategoryFilter(e.target.value)}
                            className="bg-slate-900/50 border border-white/10 rounded-2xl pl-12 pr-10 py-3 text-sm text-white focus:outline-none focus:border-cyan-500/50 appearance-none cursor-pointer transition-all"
                        >
                            <option value="">All Categories</option>
                            <option value="Economy">Economy</option>
                            <option value="Sedan">Sedan</option>
                            <option value="SUV">SUV</option>
                            <option value="Luxury">Luxury</option>
                        </select>
                        <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
                    </div>
                </div>
            </div>

            {/* Bookings Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <AnimatePresence>
                    {bookings.map((booking, idx) => (
                        <motion.div
                            key={booking.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: idx * 0.05 }}
                            className="group relative p-6 bg-slate-900/40 backdrop-blur-xl border border-white/5 rounded-3xl hover:border-cyan-500/30 transition-all shadow-xl hover:shadow-cyan-500/5 overflow-hidden"
                        >
                            {/* Card Header */}
                            <div className="flex justify-between items-start mb-6">
                                <div className="p-3 bg-cyan-500/10 rounded-2xl border border-cyan-500/20 group-hover:scale-110 transition-transform">
                                    <Car className="w-6 h-6 text-cyan-500" />
                                </div>
                                <span className="px-3 py-1 bg-slate-800/80 rounded-full text-[10px] font-black text-cyan-400 border border-white/5 tracking-tighter uppercase">
                                    RB-{booking.id}
                                </span>
                            </div>

                            {/* Booking Info */}
                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center">
                                        <User className="w-4 h-4 text-slate-400" />
                                    </div>
                                    <div>
                                        <h3 className="text-white font-bold text-sm">{booking.customerName}</h3>
                                        <div className="flex items-center gap-1.5 text-slate-500 text-[11px]">
                                            <Phone className="w-3 h-3" />
                                            <span>{booking.customerPhone}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="h-[1px] w-full bg-white/5" />

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1">
                                        <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Category</p>
                                        <p className="text-xs text-white font-medium">{booking.carCategory}</p>
                                    </div>
                                    <div className="space-y-1">
                                        <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Duration</p>
                                        <p className="text-xs text-cyan-400 font-bold italic">{booking.duration}</p>
                                    </div>
                                </div>

                                <div className="space-y-3 pt-2">
                                    <div className="flex items-start gap-3">
                                        <div className="mt-1 w-2 h-2 rounded-full bg-cyan-500 ring-4 ring-cyan-500/20" />
                                        <div>
                                            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Pickup</p>
                                            <p className="text-[12px] text-white/90 font-medium">{booking.pickupDateTime}</p>
                                            <p className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1">
                                                <MapPin className="w-3 h-3" /> {booking.pickupLocation}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-start gap-3">
                                        <div className="mt-1 w-2 h-2 rounded-full bg-slate-700 ring-4 ring-slate-700/20" />
                                        <div>
                                            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Return</p>
                                            <p className="text-[12px] text-white/90 font-medium">{booking.returnDateTime}</p>
                                            <p className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1">
                                                <MapPin className="w-3 h-3" /> {booking.dropoffLocation}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Subtle background glow */}
                            <div className="absolute -bottom-10 -right-10 w-24 h-24 bg-cyan-500/10 blur-[40px] rounded-full pointer-events-none group-hover:bg-cyan-500/20 transition-all" />
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {loading && (
                <div className="flex justify-center py-12">
                    <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
                </div>
            )}

            {hasMore && !loading && (
                <div className="flex justify-center">
                    <button
                        onClick={loadMore}
                        className="px-12 py-4 bg-slate-900/50 hover:bg-slate-800/80 border border-white/10 rounded-2xl text-white font-bold text-sm tracking-widest uppercase transition-all shadow-xl active:scale-95 hover:border-cyan-500/20"
                    >
                        Load More Bookings
                    </button>
                </div>
            )}

            {!loading && bookings.length === 0 && (
                <div className="text-center py-24 bg-slate-900/20 rounded-3xl border border-dashed border-white/5">
                    <Search className="w-12 h-12 text-slate-700 mx-auto mb-4" />
                    <p className="text-slate-500 text-sm font-medium">No confirmed rides found matching filters.</p>
                </div>
            )}

            <div className="pt-8 text-center text-[10px] text-slate-600 font-bold tracking-[0.4em] uppercase">
                End of Fleet Records • {total} Total Bookings
            </div>
        </div>
    );
};
