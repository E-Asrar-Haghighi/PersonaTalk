import { useEffect, useRef, useState } from "react";

export interface AudioInputDevice {
  deviceId: string;
  label: string;
}

const RECORDER_DEVICE_KEY = "personatalk:selected-mic-id";

export function useRecorder() {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [devices, setDevices] = useState<AudioInputDevice[]>([]);
  const [hasMicrophoneAccess, setHasMicrophoneAccess] = useState(false);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>(() => {
    try {
      return window.localStorage.getItem(RECORDER_DEVICE_KEY) ?? "";
    } catch {
      return "";
    }
  });

  useEffect(() => {
    void refreshDevices();

    const mediaDevices = navigator.mediaDevices;
    const handleDeviceChange = () => {
      void refreshDevices();
    };
    mediaDevices?.addEventListener?.("devicechange", handleDeviceChange);

    return () => {
      recorderRef.current?.stream.getTracks().forEach((track) => track.stop());
      mediaDevices?.removeEventListener?.("devicechange", handleDeviceChange);
    };
  }, []);

  useEffect(() => {
    try {
      if (selectedDeviceId) {
        window.localStorage.setItem(RECORDER_DEVICE_KEY, selectedDeviceId);
      } else {
        window.localStorage.removeItem(RECORDER_DEVICE_KEY);
      }
    } catch {
      // Ignore localStorage failures and keep recorder usable.
    }
  }, [selectedDeviceId]);

  async function requestMicrophoneAccess() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach((track) => track.stop());
    setHasMicrophoneAccess(true);
    await refreshDevices();
  }

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: selectedDeviceId ? { deviceId: { exact: selectedDeviceId } } : true
    });
    setHasMicrophoneAccess(true);
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };
    recorder.start();
    recorderRef.current = recorder;
    setIsRecording(true);
    void refreshDevices();
  }

  async function stop(): Promise<Blob> {
    const recorder = recorderRef.current;
    if (!recorder) {
      throw new Error("Recorder is not active.");
    }

    return new Promise<Blob>((resolve, reject) => {
      recorder.onstop = () => {
        recorder.stream.getTracks().forEach((track) => track.stop());
        recorderRef.current = null;
        setIsRecording(false);
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
        void convertToWav(blob).then(resolve).catch(reject);
      };
      recorder.stop();
    });
  }

  async function refreshDevices() {
    if (!navigator.mediaDevices?.enumerateDevices) {
      return;
    }

    const entries = await navigator.mediaDevices.enumerateDevices();
    const audioInputs = entries
      .filter((entry) => entry.kind === "audioinput")
      .map((entry, index) => ({
        deviceId: entry.deviceId,
        label: entry.label || `Microphone ${index + 1}`
      }));
    const normalizedAudioInputs = normalizeAudioInputLabels(audioInputs);

    setHasMicrophoneAccess(audioInputs.some((device) => !/^Microphone \d+$/.test(device.label)));
    setDevices(normalizedAudioInputs);
    setSelectedDeviceId((current) => {
      if (current && normalizedAudioInputs.some((device) => device.deviceId === current)) {
        return current;
      }
      return normalizedAudioInputs[0]?.deviceId ?? "";
    });
  }

  return {
    isRecording,
    start,
    stop,
    devices,
    hasMicrophoneAccess,
    requestMicrophoneAccess,
    selectedDeviceId,
    setSelectedDeviceId,
    refreshDevices
  };
}

async function convertToWav(blob: Blob): Promise<Blob> {
  const arrayBuffer = await blob.arrayBuffer();
  const context = new AudioContext();
  try {
    const audioBuffer = await context.decodeAudioData(arrayBuffer.slice(0));
    return encodeWav(audioBuffer);
  } finally {
    await context.close();
  }
}

function encodeWav(audioBuffer: AudioBuffer): Blob {
  const sampleRate = audioBuffer.sampleRate;
  const channelData = audioBuffer.getChannelData(0);
  const wavBuffer = new ArrayBuffer(44 + channelData.length * 2);
  const view = new DataView(wavBuffer);

  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + channelData.length * 2, true);
  writeString(view, 8, "WAVE");
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, "data");
  view.setUint32(40, channelData.length * 2, true);

  let offset = 44;
  for (let index = 0; index < channelData.length; index += 1) {
    const sample = Math.max(-1, Math.min(1, channelData[index]));
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
    offset += 2;
  }

  return new Blob([wavBuffer], { type: "audio/wav" });
}

function writeString(view: DataView, offset: number, value: string) {
  for (let index = 0; index < value.length; index += 1) {
    view.setUint8(offset + index, value.charCodeAt(index));
  }
}

function normalizeAudioInputLabels(devices: AudioInputDevice[]): AudioInputDevice[] {
  const counts = new Map<string, number>();

  return devices.map((device) => {
    const baseLabel = prettifyAudioLabel(device.label);
    const seen = counts.get(baseLabel) ?? 0;
    counts.set(baseLabel, seen + 1);
    return {
      ...device,
      label: seen === 0 ? baseLabel : `${baseLabel} ${seen + 1}`
    };
  });
}

function prettifyAudioLabel(rawLabel: string): string {
  const trimmed = rawLabel.trim();
  if (!trimmed) {
    return "Microphone";
  }

  const prefixMatch = trimmed.match(/^(Default|Communications)\s*-\s*(.+)$/i);
  if (prefixMatch) {
    const prefix = prefixMatch[1].toLowerCase() === "default" ? "Default" : "Communications";
    return `${prefix}: ${prettifyAudioLabel(prefixMatch[2])}`;
  }

  const normalized = trimmed
    .replace(/\([0-9a-f]{4}:[0-9a-f]{4}\)/gi, "")
    .replace(/\s+/g, " ")
    .trim();

  if (/microphone array/i.test(normalized) || /intel.+smart sound/i.test(normalized)) {
    return "Laptop microphone";
  }

  const namedMicrophoneMatch = normalized.match(/^Microphone\s*\((.+)\)$/i);
  if (namedMicrophoneMatch) {
    return toTitleCase(namedMicrophoneMatch[1]);
  }

  return toTitleCase(normalized);
}

function toTitleCase(value: string): string {
  return value
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => {
      if (part.length <= 3 && /[A-Z]/.test(part)) {
        return part.toUpperCase();
      }
      return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
    })
    .join(" ");
}
