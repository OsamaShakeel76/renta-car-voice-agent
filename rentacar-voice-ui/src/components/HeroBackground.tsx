import { motion } from 'framer-motion';
import type { RootState } from '@react-three/fiber';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import { useRef, useState } from 'react';

const ParticleField = () => {
    const ref = useRef<any>(null);
    const [sphere] = useState(() => {
        const coords = new Float32Array(2000 * 3);
        for (let i = 0; i < 2000; i++) {
            const theta = 2 * Math.PI * Math.random();
            const phi = Math.acos(2 * Math.random() - 1);
            const x = 1.5 * Math.sin(phi) * Math.cos(theta);
            const y = 1.5 * Math.sin(phi) * Math.sin(theta);
            const z = 1.5 * Math.cos(phi);
            coords.set([x, y, z], i * 3);
        }
        return coords;
    });

    useFrame((_state: RootState, delta: number) => {
        if (ref.current) {
            ref.current.rotation.x -= delta / 10;
            ref.current.rotation.y -= delta / 15;
        }
    });

    return (
        <group rotation={[0, 0, Math.PI / 4]}>
            <Points ref={ref} positions={sphere} stride={3} frustumCulled={false}>
                <PointMaterial
                    transparent
                    color="#06b6d4"
                    size={0.005}
                    sizeAttenuation={true}
                    depthWrite={false}
                />
            </Points>
        </group>
    );
};

export const HeroBackground = () => {
    return (
        <div className="fixed inset-0 -z-10 bg-luxury-navy">
            <div className="absolute inset-0 z-0 opacity-40">
                <Canvas camera={{ position: [0, 0, 1] }}>
                    <ParticleField />
                </Canvas>
            </div>

            {/* Light Streaks (Car Headlight Vibe) */}
            <div className="absolute inset-0 overflow-hidden">
                {[...Array(3)].map((_, i) => (
                    <motion.div
                        key={i}
                        initial={{ left: '-100%', top: `${30 + i * 20}%` }}
                        animate={{ left: '200%' }}
                        transition={{
                            duration: 3 + i,
                            repeat: Infinity,
                            ease: "circIn",
                            delay: i * 2
                        }}
                        className="absolute h-[1px] w-[600px] bg-gradient-to-r from-transparent via-cyan-400/30 to-transparent blur-[2px]"
                    />
                ))}
            </div>

            {/* Decorative Glows */}
            <div className="absolute top-0 -left-1/4 w-1/2 h-1/2 bg-cyan-500/10 blur-[120px] rounded-full" />
            <div className="absolute bottom-0 -right-1/4 w-1/2 h-1/2 bg-blue-600/10 blur-[120px] rounded-full" />

            {/* Final Polish Layers */}
            <div className="absolute inset-0 bg-gradient-to-b from-luxury-navy/20 via-transparent to-luxury-navy" />
            <div className="absolute inset-0 opacity-[0.03] bg-[url('https://grainy-gradients.vercel.app/noise.svg')] pointer-events-none" />
        </div>
    );
};
