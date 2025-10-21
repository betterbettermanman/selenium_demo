import time

import dashscope

# 设置 API Key
dashscope.api_key = "sk-b1fc73875d134f34b0f2d579b9291281"

messages = [
    {'role': 'system', 'content': '你是一个知识丰富的助手，请根据问题给出准确、简洁的回答。如果是选择题，请在最后明确写出答案选项,并只返回选项字母（如：C）'},
    {'role': 'user',
     'content': '在写论文方面，深度学习的应用包括（）。\nA. 循环神经网络\nB. 长短期记忆网络\nC. 变换器\nD. 主成分分析'}
]

time_start = time.time()
response = dashscope.Generation.call(
    model="qwen3-8b",
    messages=messages,
    enable_thinking=False,
    result_format='text'
)

print("响应内容:", response.output.text)
print("耗时:", time.time() - time_start, "秒")
