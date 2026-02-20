import { useState, useEffect } from 'react';
import {
    format,
    addMonths,
    subMonths,
    startOfMonth,
    endOfMonth,
    startOfWeek,
    endOfWeek,
    isSameMonth,
    isSameDay,
    addDays,
    parseISO,
    isWithinInterval
} from 'date-fns';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Clock, User, MapPin } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Booking {
    bookingReference: string;
    fullName: string;
    phoneNumber: string;
    pickupDateTime: string;
    returnDateTime: string;
    pickupLocation: string;
    dropoffLocation: string;
    carCategory: string;
    status: string;
}

export const BookingCalendar = ({ refreshKey }: { refreshKey?: number }) => {
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [bookings, setBookings] = useState<Booking[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);

    useEffect(() => {
        fetchBookings();
    }, [refreshKey]);

    const fetchBookings = async () => {
        try {
            const response = await fetch('/api/get-all-bookings');
            const data = await response.json();
            if (data.success) {
                setBookings(data.bookings);
            }
        } catch (error) {
            console.error('Error fetching bookings:', error);
        } finally {
            setLoading(false);
        }
    };

    const renderHeader = () => {
        return (
            <div className="flex items-center justify-between px-4 py-6">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-cyan-500/10 rounded-lg">
                        <CalendarIcon className="w-5 h-5 text-cyan-400" />
                    </div>
                    <h2 className="text-xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent italic">
                        {format(currentMonth, 'MMMM yyyy')}
                    </h2>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
                        className="p-2 hover:bg-white/5 rounded-full transition-colors text-slate-400 hover:text-white"
                    >
                        <ChevronLeft className="w-5 h-5" />
                    </button>
                    <button
                        onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
                        className="p-2 hover:bg-white/5 rounded-full transition-colors text-slate-400 hover:text-white"
                    >
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>
            </div>
        );
    };

    const renderDays = () => {
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        return (
            <div className="grid grid-cols-7 mb-2">
                {days.map((day) => (
                    <div key={day} className="text-center text-[10px] uppercase tracking-widest font-bold text-slate-500 py-2">
                        {day}
                    </div>
                ))}
            </div>
        );
    };

    const renderCells = () => {
        const monthStart = startOfMonth(currentMonth);
        const monthEnd = endOfMonth(monthStart);
        const startDate = startOfWeek(monthStart);
        const endDate = endOfWeek(monthEnd);

        const rows = [];
        let days = [];
        let day = startDate;
        let formattedDate = "";

        while (day <= endDate) {
            for (let i = 0; i < 7; i++) {
                formattedDate = format(day, "d");
                const cloneDay = day;

                // Find bookings on this day
                const dayBookings = bookings.filter(b => {
                    const start = parseISO(b.pickupDateTime.replace(' ', 'T'));
                    const end = parseISO(b.returnDateTime.replace(' ', 'T'));
                    return isSameDay(cloneDay, start) || isSameDay(cloneDay, end) ||
                        isWithinInterval(cloneDay, { start, end });
                });

                days.push(
                    <div
                        key={day.toString()}
                        className={`relative min-h-[80px] border border-white/5 p-2 transition-all group ${!isSameMonth(day, monthStart) ? "opacity-20" : "opacity-100"
                            } ${isSameDay(day, new Date()) ? "bg-cyan-500/5" : "hover:bg-white/5"}`}
                    >
                        <span className={`text-sm font-medium ${isSameDay(day, new Date()) ? "text-cyan-400" : "text-slate-400"}`}>
                            {formattedDate}
                        </span>

                        <div className="mt-1 flex flex-col gap-1">
                            {dayBookings.map((booking, idx) => (
                                <motion.div
                                    initial={{ opacity: 0, x: -5 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    key={booking.bookingReference + idx}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setSelectedBooking(booking);
                                    }}
                                    className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 truncate cursor-pointer hover:bg-cyan-500/30 transition-colors"
                                >
                                    {booking.carCategory} - {booking.fullName.split(' ')[0]}
                                </motion.div>
                            ))}
                        </div>

                        {isSameDay(day, new Date()) && (
                            <div className="absolute top-0 right-0 w-1 h-1 bg-cyan-400 rounded-full m-2 shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
                        )}
                    </div>
                );
                day = addDays(day, 1);
            }
            rows.push(
                <div className="grid grid-cols-7" key={day.toString()}>
                    {days}
                </div>
            );
            days = [];
        }
        return <div className="border-t border-l border-white/5">{rows}</div>;
    };

    return (
        <div className="glass-panel overflow-hidden border border-white/10 backdrop-blur-xl bg-slate-900/40 rounded-3xl">
            {renderHeader()}
            <div className="px-4 pb-4">
                {renderDays()}
                {loading ? (
                    <div className="h-[400px] flex items-center justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400" />
                    </div>
                ) : (
                    renderCells()
                )}
            </div>

            {/* Booking Detail Modal */}
            <AnimatePresence>
                {selectedBooking && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
                        onClick={() => setSelectedBooking(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="w-full max-w-md glass-panel p-8 bg-slate-900 border border-white/20 rounded-3xl shadow-2xl"
                            onClick={e => e.stopPropagation()}
                        >
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <h3 className="text-2xl font-bold text-white mb-1">{selectedBooking.carCategory} Elite</h3>
                                    <p className="text-cyan-400 text-xs tracking-widest uppercase font-bold">Booking Details</p>
                                </div>
                                <div className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-400 text-[10px] font-bold border border-cyan-500/30 italic">
                                    Confirmed
                                </div>
                            </div>

                            <div className="space-y-6">
                                <div className="flex items-center gap-4 group">
                                    <div className="p-3 bg-white/5 rounded-2xl group-hover:bg-cyan-500/10 transition-colors">
                                        <User className="w-5 h-5 text-slate-400 group-hover:text-cyan-400" />
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Customer</p>
                                        <p className="text-white font-medium">{selectedBooking.fullName}</p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-4 group">
                                    <div className="p-3 bg-white/5 rounded-2xl group-hover:bg-cyan-500/10 transition-colors">
                                        <Clock className="w-5 h-5 text-slate-400 group-hover:text-cyan-400" />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Duration</p>
                                        <div className="flex items-center gap-2">
                                            <span className="text-white text-sm">{selectedBooking.pickupDateTime}</span>
                                            <span className="text-slate-600">→</span>
                                            <span className="text-white text-sm">{selectedBooking.returnDateTime}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-4 group">
                                    <div className="p-3 bg-white/5 rounded-2xl group-hover:bg-cyan-500/10 transition-colors">
                                        <MapPin className="w-5 h-5 text-slate-400 group-hover:text-cyan-400" />
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Location</p>
                                        <p className="text-white text-sm">Pickup: {selectedBooking.pickupLocation}</p>
                                        <p className="text-white text-sm">Dropoff: {selectedBooking.dropoffLocation}</p>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={() => setSelectedBooking(null)}
                                className="w-full mt-8 py-4 bg-white/5 hover:bg-white/10 text-white rounded-2xl border border-white/10 transition-all font-bold tracking-widest text-xs uppercase"
                            >
                                Close Details
                            </button>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
