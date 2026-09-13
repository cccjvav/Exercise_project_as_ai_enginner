#: 显式上传有限字段，默认不启用自动追踪，不上传原始问题或证据。
import os
from uuid import uuid4
from langsmith import Client

#: 必须先设置账号、项目和密钥；这里只演示遥测写入，不能当真实业务指标。
def main():
    os.environ["LANGSMITH_API_KEY"]
    project = os.environ["LANGSMITH_PROJECT"]
    client = Client()
    run_id = uuid4()
    client.create_run(name="course-synthetic-metric", run_type="chain", id=run_id,
                      inputs={"fixture": True}, project_name=project)
    client.update_run(run_id, outputs={"candidate_count": 1, "model_calls": 0, "synthetic": True})
    print("已上传明确标注 synthetic 的课程遥测；请在项目中检查并按保留策略删除。")

if __name__ == "__main__":
    main()
