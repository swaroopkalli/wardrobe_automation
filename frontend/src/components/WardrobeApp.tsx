"use client";

import { useState, useEffect } from "react";
import { api, WardrobeItem, RecommendationResponse } from "@/lib/api";
import { Shirt, CheckCircle, RefreshCcw, Layers } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import AvatarViewer from "./3d/AvatarViewer";
import InteractiveParticleField from "./effects/InteractiveParticleField";

export default function WardrobeApp() {
  const [items, setItems] = useState<WardrobeItem[]>([]);
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [recommending, setRecommending] = useState(false);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selectedItem = items.find((item) => item.id === selectedItemId) ?? null;
  const avatarOutfit = selectedItem
    ? [selectedItem, ...(recommendation?.outfit ?? []).filter((item) => item.id !== selectedItem.id)]
    : recommendation?.outfit ?? null;

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      setError(null);
      const data = await api.getWardrobeItems();
      setItems(data);
    } catch (err) {
      console.error(err);
      setError('Unable to load wardrobe items from the API.');
    } finally {
      setLoading(false);
    }
  };

  const getRecommendation = async () => {
    setRecommending(true);
    setError(null);
    try {
      const availableTypes = [...new Set(items.map((item) => item.type).filter(Boolean))];
      const requestedTypes = availableTypes.length ? availableTypes.slice(0, 6) : undefined;

      const data = await api.getRecommendation({
        strategy: "best",
        required_types: requestedTypes,
      });
      setRecommendation(data);
    } catch (err) {
      console.error(err);
      setError('Recommendation request failed. Please try again.');
    } finally {
      setRecommending(false);
    }
  };

  return (
    <div className="flex h-screen flex-col md:flex-row overflow-hidden bg-gradient-to-br from-slate-900 via-slate-950 to-black text-slate-100 relative">

      {/* GLOBAL PARTICLE FIELD — behind all panels, pointer-events:none */}
      <InteractiveParticleField
        density={0.28}
        hue={240}
        hueAlt={270}
        repelRadius={130}
        repelStrength={55}
        springK={0.045}
        friction={0.84}
      />
      
      {/* LEFT PANEL - UI Controls */}
      <div className="w-full md:w-1/3 flex flex-col h-full border-r border-white/10 bg-white/5 backdrop-blur-xl p-6 relative z-10">
        
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
              Wardrobe AI
            </h1>
            <p className="text-xs text-slate-400">Stage 3 - Next.js & 3D Avatar</p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto pr-2 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
          
          <section>
            <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-4">Actions</h2>
            <button
              onClick={getRecommendation}
              disabled={recommending || loading || items.length === 0}
              className="w-full relative overflow-hidden group rounded-xl p-4 transition-all duration-300 hover:scale-[1.02] active:scale-95 disabled:opacity-50"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-600 opacity-80 group-hover:opacity-100 transition-opacity" />
              <div className="relative flex items-center justify-center gap-2 font-medium">
                {recommending ? (
                  <RefreshCcw className="w-5 h-5 animate-spin" />
                ) : (
                  <CheckCircle className="w-5 h-5" />
                )}
                {recommending ? "Generating Outfit..." : "Recommend Best Outfit"}
              </div>
            </button>
            {error && (
              <p className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-200">{error}</p>
            )}
          </section>

          <AnimatePresence mode="popLayout">
            {recommendation && recommendation.outfit && (
              <motion.section
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-white/5 border border-white/10 rounded-2xl p-5"
              >
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-semibold tracking-wider text-purple-400 uppercase">
                    Your Outfit
                  </h2>
                  <span className="text-xs px-2 py-1 bg-purple-500/20 text-purple-300 rounded-md">
                    Score: {recommendation.score?.toFixed(2)}
                  </span>
                </div>
                
                <div className="space-y-3">
                  {recommendation.outfit.map((item) => (
                    <div key={item.id} className="flex items-center gap-3 p-3 rounded-xl bg-black/40 border border-white/5">
                      <div 
                        className="w-8 h-8 rounded-full border border-white/20 shadow-sm"
                        style={{ backgroundColor: `rgb(${item.reds}, ${item.green}, ${item.blue})` }}
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium">{item.item_name}</p>
                        <p className="text-xs text-slate-500 capitalize">{item.type}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.section>
            )}
          </AnimatePresence>

          <section>
            <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-4 flex items-center justify-between">
              Wardrobe ({items.length})
            </h2>
            {loading ? (
              <div className="flex items-center justify-center p-8">
                <RefreshCcw className="w-6 h-6 animate-spin text-slate-500" />
              </div>
            ) : items.length === 0 ? (
              <div className="rounded-xl border border-dashed border-white/10 bg-white/5 p-6 text-center text-sm text-slate-400">
                No wardrobe items are available yet.
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {items.map((item) => {
                  const isSelected = selectedItemId === item.id;

                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setSelectedItemId((current) => (current === item.id ? null : item.id))}
                      className={`p-3 rounded-xl border flex flex-col gap-2 transition-all cursor-pointer group text-left ${
                        isSelected
                          ? 'bg-indigo-500/20 border-indigo-400/60 ring-1 ring-indigo-400/60 shadow-lg shadow-indigo-500/10'
                          : 'bg-white/5 border-white/5 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <Shirt className={`w-4 h-4 transition-colors ${isSelected ? 'text-indigo-200' : 'text-slate-400 group-hover:text-white'}`} />
                        <div 
                          className="w-3 h-3 rounded-full border border-white/20"
                          style={{ backgroundColor: `rgb(${item.reds}, ${item.green}, ${item.blue})` }}
                        />
                      </div>
                      <div>
                        <p className="text-xs font-medium truncate" title={item.item_name}>{item.item_name}</p>
                        <p className="text-[10px] text-slate-500 capitalize">{item.type}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </section>

        </div>
      </div>

      {/* RIGHT PANEL - 3D Viewer */}
      <div className="w-full md:w-2/3 h-full relative z-10 bg-black">
        {/* Subtle background glow */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.15),transparent_50%)]" />
        
        <AvatarViewer outfit={avatarOutfit} selectedItem={selectedItem} />
        
        <div className="absolute bottom-6 left-6 right-6 flex justify-center pointer-events-none">
          <div className="bg-black/50 backdrop-blur-md border border-white/10 text-white/60 text-xs px-4 py-2 rounded-full pointer-events-auto">
            Drag to rotate • Scroll to zoom
          </div>
        </div>
      </div>

    </div>
  );
}
