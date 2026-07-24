import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ASSET_TYPE_LABELS } from "@/api/assets";
import { searchGlobal } from "@/api/search";

export function GlobalSearch() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query.trim()), 300);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const { data } = useQuery({
    queryKey: ["global-search", debouncedQuery],
    queryFn: () => searchGlobal(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
  });

  const results = data?.results ?? [];

  function handleSelect(assetId: string) {
    setIsOpen(false);
    setQuery("");
    navigate(`/inventory/${assetId}`);
  }

  return (
    <div ref={containerRef} className="relative w-72">
      <input
        value={query}
        onChange={(event) => {
          setQuery(event.target.value);
          setIsOpen(true);
        }}
        onFocus={() => setIsOpen(true)}
        placeholder="Buscar ativos..."
        className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
      />
      {isOpen && debouncedQuery.length >= 2 && (
        <div className="absolute z-10 mt-1 w-full rounded-md border border-slate-200 bg-white shadow-lg">
          {results.length === 0 ? (
            <p className="px-3 py-2 text-sm text-slate-500">Nenhum resultado.</p>
          ) : (
            <ul className="max-h-72 overflow-y-auto py-1">
              {results.map((asset) => (
                <li key={asset.id}>
                  <button
                    onClick={() => handleSelect(asset.id)}
                    className="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-slate-50"
                  >
                    <span className="font-medium text-slate-900">{asset.name}</span>
                    <span className="text-xs text-slate-400">
                      {ASSET_TYPE_LABELS[asset.asset_type]}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
