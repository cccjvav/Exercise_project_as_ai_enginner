"""默认 dry-run 不发送数据；真实调用须由使用者确认免费权益并安全配置环境。"""
import argparse
import json
from evidencedesk.agnes import answer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", default="Webhook 重试多少次？")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--confirmed-current-free", action="store_true")
    args = parser.parse_args()
    try:
        result = answer(args.question, live=args.live, confirmed_current_free=args.confirmed_current_free)
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, str(exc) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
