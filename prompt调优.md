# prompt基础

## 核心组成：

- 角色：设定背景和能力（如旅游助手）
    
- 场景要求：明确需求目标
    
- 任务：可执行清单
    
- 示例：成功/失败案例+格式模板
    
- 约束：红线+偏好+风险规避
    

# prompt调用

## zero-shot

## few-shot

## CoT(chain of thought)

Zero-Shot-CoT 不添加示例而仅仅在指令中添加一行经典的“Let's think step by step”，就可以“唤醒”大模型的推理能力。而 Few-Shot-Cot 则在示例中详细描述了“解题步骤”，让大模型照猫画虎得到推理能力

## self-consisstency(自洽性)

多次调用大模型（奇次），然后使用大模型进行投票

## ToT(Tree of thought)
