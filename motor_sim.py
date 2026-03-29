"""Simple angle-limited motor model with bounded slew rate."""

from __future__ import annotations

import math
from typing import List, Tuple


def _shortest_angle_delta(current_deg: float, target_deg: float) -> float:
    """Signed smallest rotation from current to target, in (-180, 180]."""
    d = target_deg - current_deg
    return (d + 180.0) % 360.0 - 180.0


class BasicMotor:
    """Motor with angle clamped to [-180, 180] and max slew 100°/s."""

    MAX_SPEED_DEG_S = 100.0

    def __init__(self, initial_angle: float = 0.0) -> None:
        self._angle = 0.0
        self.angle = float(initial_angle)

    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        v = float(value)
        if v < -180.0:
            self._angle = -180.0
        elif v > 180.0:
            self._angle = 180.0
        else:
            self._angle = v

    def step(self, target_angle: float, dt: float) -> None:
        """Move toward target_angle; |angular speed| capped at MAX_SPEED_DEG_S."""
        if dt <= 0.0:
            return
        delta = _shortest_angle_delta(self._angle, float(target_angle))
        max_step = self.MAX_SPEED_DEG_S * dt
        if abs(delta) <= max_step:
            self.angle = self._angle + delta
        else:
            sign = math.copysign(1.0, delta)
            self.angle = self._angle + sign * max_step


def _run_experiment(dt: float, total_time: float) -> Tuple[List[float], List[float]]:
    """Square-wave setpoint ±130° every 1 s — low dt stairs and lags noticeably."""
    motor = BasicMotor(0.0)
    times: List[float] = []
    angles: List[float] = []
    t = 0.0
    while t < total_time:
        setpoint = 130.0 if int(t) % 2 == 0 else -130.0
        motor.step(setpoint, dt)
        t += dt
        times.append(t)
        angles.append(motor.angle)
    return times, angles


if __name__ == "__main__":
    total = 5.0

    print("对比实验：方波参考 ±130°（每秒翻转），电机最大 100°/s\n")

    t_a, a_a = _run_experiment(0.01, total)
    t_b, a_b = _run_experiment(0.5, total)

    print(f"实验 A：dt = 0.01 s (100 Hz)，步数 ≈ {len(t_a)}")
    print(f"  末时刻 t={t_a[-1]:.3f} s，角度 = {a_a[-1]:.4f}°")
    print(f"实验 B：dt = 0.5 s (2 Hz)，步数 ≈ {len(t_b)}")
    print(f"  末时刻 t={t_b[-1]:.3f} s，角度 = {a_b[-1]:.4f}°")

    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(t_a, a_a, label="A: dt=0.01 (平滑)", linewidth=1.2)
        ax.plot(t_b, a_b, label="B: dt=0.5 (阶跃/滞后)", linewidth=1.5, marker="o", markersize=4)
        ref_t = [0.0, 1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0, 5.0, 5.0]
        ref_y = [130, 130, -130, -130, 130, 130, -130, -130, 130, 130, -130]
        ax.plot(ref_t, ref_y, "k--", alpha=0.45, label="参考（方波）")
        ax.set_xlabel("t / s")
        ax.set_ylabel("angle / °")
        ax.set_title("BasicMotor：相同参考，不同控制周期")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        plt.show()
    except ImportError:
        print("\n(未安装 matplotlib，已跳过绘图；可 pip install matplotlib 查看曲线)")
