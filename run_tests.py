import json
from main import parse_tool_call, execute_tool

# 模拟大模型回复的映射（根据用户输入）
mock_reply_map = {
    "现在几点": "[TOOL: get_current_time]",
    "掷个骰子": "[TOOL: roll_dice]",
    "帮我算一下48*6": "[TOOL: calculate] 48*6"
}

def load_test_cases(filepath="test_questions.json"):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_test(case):
    user_input = case["input"]
    expected = case["expected"]

    # 获取模拟的大模型回复
    mock_reply = mock_reply_map.get(user_input)
    if not mock_reply:
        return "FAIL (无模拟回复)"

    # 1. 解析工具调用
    tool_name, param = parse_tool_call(mock_reply)
    if tool_name is None:
        return "FAIL (解析失败)"

    # 2. 执行工具
    result = execute_tool(tool_name, param)
    if result is None:
        return "FAIL (执行失败)"

    # 3. 验证
    if expected == "工具调用":
        return "PASS"
    else:
        return "FAIL (未知期望)"

def main():
    cases = load_test_cases()
    results = []

    for case in cases:
        status = run_test(case)
        results.append({
            "input": case["input"],
            "expected": case["expected"],
            "status": status
        })

    for r in results:
        print(f"{r['input']} -> {r['status']}")

    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")

if __name__ == "__main__":
    main()