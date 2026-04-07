import numpy as np
from scipy.linalg import expm, logm
import matplotlib.pyplot as plt
import matplotlib.animation as animation

print("==================================================================")
print(" 核心实验 1.4: 纯 Numpy 与 POE 大一统 (直白连乘+逐行注释版)")
print("==================================================================\n")

# ====================================================================
# [第 1 层：李代数基础算子 (用于把 1D 数字变成 3D 和 6D 矩阵)]
# ====================================================================
def skew_3d(w):
    """【叉乘矩阵】把 3 维角速度变成 3x3 反对称矩阵，用于计算旋转"""
    return np.array([[ 0, -w[2], w[1]], 
                     [ w[2], 0, -w[0]], 
                     [-w[1], w[0], 0]])

def skew_6d(twist):
    """【升维装箱】把 6 维螺旋向量 [v, w] 装进 4x4 的李代数矩阵 (se3)，准备喂给 expm"""
    se3 = np.zeros((4, 4))
    se3[0:3, 0:3] = skew_3d(twist[3:6]) # 右下角填入角速度反对称矩阵
    se3[0:3, 3]   = twist[0:3]          # 右上角填入线速度
    return se3

def unskew_6d(se3):
    """【降维拆箱】把 4x4 李代数矩阵，重新提取出 6 维的速度/误差向量"""
    v = se3[0:3, 3]
    w = np.array([se3[2, 1], se3[0, 2], se3[1, 0]])
    return np.concatenate((v, w))

def adjoint_matrix(T):
    """
    【伴随矩阵】极其重要！
    输入一个 4x4 位姿矩阵 T，输出 6x6 伴随矩阵 Ad。
    作用：把手腕处感知的速度，通过物理力臂，折算成底座感受到的整体速度。
    """
    R = T[0:3, 0:3]
    p = T[0:3, 3]
    Ad = np.zeros((6, 6))
    Ad[0:3, 0:3] = R                      # 线速度直接旋转
    Ad[0:3, 3:6] = skew_3d(p) @ R         # 魔法：角速度加上力臂(p)，会产生额外的线速度！
    Ad[3:6, 3:6] = R                      # 角速度直接旋转
    return Ad

def create_twist(omega, q):
    """【物理测绘算子】输入测量好的 旋转方向(omega) 和 绝对坐标(q)，算出 6D 螺旋轴"""
    v = -np.cross(omega, q)
    return np.concatenate((v, omega))


# ====================================================================
# [第 2 层：拿尺子测量机械臂 (M_joints 和 twists 的由来)]
# ====================================================================
# 定义纯物理的杆件长度 (米)
L1, L_offset, L2, L3, L4, L5 = 0.3, 0.1, 0.4, 0.35, 0.15, 0.1

# 【由来解答 1】：twists 是机械臂关节的“运动属性”
# 当机械臂角度全为 0 时，量出每个电机的 朝向(omega) 和 空间绝对位置(q)
twists = [
    create_twist(omega=[0, 0, 1], q=[0, 0, L1]),                             # 关节1
    create_twist(omega=[0, 1, 0], q=[0, L_offset, L1]),                      # 关节2 (带偏置)
    create_twist(omega=[0, 1, 0], q=[0, L_offset, L1 + L2]),                 # 关节3
    create_twist(omega=[0, 1, 0], q=[0, L_offset, L1 + L2 + L3]),            # 关节4
    create_twist(omega=[0, 0, 1], q=[0, L_offset, L1 + L2 + L3 + L4]),       # 关节5
    create_twist(omega=[1, 0, 0], q=[L5, L_offset, L1 + L2 + L3 + L4])       # 关节6
]

# 【由来解答 2】：M_joints 是机械臂的“静态骨架图纸”
# 把上面测量的坐标 q 直接填入 4x4 矩阵的右上角。
# 它代表当没有任何电机转动时，各个关节和末端在宇宙中的绝对位置。
M_joints = [
    np.block([[np.eye(3), np.array([[0], [0], [0]])], [0,0,0,1]]),                                       # 0: 底座原点
    np.block([[np.eye(3), np.array([[0], [0], [L1]])], [0,0,0,1]]),                                      # 1: 关节1中心
    np.block([[np.eye(3), np.array([[0], [L_offset], [L1]])], [0,0,0,1]]),                               # 2: 关节2中心
    np.block([[np.eye(3), np.array([[0], [L_offset], [L1 + L2]])], [0,0,0,1]]),                          # 3: 关节3中心
    np.block([[np.eye(3), np.array([[0], [L_offset], [L1 + L2 + L3]])], [0,0,0,1]]),                     # 4: 关节4中心
    np.block([[np.eye(3), np.array([[0], [L_offset], [L1 + L2 + L3 + L4]])], [0,0,0,1]]),                # 5: 关节5中心
    np.block([[np.eye(3), np.array([[L5], [L_offset], [L1 + L2 + L3 + L4]])], [0,0,0,1]])                # 6: 末端夹爪
]


# ====================================================================
# [第 3 层：运动学正解 (FK) 与雅可比推导 (彻底砸碎循环，直视公式！)]
# ====================================================================
def forward_kinematics_explicit(theta):
    """给定 6 个角度，用 POE 公式推导每个关节的位置和末端位姿"""
    
    # 1. 算出每个电机的“空间扭曲算子”。
    # 用 expm 把“静止的螺旋轴”乘以“你要转的角度”，变成真实的 4x4 旋转平移矩阵
    R1 = expm(skew_6d(twists[0]) * theta[0])
    R2 = expm(skew_6d(twists[1]) * theta[1])
    R3 = expm(skew_6d(twists[2]) * theta[2])
    R4 = expm(skew_6d(twists[3]) * theta[3])
    R5 = expm(skew_6d(twists[4]) * theta[4])
    R6 = expm(skew_6d(twists[5]) * theta[5])

    # 2. 像滤镜一样，把旋转算子一层层叠加上去，强行扭曲静态骨架 (M_joints)
    pos_0 = (M_joints[0])[0:3, 3]                                  # 原点没变
    pos_1 = (M_joints[1])[0:3, 3]                                  # 关节1不随自己转动
    pos_2 = (R1 @ M_joints[2])[0:3, 3]                             # 关节2受关节1影响
    pos_3 = (R1 @ R2 @ M_joints[3])[0:3, 3]                        # 关节3受 1,2 影响
    pos_4 = (R1 @ R2 @ R3 @ M_joints[4])[0:3, 3]                   # 关节4受 1,2,3 影响
    pos_5 = (R1 @ R2 @ R3 @ R4 @ M_joints[5])[0:3, 3]              # ...
    pos_6 = (R1 @ R2 @ R3 @ R4 @ R5 @ M_joints[6])[0:3, 3]
    
    # 3. 终极公式：末端执行器的绝对位姿 = 所有旋转滤镜连乘 @ 末端静态骨架
    T_end = R1 @ R2 @ R3 @ R4 @ R5 @ R6 @ M_joints[6]
    
    return T_end, np.array([pos_0, pos_1, pos_2, pos_3, pos_4, pos_5, pos_6])

def space_jacobian_explicit(theta):
    """通过伴随矩阵，手推 6x6 空间雅可比矩阵"""
    R1 = expm(skew_6d(twists[0]) * theta[0])
    R2 = expm(skew_6d(twists[1]) * theta[1])
    R3 = expm(skew_6d(twists[2]) * theta[2])
    R4 = expm(skew_6d(twists[3]) * theta[3])
    R5 = expm(skew_6d(twists[4]) * theta[4])
    # 雅可比的每一列，都是把该电机的螺旋轴，用伴随矩阵投影到世界原点！
    J = np.zeros((6, 6))
    J[:, 0] = twists[0]                                            # J1不需伴随，就在原点坐标系
    J[:, 1] = adjoint_matrix(R1) @ twists[1]                       # J2 被 R1 带着动了
    J[:, 2] = adjoint_matrix(R1 @ R2) @ twists[2]                  # J3 被 R1, R2 带着动了
    J[:, 3] = adjoint_matrix(R1 @ R2 @ R3) @ twists[3]
    J[:, 4] = adjoint_matrix(R1 @ R2 @ R3 @ R4) @ twists[4]
    J[:, 5] = adjoint_matrix(R1 @ R2 @ R3 @ R4 @ R5) @ twists[5]
    return J


# ====================================================================
# [第 4 层：李群对数映射 (log) -> 插值 -> 指数映射 (exp) -> DLS 逆解]
# ====================================================================
print("▶ [计算] 正在执行李代数测地线插值与 DLS 防爆逆向寻优...")

theta_start = np.array([0.0,  0.2,  0.3, -0.1,  0.0, 0.0])
theta_target = np.array([1.5, -0.5,  0.8, -0.4,  1.0, 0.5])

T_start, _ = forward_kinematics_explicit(theta_start)
T_target, _ = forward_kinematics_explicit(theta_target)

# 【重点：logm】算出目标相对起点的真实距离和旋转误差（挤成平坦的 4x4 矩阵）
T_diff = T_target @ np.linalg.inv(T_start)
se3_matrix = np.real(logm(T_diff)) 

steps = 60
trajectory_positions = []
theta_current = theta_start.copy()

for i in range(steps):
    fraction = i / (steps - 1)
    
    # 【重点：expm】根据进度条 fraction，把误差矩阵卷曲回去，算出当前该到的理想位姿！
    T_ideal = expm(se3_matrix * fraction) @ T_start
    
    # 【DLS 逆向寻优】用雅可比推算出电机应该转多少度，才能跟上 T_ideal
    for _ in range(8):  
        T_cur, _ = forward_kinematics_explicit(theta_current)
        J_s = space_jacobian_explicit(theta_current)
        
        # 算出当前实际位姿和理想位姿的 6D 空间误差
        V_error = unskew_6d(np.real(logm(T_ideal @ np.linalg.inv(T_cur))))
        
        # 阻尼最小二乘法防爆核心方程：(J^T * J + λ^2 * I)^-1 * J^T
        lambda_sq = 0.01 
        J_pinv = J_s.T @ np.linalg.inv(J_s @ J_s.T + lambda_sq * np.eye(6))
        
        # 牛顿迭代更新：当前角度 = 当前角度 + 修正值
        theta_current = theta_current + J_pinv @ V_error
        
    _, positions = forward_kinematics_explicit(theta_current)
    trajectory_positions.append(positions)

trajectory_loop = trajectory_positions + trajectory_positions[::-1]

# ====================================================================
# [第 5 层：3D 动态无限渲染]
# ====================================================================
print("🚀 [渲染] 物理绘图引擎已启动！")

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim(-1.0, 1.0); ax.set_ylim(-1.0, 1.0); ax.set_zlim(0, 1.5)
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
ax.set_title("POE Pure Math: Direct Formula Rendering")

line, = ax.plot([], [], [], 'o-', lw=5, markersize=8, color='#FF5733')

def update(frame):
    positions = trajectory_loop[frame]
    xs, ys, zs = positions[:, 0], positions[:, 1], positions[:, 2]
    line.set_data(xs, ys)
    line.set_3d_properties(zs)
    return line,

ani = animation.FuncAnimation(fig, update, frames=len(trajectory_loop), interval=40, blit=True)
plt.show()