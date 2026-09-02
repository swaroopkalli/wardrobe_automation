"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Environment, ContactShadows, Float } from "@react-three/drei";
import { WardrobeItem } from "@/lib/api";
import { useRef } from "react";
import * as THREE from "three";

interface AvatarViewerProps {
  outfit: WardrobeItem[] | null;
  selectedItem?: WardrobeItem | null;
}

// Simple procedural avatar
function PlaceholderAvatar({ outfit, selectedItem }: { outfit: WardrobeItem[] | null; selectedItem?: WardrobeItem | null }) {
  const groupRef = useRef<THREE.Group>(null);

  const normalize = (value?: string) => (value ?? '').toLowerCase();
  const matchesTypeOrCategory = (item: WardrobeItem, values: string[]) => {
    const haystacks = [normalize(item.type), normalize(item.category)];
    return values.some((value) => haystacks.some((haystack) => haystack.includes(value)));
  };

  const effectiveOutfit = selectedItem
    ? [selectedItem, ...(outfit ?? []).filter((item) => item.id !== selectedItem.id)]
    : outfit;

  const top = effectiveOutfit?.find((item) => matchesTypeOrCategory(item, ['shirt', 'top', 'tee', 't-shirt', 'polo', 'blouse']));
  const bottom = effectiveOutfit?.find((item) => matchesTypeOrCategory(item, ['pants', 'trousers', 'jeans', 'shorts', 'bottom', 'skirt']));
  const footwear = effectiveOutfit?.find((item) => matchesTypeOrCategory(item, ['shoes', 'sneakers', 'boots', 'loafers', 'footwear']));
  const layer = effectiveOutfit?.find((item) => matchesTypeOrCategory(item, ['layer', 'jacket', 'blazer', 'coat', 'cardigan', 'outerwear']));
  const accessory = effectiveOutfit?.find((item) => matchesTypeOrCategory(item, ['watch', 'accessory', 'cap', 'hat', 'belt']));

  const skinColor = "#f5d0b5";
  const getHex = (item?: WardrobeItem) => {
    if (!item) return null;
    return `rgb(${item.reds}, ${item.green}, ${item.blue})`;
  };

  const shirtColor = getHex(top) || "#ffffff";
  const pantsColor = getHex(bottom) || "#333333";
  const shoesColor = getHex(footwear) || "#111111";
  const jacketColor = getHex(layer);
  const accessoryColor = getHex(accessory) || "#c4b5fd";

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

      {/* Torso / Top */}
      <mesh position={[0, 2.0, 0]}>
        <boxGeometry args={[0.9, 1.4, 0.5]} />
        <meshStandardMaterial color={shirtColor} roughness={0.7} />
      </mesh>

      {/* Layer / outerwear */}
      {jacketColor && (
        <mesh position={[0, 2.05, 0]}>
          <boxGeometry args={[0.95, 1.5, 0.55]} />
          <meshStandardMaterial color={jacketColor} roughness={0.8} />
        </mesh>
      )}

      {/* Accessory (watch / cap / belt) */}
      {accessory && (
        <mesh position={[0.55, 1.8, 0.08]} rotation={[0, 0, -0.6]}>
          <boxGeometry args={[0.12, 0.08, 0.14]} />
          <meshStandardMaterial color={accessoryColor} roughness={0.5} />
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

export default function AvatarViewer({ outfit, selectedItem }: AvatarViewerProps) {
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
        <PlaceholderAvatar outfit={outfit} selectedItem={selectedItem} />
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
