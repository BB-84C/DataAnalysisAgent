import time
from concurrent.futures import ThreadPoolExecutor, Future

# 初始化全局 Future 注册表，模拟 MR 状态
future_map = {
    "data_A": Future(),
    "data_B": Future(),
    "data_C": Future(),
}

# 模拟第一个任务：生成 data_A
def task_A():
    print("Task A: Working...")
    time.sleep(1)  # 模拟执行时间
    result = "Result from A"
    future_map["data_A"].set_result(result)
    print("Task A: Done and set data_A.")

# 依赖 data_A，生成 data_B
def task_B():
    print("Task B: Waiting for data_A...")
    data_A = future_map["data_A"].result()  # 阻塞等待
    print(f"Task B: Got data_A = {data_A}")
    time.sleep(1)
    result = f"Result from B using ({data_A})"
    future_map["data_B"].set_result(result)
    print("Task B: Done and set data_B.")

# 依赖 data_B，生成 data_C
def task_C():
    print("Task C: Waiting for data_B...")
    data_B = future_map["data_B"].result()  # 阻塞等待
    print(f"Task C: Got data_B = {data_B}")
    time.sleep(1)
    result = f"Final result from C using ({data_B})"
    future_map["data_C"].set_result(result)
    print("Task C: Done and set data_C.")

#  主函数：用 ThreadPoolExecutor 提交任务
def main():
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(task_C)  # 提前提交，内部会阻塞等待 data_B
        executor.submit(task_B)  # 会等待 data_A
        executor.submit(task_A)  # 会最先执行

        # 主线程等待最终输出
        final_result = future_map["data_C"].result()
        print(f"\n Final Output: {final_result}")

if __name__ == "__main__":
    main()


