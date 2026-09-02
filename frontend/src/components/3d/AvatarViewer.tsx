"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Environment, ContactShadows, Float } from "@react-three/drei";
import { WardrobeItem } from "@/lib/api";
import { useRef } from "react";
import * as THREE from "three";

interface AvatarViewerProps {
  outfit: WardrobeItem[] | null;
}

// Simple procedural avatar
function PlaceholderAvatar({ outfit }: { outfit: WardrobeItem[] | null }) {
  const groupRef = useRef<THREE.Group>(null);

  // Parse outfit colors
  const shirt = outfit?.find(i => i.type === 'shirt');
  const pants = outfit?.find(i => i.type === 'pants');
  const shoes = outfit?.find(i => i.type === 'shoes');
  const jacket = outfit?.find(i => i.type === 'jacket' || i.category?.includes('outerwear'));

  const skinColor = "#f5d0b5";
  const getHex = (item?: WardrobeItem) => {
    if (!item) return null;
    return `rgb(${item.reds}, ${item.green}, ${item.blue})`;
  };

  const shirtColor = getHex(shirt) || "#ffffff";
  const pantsColor = getHex(pants) || "#333333";
  const shoesColor = getHex(shoes) || "#111111";
  const jacketColor = getHex(jacket);

  // Subtle breathing animation
  useFrame((state) => {
    if (groupRef.current) {
      const t = state.clock.getElapsedTime();
      groupRef.current.position.y = Math.sin(t * 2) * 0.02;
    }
  });

  return (
    <group ref={groupRef} position={[0, -1.5, 0]}>
      {/* Head */}
      <mesh position={[0, 3.2, 0]}>
        <sphereGeometry args={[0.3, 32, 32]} />
        <meshStandardMaterial color={skinColor} roughness={0.4} />
      </mesh>

      {/* Neck */}
      <mesh position={[0, 2.8, 0]}>
        <cylinderGeometry args={[0.1, 0.1, 0.3, 16]} />
        <meshStandardMaterial color={skinColor} roughness={0.4} />
      </mesh>

      {/* Torso / Shirt */}
      <mesh position={[0, 2.0, 0]}>
        <boxGeometry args={[0.9, 1.4, 0.5]} />
        <meshStandardMaterial color={shirtColor} roughness={0.7} />
      </mesh>

      {/* Jacket Layer (slightly larger than torso if present) */}
      {jacketColor && (
        <mesh position={[0, 2.05, 0]}>
          <boxGeometry args={[0.95, 1.5, 0.55]} />
          <meshStandardMaterial color={jacketColor} roughness={0.8} />
        </mesh>
      )}

      {/* Arms */}
      <mesh position={[-0.6, 2.0, 0]} rotation={[0, 0, 0.1]}>
        <cylinderGeometry args={[0.15, 0.12, 1.3]} />
        <meshStandardMaterial color={jacketColor || shirtColor} roughness={0.7} />
      </mesh>
      <mesh position={[0.6, 2.0, 0]} rotation={[0, 0, -0.1]}>
        <cylinderGeometry args={[0.15, 0.12, 1.3]} />
        <meshStandardMaterial color={jacketColor || shirtColor} roughness={0.7} />
      </mesh>

      {/* Legs / Pants */}
      <mesh position={[-0.25, 0.7, 0]}>
        <cylinderGeometry args={[0.2, 0.15, 1.4]} />
        <meshStandardMaterial color={pantsColor} roughness={0.8} />
      </mesh>
      <mesh position={[0.25, 0.7, 0]}>
        <cylinderGeometry args={[0.2, 0.15, 1.4]} />
        <meshStandardMaterial color={pantsColor} roughness={0.8} />
      </mesh>

      {/* Shoes */}
      <mesh position={[-0.25, 0.05, 0.05]}>
        <boxGeometry args={[0.25, 0.15, 0.4]} />
        <meshStandardMaterial color={shoesColor} roughness={0.5} />
      </mesh>
      <mesh position={[0.25, 0.05, 0.05]}>
        <boxGeometry args={[0.25, 0.15, 0.4]} />
        <meshStandardMaterial color={shoesColor} roughness={0.5} />
      </mesh>
    </group>
  );
}

export default function AvatarViewer({ outfit }: AvatarViewerProps) {
  return (
    <Canvas
      camera={{ position: [0, 1, 5], fov: 50 }}
      className="w-full h-full"
    >
      <color attach="background" args={["#000000"]} />
      
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} intensity={1} castShadow />
      <pointLight position={[-5, 5, -5]} intensity={0.5} color="#6366f1" />
      
      <Environment preset="city" />

      <Float speed={1.5} rotationIntensity={0.1} floatIntensity={0.1}>
        <PlaceholderAvatar outfit={outfit} />
      </Float>

      <ContactShadows 
        position={[0, -1.5, 0]} 
        opacity={0.5} 
        scale={5} 
        blur={2} 
        far={2} 
      />

      <OrbitControls 
        enablePan={false}
        minDistance={3}
        maxDistance={8}
        maxPolarAngle={Math.PI / 2 + 0.1}
        target={[0, 0, 0]}
      />
    </Canvas>
  );
}
