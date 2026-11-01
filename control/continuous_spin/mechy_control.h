/* mechy_control.h - small, tested control and signal algorithms for microcontroller firmware.
 *
 * Header-only, C++11, no Arduino dependency (so engine/tests runs it on a PC), no heap, float
 * maths only. Works on AVR (Uno/Nano/Mega), ESP32, RP2040, Teensy, SAMD, Renesas.
 * Copy this file next to your .ino and `#include "mechy_control.h"`.
 *
 * Contents (theory and tuning: knowledge/controls_robotics.md, the section given):
 *   FixedRate        wrap-safe fixed-period loop timer on micros()            (sec. 3, 11)
 *   Pid              PID: derivative on measurement + filter, setpoint weight,
 *                    conditional-integration anti-windup, feedforward input   (sec. 2.3-2.8)
 *   Ema              first-order low-pass (exponential moving average)       (sec. 5)
 *   LowPass2         2nd-order Butterworth low-pass (biquad, bilinear)
 *   Median3          3-sample median: removes single-sample spikes
 *   MovingAverage<N> boxcar average over N samples
 *   SlewLimiter      limits the rate of change of a command
 *   Hysteresis       on/off threshold with a dead band (thermostat logic)
 *   Debounce         time-based debouncer for buttons and switches
 *   Trapezoid        time-optimal move under v_max, a_max (triangle if short) (sec. 7.2)
 *   MinJerk          smooth point-to-point move, zero vel/acc at both ends   (sec. 7.4)
 *   Complementary    gyro + accelerometer angle fusion                       (sec. 5.2)
 *   KalmanAngle      2-state Kalman filter: angle + gyro bias                (sec. 5.3)
 *   AlphaBeta        position/velocity tracker from noisy position samples   (sec. 5.4)
 *
 * Units: whatever you feed in, but keep them SI internally (s, rad, m) and dt in seconds.
 */
#ifndef MECHY_CONTROL_H
#define MECHY_CONTROL_H

#include <math.h>
#include <stdint.h>

namespace mc {

inline float clampf(float x, float lo, float hi) { return x < lo ? lo : (x > hi ? hi : x); }
inline float signf(float x) { return x < 0.0f ? -1.0f : 1.0f; }

/* ---------------------------------------------------------------- FixedRate
 * if (loop.due(micros())) { ...runs every period_us... }
 * Keeps a fixed phase (next += period), so the average rate is exact. If the work overran a
 * whole period it resynchronises instead of bursting, and counts the overrun. */
struct FixedRate {
  uint32_t period_us;
  uint32_t next = 0;
  uint32_t overruns = 0;
  bool started = false;
  explicit FixedRate(uint32_t period) : period_us(period) {}
  bool due(uint32_t now_us) {
    if (!started) { started = true; next = now_us + period_us; return true; }
    if ((int32_t)(now_us - next) < 0) return false;
    next += period_us;
    if ((int32_t)(now_us - next) >= 0) { next = now_us + period_us; overruns++; }
    return true;
  }
  float dt() const { return period_us * 1e-6f; }
};

/* ---------------------------------------------------------------- Pid
 * u = kp*(b*sp - y) + ki*integral(e) - kd*dy/dt (filtered) + ff, clamped to [out_min, out_max].
 * - Derivative acts on the measurement (no kick on setpoint steps), low-passed with time
 *   constant kd/(kp*n); n = 5..20 (higher = less filtering).
 * - Anti-windup: the integrator stops while the output is saturated in the direction the error
 *   pushes, and is clamped to the output range. Integral is stored as ki*sum(e*dt), so changing
 *   ki on the fly does not bump the output.
 * - ff: feedforward (velocity, friction, gravity) added before the clamp; it does most of the
 *   work, feedback cleans up. */
struct Pid {
  float kp, ki, kd;
  float out_min, out_max;
  float n = 10.0f;       // derivative filter ratio
  float b = 1.0f;        // setpoint weight on P (0..1; <1 = less overshoot on steps)
  float integ = 0.0f, d_state = 0.0f, prev_y = 0.0f, out = 0.0f;
  bool first = true;

  Pid(float kp_, float ki_, float kd_, float lo, float hi) : kp(kp_), ki(ki_), kd(kd_), out_min(lo), out_max(hi) {}

  void reset(float y = 0.0f, float u0 = 0.0f) {   // bumpless start from output u0
    integ = clampf(u0, out_min, out_max); d_state = 0.0f; prev_y = y; out = u0; first = true;
  }

  float update(float sp, float y, float dt, float ff = 0.0f) {
    if (dt <= 0.0f) return out;
    float e = sp - y;
    float p = kp * (b * sp - y);
    float dy = first ? 0.0f : -(y - prev_y) / dt;
    prev_y = y;
    first = false;
    float tf = (kp > 0.0f && n > 0.0f) ? kd / (kp * n) : 0.0f;
    d_state = tf > 0.0f ? d_state + (dt / (tf + dt)) * (dy - d_state) : dy;
    float d = kd * d_state;
    float u_raw = p + integ + d + ff;
    out = clampf(u_raw, out_min, out_max);
    float di = ki * e * dt;
    bool pushing_out = (u_raw >= out_max && di > 0.0f) || (u_raw <= out_min && di < 0.0f);
    if (!pushing_out) integ = clampf(integ + di, out_min, out_max);
    return out;
  }
};

/* ---------------------------------------------------------------- filters */
struct Ema {   // y += a*(x - y), a = dt/(tau + dt), tau = 1/(2*pi*fc)
  float a, y = 0.0f;
  bool init = false;
  explicit Ema(float alpha) : a(alpha) {}
  static Ema cutoff(float fc_hz, float dt) { float tau = 1.0f / (6.2831853f * fc_hz); return Ema(dt / (tau + dt)); }
  float update(float x) { if (!init) { y = x; init = true; } else y += a * (x - y); return y; }
};

struct LowPass2 {   // Butterworth, -40 dB/decade above fc; needs fc < fs/2
  float b0 = 1, b1 = 0, b2 = 0, a1 = 0, a2 = 0, x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  bool init = false;
  LowPass2(float fc_hz, float fs_hz) {
    float k = tanf(3.14159265f * fc_hz / fs_hz), q = 1.41421356f;
    float norm = 1.0f / (1.0f + q * k + k * k);
    b0 = k * k * norm; b1 = 2.0f * b0; b2 = b0;
    a1 = 2.0f * (k * k - 1.0f) * norm; a2 = (1.0f - q * k + k * k) * norm;
  }
  float update(float x) {
    if (!init) { x1 = x2 = y1 = y2 = x; init = true; }
    float y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2;
    x2 = x1; x1 = x; y2 = y1; y1 = y;
    return y;
  }
};

struct Median3 {
  float a = 0, b = 0;
  uint8_t count = 0;
  float update(float x) {
    if (count < 2) { count++; float r = x; a = b; b = x; return r; }
    float lo = a < b ? a : b, hi = a < b ? b : a;
    float m = x < lo ? lo : (x > hi ? hi : x);
    a = b; b = x;
    return m;
  }
};

template <uint8_t N>
struct MovingAverage {
  float buf[N] = {};
  float sum = 0;
  uint8_t i = 0, count = 0;
  float update(float x) {
    if (count == N) sum -= buf[i]; else count++;
    buf[i] = x; sum += x;
    i = (uint8_t)((i + 1) % N);
    return sum / count;
  }
};

struct SlewLimiter {   // output moves toward the input at most `rate` units per second
  float rate, y = 0.0f;
  bool init = false;
  explicit SlewLimiter(float r) : rate(r) {}
  float update(float x, float dt) {
    if (!init) { y = x; init = true; return y; }
    y += clampf(x - y, -rate * dt, rate * dt);
    return y;
  }
};

struct Hysteresis {   // true above `on`, false below `off` (on > off), holds in between
  float on, off;
  bool state = false;
  Hysteresis(float on_, float off_) : on(on_), off(off_) {}
  bool update(float x) { if (x >= on) state = true; else if (x <= off) state = false; return state; }
};

struct Debounce {   // reports a new level only after the raw input held it for `ms`
  uint32_t ms, since = 0;
  bool stable = false, last = false, started = false;
  explicit Debounce(uint32_t hold_ms) : ms(hold_ms) {}
  bool update(bool raw, uint32_t now_ms) {
    if (!started) { started = true; stable = last = raw; since = now_ms; return stable; }
    if (raw != last) { last = raw; since = now_ms; }
    else if (raw != stable && (uint32_t)(now_ms - since) >= ms) stable = raw;
    return stable;
  }
};

/* ---------------------------------------------------------------- motion profiles */
struct Trapezoid {   // plan(), then sample(t) for t in [0, duration]
  float p0 = 0, dir = 1, a = 1, v_peak = 0, t_acc = 0, t_flat = 0, duration = 0, dist = 0;
  void plan(float from, float to, float v_max, float a_max) {
    p0 = from; dist = fabsf(to - from); dir = signf(to - from); a = a_max;
    if (dist == 0.0f || v_max <= 0.0f || a_max <= 0.0f) { v_peak = t_acc = t_flat = duration = 0; return; }
    t_acc = v_max / a_max;
    float d_acc = 0.5f * a_max * t_acc * t_acc;
    if (2.0f * d_acc >= dist) {           // triangle: never reaches v_max
      t_acc = sqrtf(dist / a_max); v_peak = a_max * t_acc; t_flat = 0.0f;
    } else {
      v_peak = v_max; t_flat = (dist - 2.0f * d_acc) / v_max;
    }
    duration = 2.0f * t_acc + t_flat;
  }
  void sample(float t, float &pos, float &vel, float &acc) const {
    float s, v, ac;
    if (t <= 0.0f) { s = 0; v = 0; ac = duration > 0 ? a : 0; }
    else if (t < t_acc) { s = 0.5f * a * t * t; v = a * t; ac = a; }
    else if (t < t_acc + t_flat) { float u = t - t_acc; s = 0.5f * a * t_acc * t_acc + v_peak * u; v = v_peak; ac = 0; }
    else if (t < duration) { float u = duration - t; s = dist - 0.5f * a * u * u; v = a * u; ac = -a; }
    else { s = dist; v = 0; ac = 0; }
    pos = p0 + dir * s; vel = dir * v; acc = dir * ac;
  }
  float position(float t) const { float p, v, ac; sample(t, p, v, ac); return p; }
};

struct MinJerk {   // p(t) = p0 + (p1-p0)(10s^3 - 15s^4 + 6s^5), s = t/T
  float p0 = 0, p1 = 0, T = 1;
  void plan(float from, float to, float duration) { p0 = from; p1 = to; T = duration > 0 ? duration : 1e-6f; }
  /* shortest duration that keeps peak speed <= v_max (peak = 1.875 * dist / T) */
  static float durationFor(float dist, float v_max) { return 1.875f * fabsf(dist) / v_max; }
  void sample(float t, float &pos, float &vel) const {
    float s = clampf(t / T, 0.0f, 1.0f), d = p1 - p0;
    float s2 = s * s, s3 = s2 * s;
    pos = p0 + d * (10.0f * s3 - 15.0f * s3 * s + 6.0f * s3 * s2);
    vel = (t <= 0.0f || t >= T) ? 0.0f : d * (30.0f * s2 - 60.0f * s3 + 30.0f * s3 * s) / T;
  }
};

/* ---------------------------------------------------------------- estimators */
struct Complementary {   // angle = k*(angle + rate*dt) + (1-k)*accel_angle; k = tau/(tau+dt)
  float k, angle = 0.0f;
  bool init = false;
  explicit Complementary(float k_) : k(k_) {}
  static Complementary withTau(float tau_s, float dt) { return Complementary(tau_s / (tau_s + dt)); }
  float update(float gyro_rate, float accel_angle, float dt) {
    if (!init) { angle = accel_angle; init = true; return angle; }
    angle = k * (angle + gyro_rate * dt) + (1.0f - k) * accel_angle;
    return angle;
  }
};

/* State [angle, gyro_bias]; predict with the gyro rate, correct with the accelerometer angle.
 * q_angle, q_bias: process noise (per second); r: accel angle variance (rad^2). The defaults
 * suit an MPU-6050 at 100-500 Hz (estimate; tune r up if the angle jitters, q_bias up if the
 * bias estimate is too slow). */
struct KalmanAngle {
  float q_angle = 0.001f, q_bias = 0.003f, r = 0.03f;
  float angle = 0.0f, bias = 0.0f;
  float P[2][2] = {{1, 0}, {0, 1}};
  bool init = false;
  float update(float gyro_rate, float accel_angle, float dt) {
    if (!init) { angle = accel_angle; init = true; return angle; }
    float rate = gyro_rate - bias;
    angle += dt * rate;
    P[0][0] += dt * (dt * P[1][1] - P[0][1] - P[1][0] + q_angle);
    P[0][1] -= dt * P[1][1];
    P[1][0] -= dt * P[1][1];
    P[1][1] += q_bias * dt;
    float s = P[0][0] + r;
    float k0 = P[0][0] / s, k1 = P[1][0] / s;
    float y = accel_angle - angle;
    angle += k0 * y;
    bias += k1 * y;
    float p00 = P[0][0], p01 = P[0][1];
    P[0][0] -= k0 * p00; P[0][1] -= k0 * p01;
    P[1][0] -= k1 * p00; P[1][1] -= k1 * p01;
    return angle;
  }
};

struct AlphaBeta {   // alpha 0..1 (position trust), beta ~ alpha^2/(2-alpha)
  float alpha, beta, x = 0.0f, v = 0.0f;
  bool init = false;
  AlphaBeta(float a, float b) : alpha(a), beta(b) {}
  void update(float meas, float dt) {
    if (!init) { x = meas; v = 0; init = true; return; }
    float xp = x + v * dt, r = meas - xp;
    x = xp + alpha * r;
    v += (beta / dt) * r;
  }
};

}  // namespace mc

#endif
