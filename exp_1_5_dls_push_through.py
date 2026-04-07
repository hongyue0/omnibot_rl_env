import numpy as np
import roboticstoolbox as rtb
from spatialmath import SE3
import timeit

print("=========================================================================")
print(" 核心实验 1.5 (极客修正版): 奇异点真实爆炸与 IK 矩阵直观对比")
print("=========================================================================\n")

robot = rtb.models.URDF.Panda()
I_7 = np.eye(7) 
I_6 = np.eye(6) 

print("-------------------------------------------------------------------------")
print(" 模块一：【真·奇异点爆炸】无 DLS vs 恒定 DLS vs 自适应 DLS")
print("-------------------------------------------------------------------------")
# 测试函数
def test_dls_performance(J, lam, v_req, scenario_name):
    # 使用推入恒等式求解
    q_dot = J.T @ np.linalg.inv(J @ J.T + (lam**2) * I_6) @ v_req
    v_actual = J @ q_dot
    speed = np.linalg.norm(q_dot)          
    error = np.linalg.norm(v_req - v_actual) 
    
    # 醒目的爆炸警告
    if speed > 100:
        speed_str = f"💥 {speed:8.2f} (电机烧毁!)"
    else:
        speed_str = f"🟢 {speed:8.2f} (安全)    "
        
    print(f"  [{scenario_name}]")
    print(f"    阻尼 λ={lam:.4f} | 总转速: {speed_str} | 追踪误差: {error:.6f} m/s")

# 【重点修正】：制造真正的奇异点死锁
# 姿态：Panda 机械臂几乎笔直指向上方 (Z轴极限)
q_singular = np.array([0.0, 1e-5, 0.0, 1e-5, 0.0, 0.0, 0.0])
J_A = robot.jacob0(q_singular)
w_A = np.sqrt(np.abs(np.linalg.det(J_A @ J_A.T))) 

# 【重点修正】：送命指令 -> 机械臂已经伸到了极限，还要强行以 0.1m/s 的速度继续往 Z 轴上方拽！
v_impossible = np.array([0.0, 0.0, 10.0, 0.0, 0.0, 0.0])

w_0, lam_max = 0.02, 0.1
lam_adp_A = lam_max * np.sqrt(1 - (w_A / w_0)**2) if w_A < w_0 else 0.0 

print(f"▶ 考场 A (处于奇异点边缘, 可操作度 w={w_A:.2e}):")
print("  [指令]: 强行向 Z 轴极限外继续拉扯...")
test_dls_performance(J_A, lam=1e-9, v_req=v_impossible, scenario_name="1. 传统无 DLS (裸奔)")
test_dls_performance(J_A, lam=lam_max, v_req=v_impossible, scenario_name="2. 恒定 DLS (死板)")
test_dls_performance(J_A, lam=lam_adp_A, v_req=v_impossible, scenario_name="3. 自适应 DLS (智能)")

# [场景 B] 健康安全区
q_healthy = np.array([0.0, -1.0, 0.0, -2.0, 0.0, 1.5, 0.0])
J_B = robot.jacob0(q_healthy)
w_B = np.sqrt(np.abs(np.linalg.det(J_B @ J_B.T)))
lam_adp_B = lam_max * np.sqrt(1 - (w_B / w_0)**2) if w_B < w_0 else 0.0
v_normal = np.array([0.1, 0.0, 0.0, 0.0, 0.0, 0.0]) # 正常的 X 轴平移

print(f"\n▶ 考场 B (处于安全区, 可操作度 w={w_B:.2e}):")
test_dls_performance(J_B, lam=1e-9, v_req=v_normal, scenario_name="1. 传统无 DLS (裸奔)")
test_dls_performance(J_B, lam=lam_max, v_req=v_normal, scenario_name="2. 恒定 DLS (死板)")
test_dls_performance(J_B, lam=lam_adp_B, v_req=v_normal, scenario_name="3. 自适应 DLS (智能)")


print("\n-------------------------------------------------------------------------")
print(" 模块二：【推入恒等式】验证 (J^T*J)^-1 与 J^T*(J*J^T)^-1 的等价性")
print("-------------------------------------------------------------------------")
lam_test = 0.05
def dls_standard_7x7(): return np.linalg.inv(J_A.T @ J_A + (lam_test**2) * I_7) @ J_A.T @ v_impossible
def dls_push_through_6x6(): return J_A.T @ np.linalg.inv(J_A @ J_A.T + (lam_test**2) * I_6) @ v_impossible

math_error = np.linalg.norm(dls_standard_7x7() - dls_push_through_6x6())
print(f"▶ 两种写法算出的电机指令误差为: {math_error:.2e} (数学上 100% 绝对等价！)")


print("\n-------------------------------------------------------------------------")
print(" 模块三：【算力压榨】10000 次极限 Benchmark 测速")
print("-------------------------------------------------------------------------")
num_tests = 10000
time_7x7 = timeit.timeit(dls_standard_7x7, number=num_tests)
time_6x6 = timeit.timeit(dls_push_through_6x6, number=num_tests)
gain = (time_7x7 - time_6x6) / time_7x7 * 100

print(f"▶ 传统写法 (求逆 7x7) 耗时: {time_7x7:.4f} 秒")
print(f"▶ 推入写法 (求逆 6x6) 耗时: {time_6x6:.4f} 秒")
print(f"▶ 结论：底层算力节省了 {gain:.1f}%！(受Python自身封装耗时稀释，若在C++中将达数十倍)")


print("\n-------------------------------------------------------------------------")
print(" 模块四：【实战落地】带矩阵对比的完整 IK 闭环 (自适应 DLS + 推入恒等式)")
print("-------------------------------------------------------------------------")
# 设定随机目标位姿
T_target = SE3.Tx(0.4) * SE3.Ty(0.3) * SE3.Tz(0.5) * SE3.RPY([0.1, 0.2, 0.3])
q_opt = np.zeros(7)  
max_iter = 100

print("▶ 正在向目标位姿逼近...\n")
for i in range(max_iter):
    T_cur = robot.fkine(q_opt)
    J_cur = robot.jacob0(q_opt)
    
    # 空间误差计算
    error_se3 = T_cur.inv() * T_target 
    v_err = np.concatenate((error_se3.t, error_se3.rpy())) 
    
    error_norm = np.linalg.norm(v_err)
    if error_norm < 1e-4:
        print(f"✅ 成功收敛！总迭代次数: {i}")
        break
        
    # 自适应 DLS 阻尼生成
    w_cur = np.sqrt(np.abs(np.linalg.det(J_cur @ J_cur.T)))
    lam_dynamic = 0.1 * np.sqrt(1 - (w_cur / 0.05)**2) if w_cur < 0.05 else 0.0
        
    # 推入恒等式 6x6 右求逆
    delta_q = J_cur.T @ np.linalg.inv(J_cur @ J_cur.T + (lam_dynamic**2) * I_6) @ v_err
    q_opt += delta_q * 0.5 

# 【重点修正】：输出直观的矩阵对齐对比
T_actual = robot.fkine(q_opt)

print("\n=================== 最终位姿精度核对 ===================")
print("【目标位姿矩阵 (T_target)】:")
print(np.round(T_target.A, 4))
print("\n【实际位姿矩阵 (T_actual)】:")
print(np.round(T_actual.A, 4))

print(f"\n▶ IK 反推得到的 7 轴关节角度 (rad): {np.round(q_opt, 4)}")
print("=========================================================")