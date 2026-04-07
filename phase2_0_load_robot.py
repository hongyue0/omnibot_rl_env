import os
import sys
import numpy as np

# 1. 自动化路径挂载 (保持之前的成功路径)
ISAAC_PATH = "/home/zgx/omnibot_project/isaacsim/_build/linux-x86_64/release"
exts_path = os.path.join(ISAAC_PATH, "exts")
if os.path.exists(exts_path):
    for ext in os.listdir(exts_path):
        sys.path.append(os.path.join(exts_path, ext))

# 2. 极致性能启动
from isaacsim import SimulationApp
CONFIG = {
    "headless": False, 
    "renderer": "RayTracedLighting",
    "width": 1024,
    "height": 768,
}
kit = SimulationApp(CONFIG)

# 3. 导入核心工具
from isaacsim.core.api import SimulationContext
from isaacsim.core.utils.prims import create_prim
from isaacsim.core.utils.viewports import set_camera_view # 视角控制
from isaacsim.asset.importer.urdf import _urdf

# 初始化场景
world = SimulationContext(stage_units_in_meters=1.0)
create_prim("/World/Ground", "StaticPlane")
create_prim("/World/Light", "DistantLight", attributes={"inputs:intensity": 1500.0})

# 4. 机器人导入逻辑 (严格适配 4.x 底层接口)
# 推荐使用 Franka，因为它的模型更完整，看起来更明显
urdf_path = "/home/zgx/omnibot_project/isaacsim/source/extensions/isaacsim.asset.importer.urdf/data/urdf/robots/franka_description/robots/panda_arm_hand.urdf"

# --- 关键：拆分路径和文件名 ---
asset_root = os.path.dirname(urdf_path)
asset_name = os.path.basename(urdf_path)

# 获取接口
urdf_interface = _urdf.acquire_urdf_interface()
import_config = _urdf.ImportConfig()
import_config.merge_fixed_joints = False
import_config.fix_base = True 
import_config.make_default_prim = True

print(f"--- 正在解析: {asset_name} 从目录: {asset_root} ---")

# 4.x 精确参数顺序: (路径, 文件名, 配置)
robot_obj = urdf_interface.parse_urdf(asset_root, asset_name, import_config)

print(f"--- 正在载入物理舞台... ---")
# 4.x 精确参数顺序: (路径, 机器人名, 对象, 配置)
urdf_interface.import_robot(asset_root, "Robot", robot_obj, import_config)

# 5. 设置“上帝视角”摄像头 (不再盯着地板)
# eye: 摄像头位置, target: 盯着哪看
set_camera_view(eye=[2.5, 2.5, 2.5], target=[0, 0, 0.5])

# 6. 仿真运行
world.play()
print("🎉 物理世界已开启！如果还是黑屏，请点击 3D 窗口按 'F' 键聚焦机器人。")

try:
    while kit.is_running():
        world.step(render=True)
except KeyboardInterrupt:
    pass

world.stop()
kit.close()