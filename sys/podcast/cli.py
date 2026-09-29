"""Command line entry point: run with `python3 -m podcast.cli` from sys/."""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
from typing import Any

from .coordinator import Coordinator, EpisodeError, SYS_ROOT


def _print(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _load_json(path: str) -> Any:
    return json.loads(Path(path).expanduser().read_text(encoding="utf-8"))


def _load_handlers(spec: str, coordinator: Coordinator, episode_id: str) -> dict[str, Any]:
    """Load `module:function`; factory returns handler map for run_episode()."""
    module_name, separator, function_name = spec.partition(":")
    if not separator or not module_name or not function_name:
        raise EpisodeError("Backend cần dạng module:function.")
    function = getattr(importlib.import_module(module_name), function_name)
    handlers = function(coordinator, episode_id)
    if not isinstance(handlers, dict):
        raise EpisodeError("Backend factory phải trả về dict tên-handler → hàm.")
    return handlers


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Điều phối podcast dài 20–30 phút theo bốn phần và các subchunk.")
    parser.add_argument("--sys-root", default=str(SYS_ROOT),
                        help="Thư mục sys của dự án (mặc định là sys hiện tại).")
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create", help="Tự chọn chủ đề, tạo và chạy podcast ngủ.")
    create.add_argument("--auto", action="store_true", required=True)
    create.add_argument("--request-id", required=True, help="ID ổn định của yêu cầu; giữ nguyên khi tiếp tục.")
    create.add_argument("--topic")
    create.add_argument("--minutes", type=float, default=25)
    create.add_argument("--backend", default="podcast.backend:handlers")
    create.add_argument("--prepare-only", action="store_true", help="Chuẩn bị episode, chưa gọi dịch vụ tạo media.")

    commands.add_parser("doctor", help="Kiểm tra dịch vụ trước khi tạo podcast.")

    new = commands.add_parser("new", help="Tạo episode từ chủ đề hoặc brief JSON.")
    new.add_argument("--id", dest="episode_id")
    source = new.add_mutually_exclusive_group(required=True)
    source.add_argument("--topic")
    source.add_argument("--brief", help="Đường dẫn brief JSON.")

    for name in ("status", "resume"):
        command = commands.add_parser(name, help="Xem trạng thái hoặc tiếp tục episode.")
        command.add_argument("episode_id")
        if name == "resume":
            command.add_argument("--backend", default="podcast.backend:handlers", help="Factory module:function trả về các handler.")
            command.add_argument("--retry-failed", action="store_true",
                                 help="Cho phép thử lại stage/chunk đã lỗi (tối đa 3 lần tổng).")

    read = commands.add_parser("read", help="Đọc manifest, brief, script hoặc nhật ký.")
    read.add_argument("episode_id")
    read.add_argument("kind", choices=("manifest", "brief", "script", "events"),
                      nargs="?", default="manifest")
    read.add_argument("--part", choices=("P01", "P02", "P03", "P04"),
                      help="Chỉ đọc một phần của script.")

    script = commands.add_parser("set-script", help="Lưu revision kịch bản JSON có bốn phần.")
    script.add_argument("episode_id")
    script.add_argument("--file", required=True, help="JSON writer output.")

    run = commands.add_parser("run", help="Chạy các handler đã đăng ký, có thể tiếp tục episode.")
    run.add_argument("episode_id")
    run.add_argument("--backend", default="podcast.backend:handlers",
                      help="Factory module:function trả về các handler.")
    run.add_argument("--retry-failed", action="store_true")

    commands.add_parser("list", help="Liệt kê episode trong ledger.")

    next_topics = commands.add_parser("next", help="Hiện chủ đề catalog chưa giữ hoặc hoàn tất.")
    next_topics.add_argument("--count", type=int, default=5)

    show_topic = commands.add_parser("show", help="Hiện chủ đề, reservation và episode liên quan.")
    show_topic.add_argument("topic_id")

    reserve = commands.add_parser("reserve", help="Giữ một chủ đề catalog cho episode ID.")
    reserve.add_argument("topic_id")
    reserve.add_argument("episode_id")

    start = commands.add_parser("start", help="Tạo episode từ reservation đang giữ.")
    start.add_argument("episode_id")

    mark = commands.add_parser("mark", help="Đánh dấu topic done sau khi episode complete.")
    mark.add_argument("episode_id")

    release = commands.add_parser("release", help="Giải phóng reservation, giữ nguyên lịch sử episode.")
    release.add_argument("episode_id")
    release.add_argument("--note", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    coordinator = Coordinator(args.sys_root)
    try:
        if args.command == "doctor":
            from .preflight import check_environment
            _print(check_environment(coordinator.sys_root))
        elif args.command == "create":
            from .request import prepare_request
            manifest = prepare_request(coordinator, args.request_id, args.topic, args.minutes)
            episode_id = manifest["episode_id"]
            if args.prepare_only:
                _print(coordinator.status(episode_id))
            else:
                handlers = _load_handlers(args.backend, coordinator, episode_id)
                _print(coordinator.run_episode(episode_id, handlers))
        elif args.command == "new":
            brief = _load_json(args.brief) if args.brief else None
            _print(coordinator.create_episode(args.topic, brief, args.episode_id))
        elif args.command == "status":
            _print(coordinator.status(args.episode_id))
        elif args.command == "resume":
            if args.backend:
                handlers = _load_handlers(args.backend, coordinator, args.episode_id)
                _print(coordinator.resume(args.episode_id, handlers,
                                          retry_failed=args.retry_failed))
            else:
                _print(coordinator.resume(args.episode_id))
        elif args.command == "read":
            value = coordinator.read(args.episode_id, args.kind)
            if args.part:
                if args.kind != "script":
                    raise EpisodeError("--part chỉ dùng cùng read script.")
                value = next((part for part in value["parts"] if part["id"] == args.part), None)
                if value is None:
                    raise EpisodeError(f"Không tìm thấy {args.part} trong script hiện tại.")
            _print(value)
        elif args.command == "set-script":
            _print(coordinator.set_script(args.episode_id, _load_json(args.file)))
        elif args.command == "run":
            handlers = _load_handlers(args.backend, coordinator, args.episode_id)
            _print(coordinator.run_episode(args.episode_id, handlers,
                                           retry_failed=args.retry_failed))
        elif args.command == "list":
            _print(coordinator.list_episodes())
        elif args.command == "next":
            _print(coordinator.next_topics(args.count))
        elif args.command == "show":
            _print(coordinator.show_topic(args.topic_id))
        elif args.command == "reserve":
            _print(coordinator.reserve_topic(args.topic_id, args.episode_id))
        elif args.command == "start":
            _print(coordinator.start_reserved(args.episode_id))
        elif args.command == "mark":
            _print(coordinator.mark_done(args.episode_id))
        elif args.command == "release":
            _print(coordinator.release_reservation(args.episode_id, args.note))
        return 0
    except (EpisodeError, OSError, ValueError, KeyError, ImportError, AttributeError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
