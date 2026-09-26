"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import Image from "next/image";
import {
  getProductScorecard,
  Product,
  HealthScorecard,
  ProductScoreResponse,
  HealthySwap,
} from "@/lib/api";
import { useProfile } from "./ProfileProvider";

interface ProductScannerProps {
  onClose?: () => void;
  initialBarcode?: number | null;
}

export function ProductScanner({ onClose, initialBarcode }: ProductScannerProps) {
  const { profile } = useProfile();
  const [activeBarcode, setActiveBarcode] = useState<number | null>(initialBarcode || null);
  const [inputBarcode, setInputBarcode] = useState(initialBarcode ? String(initialBarcode) : "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ProductScoreResponse | null>(null);

  // Camera scanner states
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [hasBarcodeDetector, setHasBarcodeDetector] = useState(false);
  const [hasCameraDevice, setHasCameraDevice] = useState<boolean | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [imageUploading, setImageUploading] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const scanIntervalRef = useRef<number | null>(null);

  // Check BarcodeDetector & videoinput device support
  useEffect(() => {
    if (typeof window !== "undefined") {
      if ("BarcodeDetector" in window) {
        setHasBarcodeDetector(true);
      }
      if (navigator?.mediaDevices?.enumerateDevices) {
        navigator.mediaDevices
          .enumerateDevices()
          .then(devices => {
            const hasVideo = devices.some(d => d.kind === "videoinput");
            setHasCameraDevice(hasVideo);
          })
          .catch(() => {
            setHasCameraDevice(false);
          });
      }
    }
  }, []);

  // Fetch product score
  const fetchScorecard = useCallback(
    async (barcode: number) => {
      setLoading(true);
      setError("");
      try {
        const allergiesStr = profile?.allergies?.join(",") || undefined;
        const exclusionsStr = profile?.exclusions?.join(",") || undefined;
        const dietStr =
          profile?.dietPreference && profile.dietPreference !== "no preference"
            ? profile.dietPreference
            : undefined;

        const data = await getProductScorecard(barcode, {
          allergies: allergiesStr,
          exclusions: exclusionsStr,
          diet: dietStr,
        });
        setResult(data);
        setActiveBarcode(barcode);
        setInputBarcode(String(barcode));

        // Stop camera once scanned successfully
        stopCamera();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Product not found in database.");
        setResult(null);
      } finally {
        setLoading(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [profile]
  );

  // Load initial barcode if provided
  useEffect(() => {
    if (initialBarcode) {
      void fetchScorecard(initialBarcode);
    }
  }, [initialBarcode, fetchScorecard]);

  // Callback ref to reliably attach media stream to video element upon mount
  const attachStreamToVideo = useCallback((node: HTMLVideoElement | null) => {
    videoRef.current = node;
    if (node && streamRef.current) {
      node.srcObject = streamRef.current;
      node.onloadedmetadata = () => {
        node.play().catch(() => {});
      };
    }
  }, []);

  // Start HTML5 camera stream with robust device fallback
  async function startCamera() {
    setCameraError("");
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Camera API is not supported in this browser. Please use manual barcode lookup below.");
      }

      let stream: MediaStream;
      try {
        // Ideal environment/rear camera (for mobile / tablets)
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 } },
        });
      } catch {
        // Resilient fallback for desktop/laptop webcams without "environment" camera
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
      }

      streamRef.current = stream;
      setIsCameraActive(true);

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play().catch(() => {});
        };
      }

      // If native BarcodeDetector is available, scan continuously
      if (typeof window !== "undefined" && "BarcodeDetector" in window) {
        try {
          const detector = new (window as any).BarcodeDetector({
            formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128"],
          });

          scanIntervalRef.current = window.setInterval(async () => {
            if (videoRef.current && videoRef.current.readyState >= 2) {
              try {
                const barcodes = await detector.detect(videoRef.current);
                if (barcodes && barcodes.length > 0) {
                  const detectedVal = barcodes[0].rawValue;
                  const numericCode = parseInt(detectedVal.replace(/\D/g, ""), 10);
                  if (numericCode && String(numericCode).length >= 8) {
                    stopCamera();
                    void fetchScorecard(numericCode);
                  }
                }
              } catch (_) {
                // Ignore transient frame decoding errors
              }
            }
          }, 400);
        } catch {}
      }
    } catch (e: any) {
      console.warn("Camera start warning:", e);
      const isNotFound =
        e?.name === "NotFoundError" ||
        String(e?.message).toLowerCase().includes("not found");
      if (isNotFound) {
        setHasCameraDevice(false);
        setCameraError(
          "No physical webcam detected on this machine. You can upload an image of a food label/barcode or enter the barcode manually."
        );
      } else {
        setCameraError(
          e instanceof Error
            ? `${e.message} (You can also upload a photo or enter the barcode manually.)`
            : "Unable to access camera."
        );
      }
      setIsCameraActive(false);
    }
  }

  // Handle image upload for barcode extraction
  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageUploading(true);
    setCameraError("");

    try {
      if (typeof window !== "undefined" && "BarcodeDetector" in window) {
        try {
          const detector = new (window as any).BarcodeDetector({
            formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128"],
          });
          const bitmap = await createImageBitmap(file);
          const barcodes = await detector.detect(bitmap);
          if (barcodes && barcodes.length > 0) {
            const detectedVal = barcodes[0].rawValue;
            const numericCode = parseInt(detectedVal.replace(/\D/g, ""), 10);
            if (numericCode && String(numericCode).length >= 8) {
              void fetchScorecard(numericCode);
              setImageUploading(false);
              return;
            }
          }
        } catch {}
      }

      setCameraError(
        "Could not read a clear barcode from the image. Please enter the barcode number."
      );
    } catch {
      setCameraError("Could not process image. Please enter the barcode number.");
    } finally {
      setImageUploading(false);
    }
  }

  function stopCamera() {
    if (scanIntervalRef.current) {
      window.clearInterval(scanIntervalRef.current);
      scanIntervalRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  }

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  function handleManualSubmit(e: React.FormEvent) {
    e.preventDefault();
    const clean = inputBarcode.trim().replace(/\D/g, "");
    if (!clean) return;
    void fetchScorecard(parseInt(clean, 10));
  }

  const gradeColor = result?.scorecard ? getGradeColor(result.scorecard.grade) : "#888";

  return (
    <div className="product-scanner-backdrop" onClick={onClose}>
      <div className="product-scanner-modal" onClick={e => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="product-scanner-header">
          <div>
            <div className="badge-line">
              <span className="pill pill-green">Jivanya Health Score</span>
              <span className="pill pill-warm">Healthy Swaps</span>
            </div>
            <h3>Packaged Food Health Scorecard</h3>
            <p>Scan a barcode to look up a real product record and compare its stored nutrition values.</p>
          </div>
          {onClose && (
            <button
              type="button"
              className="outline-link close-button"
              onClick={() => {
                stopCamera();
                onClose();
              }}
              aria-label="Close Scanner"
            >
              Close ×
            </button>
          )}
        </div>

        {/* Scanner & Input Toolbar */}
        <div className="scanner-toolbar-section">
          {isCameraActive ? (
            <div className="camera-viewport-container">
              <video ref={attachStreamToVideo} className="camera-video-feed" playsInline muted />
              <div className="camera-targeting-box">
                <div className="targeting-reticle" />
                <div className="targeting-beam" />
                <span className="targeting-instruction">Align barcode inside frame</span>
              </div>
              <button type="button" className="button button-light button-small camera-stop-btn" onClick={stopCamera}>
                ✕ Close Camera
              </button>
            </div>
          ) : (
            <div className="camera-start-row">
              {hasCameraDevice !== false ? (
                <button
                  type="button"
                  className="button button-primary camera-launch-btn"
                  onClick={startCamera}
                >
                  📷 Open Camera Barcode Scanner
                </button>
              ) : (
                <div className="no-camera-pill">
                  <span>💻 <strong>No physical webcam detected on this device</strong></span>
                </div>
              )}

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={handleImageUpload}
              />
              <button
                type="button"
                className="button button-secondary upload-photo-btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={imageUploading}
              >
                {imageUploading ? "Scanning image…" : "📁 Upload Photo of Barcode"}
              </button>

              <span className="camera-help-text">
                {hasCameraDevice === false
                  ? "Upload a photo or enter the barcode below"
                  : "Point camera at any barcode or upload a photo"}
              </span>
            </div>
          )}

          {cameraError && <div className="scanner-warning-box">{cameraError}</div>}

          {/* Quick Barcode Text Input */}
          <form className="scanner-manual-form" onSubmit={handleManualSubmit}>
            <input
              type="text"
              className="input barcode-input"
              placeholder="Enter EAN barcode (e.g. 8904335601951)"
              value={inputBarcode}
              onChange={e => setInputBarcode(e.target.value)}
            />
            <button
              type="submit"
              className="button button-secondary"
              disabled={loading || !inputBarcode.trim()}
            >
              {loading ? "Analyzing…" : "Lookup"}
            </button>
          </form>

        </div>

        {/* Loading Spinner */}
        {loading && (
          <div className="loading-card-box">
            <div className="loading-row">
              <span />
              <span />
              <span />
            </div>
            <p>Evaluating the deterministic Jivanya score from this product record…</p>
          </div>
        )}

        {/* Error Notification */}
        {error && (
          <div className="scanner-error-card">
            <h4>Product Not in Database</h4>
            <p>{error}</p>
          </div>
        )}

        {/* Scorecard Results View */}
        {result && result.scorecard && (
          <div className="scorecard-content-wrap">
            {/* Top Product Summary Banner */}
            <div className="scorecard-product-header">
              <div className="product-identity">
                {result.product.image_url ? (
                  <div className="product-image-frame" style={{ position: "relative", width: 64, height: 64 }}>
                    <Image
                      src={result.product.image_url}
                      alt={result.product.product_name}
                      fill
                      sizes="64px"
                      className="product-thumb-img"
                      style={{ objectFit: "contain" }}
                      unoptimized
                    />
                  </div>
                ) : (
                  <div className="product-image-fallback">Image unavailable</div>
                )}
                <div>
                  <span className="product-brand-tag">{result.product.brand || "Indian Packaged Food"}</span>
                  <h2 className="product-title">{result.product.product_name}</h2>
                  <span className="product-category-tag">{result.product.category || "General"}</span>
                </div>
              </div>

              {/* Big Score Gauge */}
              <div className="score-gauge-box">
                <div
                  className="score-circular-badge"
                  style={{ borderColor: gradeColor, color: gradeColor }}
                >
                  <span className="score-grade-letter">{result.scorecard.grade}</span>
                  <span className="score-numeric">{result.scorecard.score}/100</span>
                </div>
                <div className="score-label-wrap">
                  <strong style={{ color: gradeColor }}>{result.scorecard.grade_label}</strong>
                  <span className="score-benchmark-text">Jivanya Health Score</span>
                </div>
              </div>
            </div>

            {/* Profile Allergen & Diet Alerts (If Any) */}
            {result.scorecard.profile_warnings.length > 0 && (
              <div className="profile-alert-banner">
                {result.scorecard.profile_warnings.map((warn, i) => (
                  <div key={i} className="profile-alert-item">
                    {warn.message}
                  </div>
                ))}
              </div>
            )}

            {/* Scorecard Summary */}
            <div className="scorecard-summary-card">
              <p>{result.scorecard.summary}</p>
            </div>

            {/* Deterministic product rules and ingredient flags */}
            {result.scorecard.rule_warnings.length > 0 && (
              <div className="hfss-warnings-section">
                <h4>⚠️ Deterministic product flags</h4>
                <div className="hfss-warning-list">
                  {result.scorecard.rule_warnings.map(warning => (
                    <div key={warning.code} className={`hfss-warning-card ${warning.severity}`}>
                      <div className="hfss-warning-title">
                        <span>🔴</span>
                        <strong>{warning.label}</strong>
                      </div>
                      <p>{warning.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Clean Accolades & Positive Highlights */}
            {result.scorecard.clean_highlights.length > 0 && (
              <div className="clean-highlights-section">
                <h4>✨ Clean Nutrition Accolades</h4>
                <div className="clean-highlights-grid">
                  {result.scorecard.clean_highlights.map(item => (
                    <div key={item.code} className="clean-highlight-pill">
                      <span>🟢</span>
                      <div>
                        <strong>{item.label}</strong>
                        <small>{item.description}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Key Nutrition Breakdown Grid */}
            <div className="nutrition-breakdown-section">
              <h4>Nutritional Values (per 100g)</h4>
              <div className="macro-stats-grid">
                <div className="macro-stat-cell">
                  <span>Energy</span>
                  <strong>{result.product.energy_100g ? `${result.product.energy_100g.toFixed(0)} kcal` : "—"}</strong>
                </div>
                <div className={`macro-stat-cell ${(result.product.sugars_100g || 0) > 10 ? "flagged" : ""}`}>
                  <span>Sugars</span>
                  <strong>{result.product.sugars_100g ? `${result.product.sugars_100g.toFixed(1)}g` : "—"}</strong>
                </div>
                <div className={`macro-stat-cell ${(result.product.saturated_fat_100g || 0) > 4 ? "flagged" : ""}`}>
                  <span>Sat. Fat</span>
                  <strong>{result.product.saturated_fat_100g ? `${result.product.saturated_fat_100g.toFixed(1)}g` : "—"}</strong>
                </div>
                <div className="macro-stat-cell">
                  <span>Protein</span>
                  <strong className="stat-green">{result.product.protein_100g ? `${result.product.protein_100g.toFixed(1)}g` : "—"}</strong>
                </div>
                <div className="macro-stat-cell">
                  <span>Fiber</span>
                  <strong className="stat-green">{result.product.fiber_100g ? `${result.product.fiber_100g.toFixed(1)}g` : "—"}</strong>
                </div>
                <div className="macro-stat-cell">
                  <span>Sodium</span>
                  <strong>{result.product.sodium_100g != null ? `${result.product.sodium_100g.toFixed(1)}mg` : "—"}</strong>
                </div>
              </div>
            </div>

            {/* Ingredients Full Text (With Palm Oil / Maida Highlights) */}
            {result.product.ingredients_text && (
              <div className="ingredients-inspect-box">
                <h4>Ingredients List</h4>
                <p className="ingredients-paragraph">
                  {result.product.ingredients_text}
                </p>
                <div className="ingredients-tags-row">
                  {result.scorecard.contains_palm_oil && (
                    <span className="badge-danger">⚠️ Contains Palm Oil / Palmolein</span>
                  )}
                  {result.scorecard.contains_maida && (
                    <span className="badge-warning">⚠️ Contains Refined Maida</span>
                  )}
                </div>
              </div>
            )}

            {/* ✨ HEALTHIER SWAPS RECOMMENDATION ENGINE */}
            <div className="healthy-swaps-section">
              <div className="swaps-section-header">
                <div>
                  <h3>Database alternatives</h3>
                  <p>Higher-scoring alternatives in <strong>{result.product.category || "this category"}</strong>, compared using stored nutrition values.</p>
                </div>
                <span className="pill pill-green">Same Aisle</span>
              </div>

              {result.scorecard.healthy_swaps.length > 0 ? (
                <div className="healthy-swaps-grid">
                  {result.scorecard.healthy_swaps.map((swap: HealthySwap) => {
                    const swapColor = getGradeColor(swap.grade);
                    return (
                      <div key={swap.product.barcode} className="healthy-swap-card">
                        <div className="swap-card-top">
                          <div className="swap-product-info">
                            <span className="swap-brand">{swap.product.brand || "Recommended Alternative"}</span>
                            <h4>{swap.product.product_name}</h4>
                          </div>
                          <div
                            className="swap-grade-badge"
                            style={{ background: swapColor, color: "#fff" }}
                          >
                            {swap.grade}
                            <small>{swap.score}</small>
                          </div>
                        </div>

                        {/* Nutrition Diff Badges */}
                        <div className="swap-diff-badges">
                          {swap.highlights.map((h, i) => (
                            <span key={i} className="swap-diff-pill">
                              {h}
                            </span>
                          ))}
                        </div>

                        {/* Inspect Swap Button */}
                        <div className="swap-card-actions">
                          <button
                            type="button"
                            className="button button-small button-primary"
                            onClick={() => {
                              void fetchScorecard(swap.product.barcode);
                            }}
                          >
                            Inspect Swap →
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="no-swaps-box">
                  <span>🏆</span>
                  <p>
                    <strong>No higher-scoring match found.</strong> Jivanya did not find a qualifying alternative in this product category.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function getGradeColor(grade: string): string {
  switch (grade) {
    case "A":
      return "#15803d"; // Emerald green
    case "B":
      return "#4d7c0f"; // Lime green
    case "C":
      return "#b45309"; // Amber / Warm gold
    case "D":
      return "#c2410c"; // Orange
    case "E":
      return "#b91c1c"; // Crimson red
    default:
      return "#4b5563";
  }
}
