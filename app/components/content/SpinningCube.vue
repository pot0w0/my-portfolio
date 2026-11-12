<script setup lang="ts">
const speed = ref(6)   // 1-10，越大越快
const hue = ref(200)   // 0-360

// 动画时长：速度 10 → 2s，速度 1 → 11s
const duration = computed(() => `${12 - speed.value}s`)
const cubeStyle = computed(() => ({
  animationDuration: duration.value,
  '--hue': hue.value,
}))
</script>

<template>
  <div class="safe-widget" :style="{ '--hue': hue }">
    <div class="cube-wrap">
      <div class="cube" :style="cubeStyle">
        <div class="face f1"></div>
        <div class="face f2"></div>
        <div class="face f3"></div>
        <div class="face f4"></div>
        <div class="face f5"></div>
        <div class="face f6"></div>
      </div>
    </div>

    <div class="row">
      <label>速度</label>
      <input v-model.number="speed" type="range" min="1" max="10" step="1" />
      <output>{{ speed }}</output>
    </div>

    <div class="row">
      <label>色相</label>
      <input v-model.number="hue" type="range" min="0" max="360" step="30" />
      <output>{{ hue }}</output>
    </div>
  </div>
</template>

<style scoped>
.safe-widget {
  --hue: 200;
  font-family: system-ui, -apple-system, sans-serif;
  color: #e0e0ff;
  background: radial-gradient(circle at 50% 30%, #1a1a2e, #050510 70%);
  padding: 24px;
  border-radius: 16px;
  width: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.cube-wrap { width: 120px; height: 120px; perspective: 600px; }
.cube {
  width: 100%; height: 100%;
  position: relative;
  transform-style: preserve-3d;
  animation: spin 8s linear infinite;   /* duration 由 :style 覆盖 */
}
.face {
  position: absolute; inset: 0;
  border: 2px solid hsl(var(--hue) 90% 60% / 0.8);
  background: hsl(var(--hue) 80% 40% / 0.25);
  box-shadow: 0 0 18px hsl(var(--hue) 90% 60% / 0.5),
              inset 0 0 18px hsl(var(--hue) 90% 60% / 0.3);
}
.f1 { transform: rotateY(0deg) translateZ(60px); }
.f2 { transform: rotateY(180deg) translateZ(60px); }
.f3 { transform: rotateY(90deg) translateZ(60px); }
.f4 { transform: rotateY(-90deg) translateZ(60px); }
.f5 { transform: rotateX(90deg) translateZ(60px); }
.f6 { transform: rotateX(-90deg) translateZ(60px); }

@keyframes spin {
  from { transform: rotateX(0) rotateY(0) rotateZ(0); }
  to   { transform: rotateX(360deg) rotateY(360deg) rotateZ(360deg); }
}

.row { display: flex; align-items: center; gap: 10px; width: 100%; }
.row label { font-size: 12px; color: #99a; min-width: 44px; }
.row output { font-size: 12px; color: hsl(var(--hue) 90% 70%); min-width: 32px; text-align: right; }

input[type="range"] {
  -webkit-appearance: none; appearance: none;
  flex: 1; height: 6px; border-radius: 3px;
  background: linear-gradient(90deg, hsl(var(--hue) 80% 50% / 0.3), hsl(var(--hue) 80% 50% / 0.9));
  outline: none; cursor: pointer;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 16px; height: 16px; border-radius: 50%;
  background: hsl(var(--hue) 90% 65%);
  box-shadow: 0 0 10px hsl(var(--hue) 90% 60% / 0.8);
  cursor: grab;
}
input[type="range"]::-moz-range-thumb {
  width: 16px; height: 16px; border: none; border-radius: 50%;
  background: hsl(var(--hue) 90% 65%);
  box-shadow: 0 0 10px hsl(var(--hue) 90% 60% / 0.8);
  cursor: grab;
}
</style>